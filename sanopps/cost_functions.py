import pandas as pd
import copy

def add_capital_cost(arrays, i, st_state):
    """Calculate capital costs for infrastructure investments
    
    Inputs:
    arrays: state variables at each indexed year
    i: index of investment year
    st_state: current input variable state
    
    Returns:
    Dictionary of capital costs by component
    """

    urban_households_without_fhtc = st_state.urban_households - st_state.urban_households_with_fhtp
    additional_ct = max(
        (arrays['slum_pop'][i] / st_state.persons_per_wc) - st_state.comm_toilets * st_state.wc_per_ct, 
        0
        ) 
    additional_pt = max(
        (arrays['floating_pop'][i] / st_state.persons_per_pt) - st_state.public_toilets * st_state.wc_per_ct,
        0
        )
    
    return {
        'Tap Water Supply': urban_households_without_fhtc * st_state.fhtc_cost,
        'Community Toilets': additional_ct * st_state.comm_toilet_cost,
        'Public Toilets': additional_pt * st_state.public_toilet_cost,
        'Sewer Network (CapEx + OpEx)': st_state.gap_sewer_network_km * st_state.sewer_const_cost,
        'Sewage Treatment (CapEx + OpEx)': st_state.sewer_fraction * st_state.gap_treatment_capacity * st_state.stp_cost,
        'Fecal Sludge Treatment Plant': (arrays['septage_treated_per_day'][i] * st_state.fstp_cost) / 1000,
        'Training Officials': 0,
        'Public Awareness': 0
    }


def add_annual_operating_cost(i, arrays, st_state, current_year):
    """Calculate operating costs based on construction completion"""
    years_since_investment = current_year - st_state.investment_year
    
    # initialize variables
    training_officials, public_awareness, sewer, sewage_treatment_plant, fecal_sludge_treatment_plant = 0, 0, 0, 0, 0
    
    # training starts immediately after investment
    if years_since_investment >= 0:
        training_officials = (st_state.percent_ulb_officials_trained / 100) * arrays['urban_pop'][i] * st_state.training_cost
        public_awareness = arrays['urban_pop'][i] * st_state.awareness_cost

    # infrastructure operating costs for sewer and STP start after construction completed
    if years_since_investment >= st_state.construction_time_small:
        pass # for now, assuming no opex for CTs and PTs since it's covered by user fees
    
    if years_since_investment >= st_state.construction_time_large:
        sewer = st_state.gap_sewer_network_km * st_state.sewer_maint_cost
        sewage_treatment_plant = st_state.gap_treatment_capacity * st_state.stp_maint_cost

        # Septage treatment decision logic based on the decision matrix
        if st_state.co_treat_avail == "YES":

            current_sewage_load = (st_state.urban_pop_with_sewer_percent/100) * arrays['urban_pop'][i] * st_state.water_consumption / 1000000

            if st_state.gap_treatment_capacity < (st_state.stp_capacity - current_sewage_load):
                fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.cost_co_treatment / 1000
            
            elif st_state.fstp_avail == "YES" and st_state.fstp_capacity >= arrays['septage_treated_per_day'][i]: # FSTP available with capacity
                fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost / 1000

            else: # Default to FSTP cost if no other option available
                fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost / 1000

        elif st_state.co_treat_avail == "NO" and st_state.co_treat_proposed == "YES":
            # If town is proposing co-treatment at STP but it's not currently available
            # Capital cost is handled elsewhere, no additional maintenance cost
            fecal_sludge_treatment_plant = 0
        else:
            # If no co-treatment at STP and no FSTP, still need to handle septage
            # Default to FSTP maintenance cost
            fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost / 1000

    return {
        'Training Officials': training_officials,
        'Public Awareness': public_awareness,
        'Sewer Network (CapEx + OpEx)': sewer,
        'Sewage Treatment (CapEx + OpEx)': sewage_treatment_plant,
        'Fecal Sludge Treatment Plant': fecal_sludge_treatment_plant
    }

