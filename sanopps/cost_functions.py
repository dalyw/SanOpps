import pandas as pd
import copy

def determine_treatment_approach(st_state, arrays, i):
    """Determine the appropriate treatment approach based on available infrastructure
    
    Inputs:
    st_state: current input variable state
    arrays: state variables at each indexed year
    i: index of current year
    
    Returns:
    Dictionary with treatment decisions, flow allocations, and capacity requirements
    """
    result = {
        'use_co_treatment': False,
        'use_fstp': False,
        'flow_to_co_treatment': 0,
        'flow_to_fstp': 0,
        'additional_fstp_capacity_needed': 0,
        'additional_co_treatment_capacity_needed': 0
    }
    
    daily_septage_flow = arrays['septage_treated_per_day'][i]
    
    # Check if co-treatment is available at existing STP
    if st_state.co_treat_avail == "YES":
        current_sewage_load = (st_state.urban_pop_with_sewer_percent/100) * arrays['urban_pop'][i] * st_state.water_consumption / 1000000
        
        if st_state.gap_treatment_capacity < (st_state.stp_capacity - current_sewage_load): # If there's enough capacity in the STP for co-treatment
            result['use_co_treatment'] = True
            result['flow_to_co_treatment'] = daily_septage_flow
        elif st_state.fstp_avail == "YES" and st_state.fstp_capacity >= daily_septage_flow:   # If co-treatment capacity is insufficient but FSTP is available
            result['use_fstp'] = True
            result['flow_to_fstp'] = daily_septage_flow
        else: # Use FSTP
            result['use_fstp'] = True
            result['flow_to_fstp'] = daily_septage_flow
            result['additional_fstp_capacity_needed'] = daily_septage_flow
    
    # If co-treatment is not available but is being proposed
    elif st_state.co_treat_avail == "NO" and st_state.co_treat_proposed == "YES":
        result['use_co_treatment'] = True
        result['flow_to_co_treatment'] = daily_septage_flow
        result['additional_co_treatment_capacity_needed'] = daily_septage_flow
    
    # If no co-treatment (available or proposed)
    else:
        result['use_fstp'] = True
        result['flow_to_fstp'] = daily_septage_flow
        
        if not (st_state.fstp_avail == "YES" and st_state.fstp_capacity >= daily_septage_flow): # Need to build FSTP
            result['additional_fstp_capacity_needed'] = daily_septage_flow
    
    return result

def add_capital_cost(arrays, i, st_state, treatment_decision):
    """Calculate capital costs for infrastructure investments
    
    Inputs:
    arrays: state variables at each indexed year
    i: index of investment year
    st_state: current input variable state
    treatment_decision: dictionary with treatment approach details
    
    Returns:
    Dictionary of capital costs by component
    """
    urban_households_without_fhtc = st_state.urban_households - st_state.urban_households_with_fhtp
    additional_ct = max((arrays['slum_pop'][i] / st_state.persons_per_wc) - st_state.comm_toilets * st_state.wc_per_ct, 0) 
    additional_pt = max((arrays['floating_pop'][i] / st_state.persons_per_pt) - st_state.public_toilets * st_state.wc_per_ct, 0)
    
    # Calculate capital costs for treatment
    fstp_capital_cost = treatment_decision['additional_fstp_capacity_needed'] * st_state.fstp_cost / 1000
    co_treatment_capital_cost = treatment_decision['additional_co_treatment_capacity_needed'] * st_state.cost_co_treatment / 1000
    
    return {
        'Tap Water Supply': urban_households_without_fhtc * st_state.fhtc_cost,
        'Community Toilets': additional_ct * st_state.comm_toilet_cost,
        'Public Toilets': additional_pt * st_state.public_toilet_cost,
        'Sewer Network (CapEx + OpEx)': st_state.gap_sewer_network_km * st_state.sewer_const_cost,
        'Sewage Treatment (CapEx + OpEx)': st_state.sewer_fraction * st_state.gap_treatment_capacity * st_state.stp_cost,
        'Fecal Sludge Treatment Plant': fstp_capital_cost + co_treatment_capital_cost,
        'Training Officials': 0,
        'Public Awareness': 0
    }

