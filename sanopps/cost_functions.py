def add_capital_cost(year, arrays, i, st_state):
    """Calculate capital costs for investment year"""
    # Water supply capital costs
    capital_cost_piped_water = arrays['urban_households_without_fhtc'][i] * st_state.fhtc_cost
    
    # Toilet capital costs
    total_capital_cost_ct = arrays['additional_ct'][i] * st_state.capital_cost_wc
    total_capital_cost_pt = arrays['additional_pt'][i] * st_state.capital_cost_wc

    # Sewer and treatment capital costs
    if arrays['pop'][i] <= 20000:
        sewer_length_per_person = st_state.sewer_length_small
    elif arrays['pop'][i] <= 100000:
        sewer_length_per_person = st_state.sewer_length_medium
    else:
        sewer_length_per_person = st_state.sewer_length_large
        
    sewer_network = (arrays['pop_connected_sewer'][i] * sewer_length_per_person) / 1000
    gap_sewer_network = max(0, sewer_network - st_state.sewer_length)
    capital_cost_sewer_network = max(0, gap_sewer_network * st_state.sewer_const_cost)
    capital_cost_additional_stp = max(0, arrays['gap_treatment_capacity'][i] * st_state.stp_cost)
    
    # FSTP costs
    if st_state.co_treat_avail == "NO":
        cost_fstp_total = max(0, arrays['septage_treated_per_day'][i] * st_state.cost_fstp) / 1000
    else:
        cost_fstp_total = max(0, arrays['septage_treated_per_day'][i] * st_state.cost_co_treatment) / 1000

    # Training and awareness costs
    officials_capacity_building = (st_state.percent_ulb_officials_trained/100) * arrays['pop'][i]
    total_annual_cost_capacity_building = max(0, officials_capacity_building * st_state.training_cost)
    total_awareness_cost = max(0, arrays['pop'][i] * st_state.awareness_cost)

    return {
        'Tap Water Supply': capital_cost_piped_water,
        'Community Toilets': total_capital_cost_ct,
        'Public Toilets': total_capital_cost_pt,
        'Sewer': capital_cost_sewer_network,
        'Sewage Treatment Plant': capital_cost_additional_stp,
        'Fecal Sludge Treatment Plant': cost_fstp_total,
        'Training Officials': total_annual_cost_capacity_building,
        'Public Awareness': total_awareness_cost
    }


def add_operating_cost(i, arrays, st_state):
    """Calculate operating costs for post-construction years"""
    annual_maint_sewer_network_total = max(0, arrays['gap_sewer_network'][i] * st_state.sewer_maint_cost)
    annual_maint_stp_total = max(0, arrays['gap_treatment_capacity'][i] * st_state.stp_maint_cost)
    annual_maint_fstp_total = max(0, arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost) / 1000
    
    officials_capacity_building = (st_state.percent_ulb_officials_trained/100) * arrays['pop'][i]
    total_annual_cost_capacity_building = max(0, officials_capacity_building * st_state.training_cost)
    total_awareness_cost = max(0, arrays['pop'][i] * st_state.awareness_cost)

    return {
        'Sewer': annual_maint_sewer_network_total,
        'Sewage Treatment Plant': annual_maint_stp_total,
        'Fecal Sludge Treatment Plant': annual_maint_fstp_total,
        'Training Officials': total_annual_cost_capacity_building,
        'Public Awareness': total_awareness_cost
    }


def add_annual_benefit(i, arrays, st_state):
    """Calculate annual benefits"""
    # Health benefits
    health_benefits = st_state.disease_incidence * (st_state.cost_per_visit + st_state.commute_cost_doctor) * 0.6
    
    # Productivity benefits
    working_age_ratio = st_state.working_age_pop / 100
    productivity_benefits_working = st_state.hourly_monetary_income * working_age_ratio * 5 * 8 * arrays['pop'][i] * 0.6
    productivity_benefits_nonworking = st_state.hourly_monetary_income * (1 - working_age_ratio) * 5 * 8 * 0.15 * arrays['pop'][i]
    
    # Time saved benefits
    time_saved_sanitation_working = st_state.hourly_monetary_income * working_age_ratio * 0.6 * (
        st_state.sanitation_access_saved * arrays['pop'][i]
    )
    time_saved_sanitation_nonworking = st_state.hourly_monetary_income * (1 - working_age_ratio) * 0.15 * (
        st_state.sanitation_access_saved * arrays['pop'][i]
    )
    time_saved_water_working = st_state.hourly_monetary_income * working_age_ratio * 0.6 * (
        st_state.water_access_saved * arrays['urban_households'][i]
    )
    time_saved_water_nonworking = st_state.hourly_monetary_income * (1 - working_age_ratio) * 0.15 * (
        st_state.water_access_saved * arrays['urban_households'][i]
    )
    
    # Other benefits
    recycled_water_benefits = st_state.wastewater_reuse_pct/100 * arrays['sewage_generated'][i] * 365 * 1000 * st_state.recycled_water_value
    tourism_benefits = 0.091 * st_state.gdp_per_capita * arrays['pop'][i] * 0.1

    return {
        'Reduced Healtcare Costs': health_benefits,
        'Productivity from Healthcare': productivity_benefits_working + productivity_benefits_nonworking,
        'Time Saved from Water Collection': time_saved_water_working + time_saved_water_nonworking,
        'Time Saved from Sanitation Access': time_saved_sanitation_working + time_saved_sanitation_nonworking,
        'Recycled Water': recycled_water_benefits,
        'Tourism': tourism_benefits
    }