def add_annual_benefits(i, arrays, st_state, current_year):
    """Calculate annual benefits based on construction completion with smooth ramping"""
    years_since_investment = current_year - st_state.investment_year
    
    # Initialize benefits
    reduced_healthcare_costs, productivity_from_healthcare, water_collection_time_saved = 0, 0, 0
    sanitation_time_saved, recycled_water, tourism = 0, 0, 0

    # Common values
    decreased_incidences = st_state.disease_incidence * st_state.disease_decrease_percent / 100
    working_age_ratio = st_state.working_age_pop_percent / 100
    
    # Calculate ramp factor for smooth transition between small and large infrastructure completion
    # Factor is 0 before small construction time, 1 after large construction time, and linear in between
    ramp_factor = 0
    if years_since_investment >= st_state.construction_time_small:
        if years_since_investment >= st_state.construction_time_large:
            ramp_factor = 1.0
        else:
            # Linear interpolation between small and large construction times
            ramp_factor = (years_since_investment - st_state.construction_time_small) / (
                st_state.construction_time_large - st_state.construction_time_small)
    
    # Apply benefits with ramping factor if past small construction time
    if years_since_investment >= st_state.construction_time_small:
        # Health-related benefits
        reduced_healthcare_costs = decreased_incidences * (st_state.cost_per_visit + st_state.commute_cost_doctor)

        productivity_benefits_working = st_state.hourly_monetary_income * working_age_ratio * st_state.days_per_incidence * 8 * 0.6 * decreased_incidences
        productivity_benefits_nonworking = st_state.hourly_monetary_income * (1 - working_age_ratio) * st_state.days_per_incidence * 8 * 0.15 * decreased_incidences
        productivity_from_healthcare = productivity_benefits_working + productivity_benefits_nonworking

        # Recycled water benefits
        reuse_rate = st_state.wastewater_reuse_percent / 100

        new_sewer_connections = max(st_state.final_pop_connected_sewer_percent - 
                                st_state.urban_pop_with_sewer_in_investment_year_percent, 0) / 100
        
        annual_recycled_volume = (reuse_rate * new_sewer_connections * arrays['urban_pop'][i] * 365 * 1000)
        
        recycled_water = annual_recycled_volume * st_state.recycled_water_value
        
        # Time Saved Benefits
        time_saved_sanitation_working = st_state.hourly_monetary_income * working_age_ratio * 0.6 * (
            st_state.sanitation_access_saved * arrays['urban_pop'][i]
        )
        time_saved_sanitation_nonworking = st_state.hourly_monetary_income * (1 - working_age_ratio) * 0.15 * (
            st_state.sanitation_access_saved * arrays['urban_pop'][i]
        )
        time_saved_water_working = st_state.hourly_monetary_income * working_age_ratio * 0.6 * (
            st_state.water_access_saved * arrays['urban_households'][i]
        )
        time_saved_water_nonworking = st_state.hourly_monetary_income * (1 - working_age_ratio) * 0.15 * (
            st_state.water_access_saved * arrays['urban_households'][i]
        )

        water_collection_time_saved = time_saved_water_working + time_saved_water_nonworking
        sanitation_time_saved = time_saved_sanitation_working + time_saved_sanitation_nonworking

        # Tourism benefits (ramp up smoothly from small to large construction time)
        tourism = ramp_factor * (st_state.tourism_contribution_percent / 100 * 
                                st_state.increase_gdp_tourism_percent / 100 * 
                                st_state.gdp_per_capita * arrays['urban_pop'][i])
    
    return {
        'Reduced Healtcare Costs': reduced_healthcare_costs,
        'Productivity from Healthcare': productivity_from_healthcare,
        'Water Collection Time Saved': water_collection_time_saved,
        'Sanitation Time Saved': sanitation_time_saved,
        'Recycled Water': recycled_water,
        'Tourism': tourism
    }

