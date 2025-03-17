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
    additional_ct = max((arrays['slum_pop'][i] / st_state.persons_per_wc) - st_state.comm_toilets * st_state.wc_per_ct, 0) 
    additional_pt = max((arrays['floating_pop'][i] / st_state.persons_per_pt) - st_state.public_toilets * st_state.wc_per_ct, 0)
    
    return {
        'Tap Water Supply': urban_households_without_fhtc * st_state.fhtc_cost,
        'Community Toilets': additional_ct * st_state.comm_toilet_cost,
        'Public Toilets': additional_pt * st_state.public_toilet_cost,
        'Sewer': st_state.gap_sewer_network_km * st_state.sewer_const_cost,
        'Sewage Treatment Plant': st_state.sewer_fraction * st_state.gap_treatment_capacity * st_state.stp_cost,
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
        pass # for now, assuming no opex for CTs and PTs
    if years_since_investment >= st_state.construction_time_large:
        sewer = st_state.gap_sewer_network_km * st_state.sewer_maint_cost
        sewage_treatment_plant = st_state.gap_treatment_capacity * st_state.stp_maint_cost

        if st_state.co_treat_avail == "YES":

            current_sewage_load = (st_state.urban_pop_with_sewer_percent/100) * arrays['urban_pop'][i] * st_state.water_consumption / 1000000

            if st_state.gap_treatment_capacity < (st_state.stp_capacity - current_sewage_load):
                fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.cost_co_treatment / 1000
            
            elif st_state.fstp_avail == "YES" and st_state.fstp_capacity >= arrays['septage_treated_per_day'][i]: # FSTP available with capacity
                fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost / 1000

            else: # Default to FSTP cost if no other option available
                fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost / 1000

        elif st_state.fstp_avail == "YES" and st_state.fstp_capacity >= arrays['septage_treated_per_day'][i]:
            # FSTP is available and has capacity
            fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost / 1000
        else:
            # Default to FSTP cost if no other option available
            fecal_sludge_treatment_plant = arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost / 1000

    return {
        'Training Officials': training_officials,
        'Public Awareness': public_awareness,
        'Sewer': sewer,
        'Sewage Treatment Plant': sewage_treatment_plant,
        'Fecal Sludge Treatment Plant': fecal_sludge_treatment_plant
    }
def add_annual_benefits(i, arrays, st_state, current_year):
    """Calculate annual benefits based on construction completion"""
    years_since_investment = current_year - st_state.investment_year
    
    # Initialize benefits
    reduced_healthcare_costs, productivity_from_healthcare, water_collection_time_saved = 0, 0, 0
    sanitation_time_saved, recycled_water, tourism = 0, 0, 0

    # Common values
    decreased_incidences = st_state.disease_incidence * st_state.disease_decrease_percent / 100
    working_age_ratio = st_state.working_age_pop_percent / 100
    
    # Small infrastructure benefits
    if years_since_investment >= st_state.construction_time_small:

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

    # Large infrastructure benefits
    if years_since_investment >= st_state.construction_time_large:  
        tourism = st_state.tourism_contribution_percent / 100 * st_state.increase_gdp_tourism_percent / 100 * st_state.gdp_per_capita * arrays['urban_pop'][i] / 100
        # print(st_state.tourism_contribution_percent)
        # print(st_state.increase_gdp_tourism_percent)
        # print(tourism)
        # print(tourism / arrays['urban_pop'][i])
    return {
        'Reduced Healtcare Costs': reduced_healthcare_costs,
        'Productivity from Healthcare': productivity_from_healthcare,
        'Water Collection Time Saved': water_collection_time_saved,
        'Sanitation Time Saved': sanitation_time_saved,
        'Recycled Water': recycled_water,
        'Tourism': tourism
    }