def add_annual_operating_cost(i, arrays, st_state, years_since_investment, treatment_decision):
    """Calculate operating costs based on construction completion"""    
    training_officials = public_awareness = sewer = stp_maintenance = fstp_maintenance = 0
    
    if years_since_investment >= 0: # training starts immediately
        training_officials = (st_state.percent_ulb_officials_trained / 100) * arrays['urban_pop'][i] * st_state.training_cost
        public_awareness = arrays['urban_pop'][i] * st_state.awareness_cost
    
    if years_since_investment >= st_state.construction_time_large: # sewer opex starts after construction completed
        sewer = st_state.gap_sewer_network_km * st_state.sewer_maint_cost
        stp_maintenance = (st_state.gap_treatment_capacity + treatment_decision['flow_to_co_treatment']) * st_state.stp_maint_cost / 1000
        fstp_maintenance = treatment_decision['flow_to_fstp'] * st_state.fstp_maint_cost / 1000

    return {
        'Training Officials': training_officials,
        'Public Awareness': public_awareness,
        'Sewer Network (CapEx + OpEx)': sewer,
        'Sewage Treatment (CapEx + OpEx)': stp_maintenance,
        'Fecal Sludge Treatment Plant': fstp_maintenance
    }

def add_annual_benefits(i, arrays, st_state, years_since_investment):
    """Calculate annual benefits based on construction completion"""    
    reduced_healthcare_costs = reduced_healthcare_commute_costs = productivity_benefits_working = productivity_benefits_nonworking = water_collection_time_saved = 0
    sanitation_time_saved = recycled_water = tourism = 0
    hourly_income = st_state.hourly_monetary_income * (1 + st_state.inflation_rate/100) ** years_since_investment
    
    working_age_factor = 0.6
    nonworking_age_factor = 0.15
    working_hours_per_day = 8

    if years_since_investment >= st_state.construction_time_small:
        # Health-related benefits
        decreased_incidences = st_state.disease_incidence * st_state.disease_decrease_percent / 100
        working_age_ratio = st_state.working_age_pop_percent / 100
        reduced_healthcare_costs = decreased_incidences * st_state.cost_per_visit
        reduced_healthcare_commute_costs  = decreased_incidences * st_state.commute_cost_doctor
        productivity_benefits_working = hourly_income * working_age_ratio * st_state.days_per_incidence * working_hours_per_day * working_age_factor * decreased_incidences
        productivity_benefits_nonworking = hourly_income * (1 - working_age_ratio) * st_state.days_per_incidence * working_hours_per_day * nonworking_age_factor * decreased_incidences

        # Recycled water benefits
        new_sewer_connections = max(st_state.final_pop_connected_sewer_percent - 
                                st_state.urban_pop_with_sewer_in_investment_year_percent, 0) / 100
        recycled_water = st_state.wastewater_reuse_percent / 100 * new_sewer_connections * arrays['urban_pop'][i] * 365 * 1000 * st_state.recycled_water_value    
        
        # Water time saved
        prop_new_fhtc = max(100 - st_state.urban_households_with_fhtp_percent, 0) / 100
        time_saved_water_working = hourly_income * working_age_ratio * working_age_factor * st_state.water_access_saved * arrays['urban_households'][i] * prop_new_fhtc
        time_saved_water_nonworking = hourly_income * (1 - working_age_ratio) * nonworking_age_factor * st_state.water_access_saved * arrays['urban_households'][i] * prop_new_fhtc
        water_collection_time_saved = time_saved_water_working + time_saved_water_nonworking

        # Sanitation time saved
        affected_pop = (st_state.slum_pop_percent + st_state.floating_pop_percent) / 100
        time_saved_sanitation_working = hourly_income * working_age_ratio * working_age_factor * st_state.sanitation_access_saved * affected_pop
        time_saved_sanitation_nonworking = hourly_income * (1 - working_age_ratio) * nonworking_age_factor * st_state.sanitation_access_saved * affected_pop
        sanitation_time_saved = time_saved_sanitation_working + time_saved_sanitation_nonworking

        # Tourism Benefits
        # Adjust GDP per capita for inflation over time
        inflation_adjusted_gdp = st_state.gdp_per_capita * (1 + st_state.inflation_rate/100) ** years_since_investment
        tourism = (st_state.tourism_contribution_percent / 100 * st_state.increase_gdp_tourism_percent / 100 * inflation_adjusted_gdp * arrays['urban_pop'][i])

    return {
        'Healthcare Treatment Cost Savings': reduced_healthcare_costs,
        'Healthcare Commute Cost Savings': reduced_healthcare_commute_costs,
        'Productive Time Saved - Working Age': productivity_benefits_working,
        'Productive Time Saved - Nonworking Age': productivity_benefits_nonworking,
        'Water Collection Time Saved': water_collection_time_saved,
        'Access to Sanitation Time Saved': sanitation_time_saved,
        'Value of Recycled Water': recycled_water,
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
    arrays['households_septic_tanks'] = [households * (1 - st_state.urban_pop_with_sewer_percent/100) * st_state.fstp_fraction 
                                        for households in arrays['urban_households']]
    arrays['septage_treated_per_day'] = [(households * st_state.septage_emptied_per_household) / (st_state.desludging_freq * 300) 
                                        for households in arrays['households_septic_tanks']]

    # Initialize component dictionaries
    cost_keys = ['Tap Water Supply', 'Community Toilets', 'Public Toilets', 'Sewer Network (CapEx + OpEx)', 
                'Sewage Treatment (CapEx + OpEx)', 'Fecal Sludge Treatment Plant', 'Training Officials', 'Public Awareness']
    benefit_keys = ['Healthcare Treatment Cost Savings', 'Healthcare Commute Cost Savings', 'Productive Time Saved - Working Age', 
                   'Productive Time Saved - Nonworking Age', 'Water Collection Time Saved', 
                   'Access to Sanitation Time Saved', 'Value of Recycled Water', 'Tourism']
    
    cost_components = dict.fromkeys(cost_keys, 0)
    benefit_components = dict.fromkeys(benefit_keys, 0)
    cumulative_benefit_components = dict.fromkeys(benefit_keys + ['Total'], 0)
    cumulative_cost_components = dict.fromkeys(cost_keys + ['Total'], 0)

    # Calculate amortization factor if needed
    amortization_period = 20  # years
    treatment_decision = None
    annual_amortized_payments = {}
    
    # Loop through years for cost-benefit calculations
    for i, year in enumerate(years):
        inflation_factor = (1 + st_state.inflation/100) ** (year - st_state.current_year)
        discount_factor = 1 / ((1 + st_state.discount_rate/100) ** (year - st_state.current_year))
        overall_factor = inflation_factor * discount_factor        
        
        if year == st_state.investment_year: # Add capital costs only
            treatment_decision = determine_treatment_approach(st_state, arrays, i)

            # Calculate sewer network and treatment capacity needs
            st_state.additional_pop_connected_sewer = arrays['urban_pop'][i] * st_state.sewer_fraction * (1 - st_state.urban_pop_with_sewer_in_investment_year_percent / 100)
            st_state.final_pop_connected_sewer_percent = (st_state.additional_pop_connected_sewer + st_state.urban_pop_with_sewer_percent/100 * st_state.urban_pop) / st_state.urban_pop
            st_state.gap_sewer_network_km = max(0, (st_state.additional_pop_connected_sewer * st_state.sewer_length_per_person) / 1000)
            
            new_sewage_treatment_vol = st_state.additional_pop_connected_sewer * st_state.water_consumption / 1000000
            existing_sewage_treatment_vol = ((st_state.urban_pop_with_sewer_percent/100) * st_state.urban_pop) * st_state.water_consumption / 1000000
            st_state.gap_treatment_capacity = max(0, new_sewage_treatment_vol + existing_sewage_treatment_vol - st_state.stp_capacity)
            
            capital_costs = add_capital_cost(arrays, i, st_state, treatment_decision)
            
            if st_state.amortize_capex == 'YES':
                # Calculate annual payment for each capital cost component
                r = st_state.interest_rate / 100
                amortization_factor = r * (1 + r)**amortization_period / ((1 + r)**amortization_period - 1)
                
                for component, cost in capital_costs.items():
                    annual_amortized_payments[component] = cost * amortization_factor if cost > 0 else 0
                
                cost_components = annual_amortized_payments.copy()
            else:
                cost_components = capital_costs
            
            cumulative_cost_components = {key: cost_components.get(key, 0) for key in cost_keys}
            cumulative_cost_components['Total'] = sum(cost_components.values()) * overall_factor

        # Add operating costs and benefits after investment year
        elif year > st_state.investment_year:
            operating_costs = add_annual_operating_cost(i, arrays, st_state, year - st_state.investment_year, treatment_decision)
            benefit_components = add_annual_benefits(i, arrays, st_state, year - st_state.investment_year)
            
            # If amortizing and within amortization period, add annual payments
            if hasattr(st_state, 'amortize_capex') and st_state.amortize_capex and (year - st_state.investment_year) < amortization_period:
                cost_components = operating_costs.copy()
                # Add amortized capital costs to operating costs
                for component, annual_payment in annual_amortized_payments.items():
                    cost_components[component] = cost_components.get(component, 0) + annual_payment
            else:
                cost_components = operating_costs

            # Update cumulative components
            for key in cost_components:
                cumulative_cost_components[key] = cumulative_cost_components.get(key, 0) + cost_components[key] * overall_factor
            for key in benefit_components:
                cumulative_benefit_components[key] = cumulative_benefit_components.get(key, 0) + benefit_components[key] * overall_factor

            cumulative_cost_components['Total'] += sum(cost_components.values()) * overall_factor
            cumulative_benefit_components['Total'] += sum(benefit_components.values()) * overall_factor

        else: # Years before investment
            cumulative_cost_components = {key: 0 for key in cost_keys + ['Total']}
            cumulative_benefit_components = {key: 0 for key in benefit_keys + ['Total']}

        # Calculate benefit-to-cost ratio consistently for all years
        benefit_to_cost_ratio = (cumulative_benefit_components['Total'] / cumulative_cost_components['Total'] 
                                if cumulative_cost_components['Total'] > 0 else 0)

        # Add state snapshot for all years after investment
        if year >= st_state.investment_year:
            state_snapshots.append({
                'year': year,
                'benefit_to_cost_ratio': benefit_to_cost_ratio,
                'cumulative_benefit_components': copy.deepcopy(cumulative_benefit_components),
                'cumulative_cost_components': copy.deepcopy(cumulative_cost_components)
            })

        present_value_total_benefits = sum(benefit_components.values()) * overall_factor
        present_value_total_cost = sum(cost_components.values()) * overall_factor

        results_data.append({
            "Year": year,
            "Total_Benefit": present_value_total_benefits,
            "Total_Costs": present_value_total_cost,
            "Cumulative_Total_Benefit": cumulative_benefit_components['Total'],
            "Cumulative_Total_Cost": cumulative_cost_components['Total'],
            "Cumulative_Benefits_Per_Person": cumulative_benefit_components['Total'] / st_state.urban_pop if cumulative_benefit_components['Total'] > 0 else 0,
            "Cumulative_Costs_Per_Person": cumulative_cost_components['Total'] / st_state.urban_pop if cumulative_cost_components['Total'] > 0 else 0,
            "Benefit_to_Cost_Ratio": benefit_to_cost_ratio
        })

    return pd.DataFrame(results_data), state_snapshots