def run_calculations(st_state):
    """
    Run all calculations for the sanitation opportunity cost-benefit analysis
    
    Inputs:
    st_state: session state containing all input variables
    
    Returns:
    results_df: DataFrame with year-by-year results
    state_snapshots: List of state dictionaries for each year
    """
    # Code that would replace the code in sanopps_app.py after else:
    """
    else:
        # RUN CALCULATIONS
        results_df, state_snapshots = run_calculations(st.session_state)
        st.session_state.results_df = results_df
        st.session_state.state_snapshots = state_snapshots
        st.session_state.calculations_done = True

        # Switch to Dashboard tab
        script_placeholder = st.empty()
        components.html(f"<script>{switch_tab(2)}</script>", height=0)
        time.sleep(0.2)
        script_placeholder.empty()
    """
    
    years = list(range(st_state.current_year, 2061))
    results_data = []
    state_snapshots = []
    
    # Calculate derived values in session state
    st_state.hourly_monetary_income = st_state.gdp_per_capita/(8*5*52)
    st_state.slum_pop_percent_in_investment_year = max(
        st_state.slum_pop_percent-st_state.slum_pop_percent_decrease,
        0)
    # st_state.household_size = st_state.urban_pop / st_state.urban_households
    st_state.sewer_fraction = st_state.sewer_vs_fstp_percent / 100
    st_state.fstp_fraction = 1 - st_state.sewer_fraction
    
    # Create arrays for year-by-year calculations
    n_years = [(year - st_state.current_year) / 10 for year in years]
    arrays = {}
    
    # Population arrays
    for key in ['urban_pop', 'urban_households']:
        arrays[key] = [st_state[key] * (1 + st_state.growth_rate/100) ** n for n in n_years]
    
    arrays['slum_pop'] = [(st_state.slum_pop_percent_in_investment_year / 100) * pop for pop in arrays['urban_pop']]
    arrays['floating_pop'] = [(st_state.floating_pop_percent / 100) * pop for pop in arrays['urban_pop']]
    
    # FSTP calculations
    arrays['households_septic_tanks'] = [households * (1 - st_state.urban_pop_with_sewer_percent/100) * st_state.fstp_fraction for households in arrays['urban_households']]
    arrays['septage_treated_per_day'] = [(households * st_state.septage_emptied_per_household) / (st_state.desludging_freq * 300) for households in arrays['households_septic_tanks']]

    # Initialize component dictionaries
    cost_components = dict.fromkeys([
        'Tap Water Supply', 'Community Toilets', 'Public Toilets',
        'Sewer Network (CapEx + OpEx)', 'Sewage Treatment (CapEx + OpEx)', 'Fecal Sludge Treatment Plant',
        'Training Officials', 'Public Awareness'
    ], 0)
    
    benefit_components = dict.fromkeys([
        'Reduced Healtcare Costs', 'Productivity from Healthcare',
        'Water Collection Time Saved', 'Sanitation Time Saved',
        'Recycled Water', 'Tourism'
    ], 0)

    cumulative_benefit_components = copy.deepcopy(benefit_components)
    cumulative_benefit_components['Total'] = 0

    # Loop through years for cost-benefit calculations
    for i, year in enumerate(years):
        inflation_factor = (1 + st_state.inflation/100) ** (year - st_state.current_year)
        discount_factor = 1 / ((1 + st_state.discount_rate/100) ** (year - st_state.current_year))
        overall_factor = inflation_factor * discount_factor

        # Add capital costs only in investment year
        if year == st_state.investment_year:
            # Determine sewer length per person based on population
            if arrays['urban_pop'][i] <= 20000:
                sewer_length_per_person = st_state.sewer_length_small
            elif arrays['urban_pop'][i] <= 100000:
                sewer_length_per_person = st_state.sewer_length_medium
            else:
                sewer_length_per_person = st_state.sewer_length_large

            # Calculate sewer network and treatment capacity needs
            st_state.additional_pop_connected_sewer = arrays['urban_pop'][i] * st_state.sewer_fraction * (1 - st_state.urban_pop_with_sewer_in_investment_year_percent / 100)
            st_state.final_pop_connected_sewer_percent = (st_state.additional_pop_connected_sewer + st_state.urban_pop_with_sewer_percent/100 * st_state.urban_pop) / st_state.urban_pop
            st_state.gap_sewer_network_km = max(0, (st_state.additional_pop_connected_sewer * sewer_length_per_person) / 1000)
            
            new_sewage_treatment_vol = st_state.additional_pop_connected_sewer * st_state.water_consumption / 1000000
            existing_sewage_treatment_vol = ((st_state.urban_pop_with_sewer_percent/100) * st_state.urban_pop) * st_state.water_consumption / 1000000
            total_sewage_treatment_vol = new_sewage_treatment_vol + existing_sewage_treatment_vol
            st_state.gap_treatment_capacity = max(0, total_sewage_treatment_vol - st_state.stp_capacity)
            
            cost_components = add_capital_cost(arrays, i, st_state)
            cumulative_cost_components = {key: cost_components[key] for key in cost_components}
            cumulative_cost_components['Total'] = sum(cost_components.values()) * overall_factor

        # Add operating costs and benefits after investment year
        elif year > st_state.investment_year:
            cost_components = add_annual_operating_cost(i, arrays, st_state, year)
            benefit_components = add_annual_benefits(i, arrays, st_state, year)

            for key in cost_components:
                if key in cumulative_cost_components:
                    cumulative_cost_components[key] += cost_components[key] * overall_factor
                else:
                    print(f"Warning: Cost component key '{key}' not found in cumulative_cost_components")
            for key in benefit_components:
                if key in cumulative_benefit_components:
                    cumulative_benefit_components[key] += benefit_components[key] * overall_factor
                else:
                    print(f"Warning: Benefit component key '{key}' not found in cumulative_benefit_components")

            cumulative_cost_components['Total'] += sum(cost_components.values()) * overall_factor
            cumulative_benefit_components['Total'] += sum(benefit_components.values()) * overall_factor

            benefit_to_cost_ratio = cumulative_benefit_components['Total'] / cumulative_cost_components['Total'] if cumulative_cost_components['Total'] != 0 else 0

            state_snapshots.append({
                'year': year,
                'benefit_to_cost_ratio': benefit_to_cost_ratio,
                'cumulative_benefit_components': cumulative_benefit_components,
                'cumulative_cost_components': cumulative_cost_components
                })
        
        else:
            cumulative_cost_components = {key: 0 for key in cost_components}
            cumulative_cost_components['Total'] = 0
            cumulative_benefit_components = {key: 0 for key in benefit_components}
            cumulative_benefit_components['Total'] = 0
            benefit_to_cost_ratio = 0

        present_value_total_benefits = sum(benefit_components.values()) * overall_factor
        present_value_total_cost = sum(cost_components.values()) * overall_factor

        # Store results
        results_data.append({
            "Year": year,
            "Benefits_Per_Person": present_value_total_benefits / st_state.urban_pop,
            "Costs_Per_Person": present_value_total_cost / st_state.urban_pop,
            "Total_Benefit": present_value_total_benefits,
            "Total_Costs": present_value_total_cost,
            "Cumulative_Total_Benefit": cumulative_benefit_components['Total'],
            "Cumulative_Total_Cost": cumulative_cost_components['Total'],
            "Cumulative_Benefits_Per_Person": cumulative_benefit_components['Total'] / arrays['urban_pop'][0] if cumulative_benefit_components['Total'] > 0 else 0,
            "Cumulative_Costs_Per_Person": cumulative_cost_components['Total'] / arrays['urban_pop'][0] if cumulative_cost_components['Total'] > 0 else 0,
            "Benefit_to_Cost_Ratio": benefit_to_cost_ratio
        })

    # Return results
    return pd.DataFrame(results_data), state_snapshots