def add_capital_cost_small(arrays, i, st_state):
    """Calculate capital costs for small infrastructure:
     -- functional household tap connections
     -- toilets

     Inputs:
     arrays: state variables at each indexed year
     i: index of investmeng year
     st_state: current input variable state
     """

    # Water supply capital costs
    urban_households_without_fhtc = arrays['urban_households'][i] - st_state.urban_households_with_fhtp

    # Toilet capital costs
    #   addition ct based on slum pop in investment year
    additional_ct = max((arrays['slum_pop'][i] / st_state.persons_per_wc) - st_state.comm_toilets * st_state.wc_per_ct,0) 
    #   addition pt based on floating pop in investment year
    additional_pt = max((arrays['floating_pop'][i] / st_state.persons_per_pt) - st_state.public_toilets * st_state.wc_per_ct,0)

    return {
        'Tap Water Supply': urban_households_without_fhtc * st_state.fhtc_cost,
        'Community Toilets': additional_ct * st_state.comm_toilet_cost,
        'Public Toilets': additional_pt * st_state.public_toilet_cost,
    }

def add_capital_cost_large(arrays, i, st_state):
    """Calculate capital costs for large infrastructure
    -- sewer
    -- STP
    -- FSTP
    -- septic
    """
            
    capital_cost_fstp = (arrays['septage_treated_per_day'][i] * st_state.fstp_cost) / 1000

    return {
        'Sewer':  st_state.gap_sewer_network_km * st_state.sewer_const_cost,
        'Sewage Treatment Plant': st_state.gap_treatment_capacity * st_state.stp_cost,
        'Fecal Sludge Treatment Plant': capital_cost_fstp,
    }

def add_capital_cost(arrays, i, st_state):
    """Calculate total capital costs by combining small and large infrastructure costs"""
    small_costs = add_capital_cost_small(arrays, i, st_state)
    large_costs = add_capital_cost_large(arrays, i, st_state)
    
    total_costs = {}
    total_costs.update(small_costs)
    total_costs.update(large_costs)
    
    return total_costs

def add_operating_cost(i, arrays, st_state, current_year):
    """Calculate operating costs based on construction completion"""
    years_since_investment = current_year - st_state.investment_year
    
    # Initialize costs dictionary
    costs = {
        'Training Officials': 0,
        'Public Awareness': 0,
        'Sewer': 0,
        'Sewage Treatment Plant': 0,
        'Fecal Sludge Treatment Plant': 0
    }
    
    # training starts immediately after investment
    if years_since_investment >= 0:
        officials_capacity_building = (st_state.percent_ulb_officials_trained / 100) * arrays['urban_pop'][i]
        costs['Training Officials'] = max(0, officials_capacity_building * st_state.training_cost)
        costs['Public Awareness'] = arrays['urban_pop'][i] * st_state.awareness_cost

    # infrastructure operating costs for sewer and STP start after construction completed
    if years_since_investment >= st_state.construction_time_large:
        costs['Sewer'] = max(0,  st_state.gap_sewer_network_km * st_state.sewer_maint_cost)
        costs['Sewage Treatment Plant'] = max(0, st_state.gap_treatment_capacity * st_state.stp_maint_cost)
        
        # FSTP operating costs including co-treatment if available
        if st_state.co_treat_avail == "NO":
            costs['Fecal Sludge Treatment Plant'] = max(0, arrays['septage_treated_per_day'][i] * st_state.fstp_maint_cost) / 1000
        else:
            costs['Fecal Sludge Treatment Plant'] = max(0, arrays['septage_treated_per_day'][i] * st_state.cost_co_treatment) / 1000

    return costs

def add_annual_benefit(i, arrays, st_state, current_year):
    """Calculate annual benefits based on construction completion"""
    years_since_investment = current_year - st_state.investment_year
    
    # Initialize benefits dictionary
    benefits = {
        'Reduced Healtcare Costs': 0,
        'Productivity from Healthcare': 0,
        'Water Collection Time Saved': 0,
        'Sanitation Time Saved': 0,
        'Recycled Water': 0,
        'Tourism': 0
    }

    # Calculate common values
    decreased_incidences = st_state.disease_incidence * st_state.disease_decrease_percent / 100
    working_age_ratio = st_state.working_age_pop_percent / 100
    
    # Small infrastructure benefits
    if years_since_investment >= st_state.construction_time_small:

        benefits['Reduced Healtcare Costs'] = decreased_incidences * (st_state.cost_per_visit + st_state.commute_cost_doctor)

        productivity_benefits_working = st_state.hourly_monetary_income * working_age_ratio * st_state.days_per_incidence * 8 * 0.6 * decreased_incidences
        productivity_benefits_nonworking = st_state.hourly_monetary_income * (1 - working_age_ratio) * st_state.days_per_incidence * 8 * 0.15 * decreased_incidences
        benefits['Productivity from Healthcare'] = productivity_benefits_working + productivity_benefits_nonworking

        benefits['Recycled Water'] = max(
            st_state.wastewater_reuse_percent / 100 * (st_state.final_pop_connected_sewer_percent - st_state.urban_pop_with_sewer_in_investment_year_percent) / 100 * arrays['urban_pop'][i] * 365 * 1000 * st_state.recycled_water_value,
            0)
        
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

        benefits['Water Collection Time Saved'] = time_saved_water_working + time_saved_water_nonworking
        benefits['Sanitation Time Saved'] = time_saved_sanitation_working + time_saved_sanitation_nonworking

    # Large infrastructure benefits
    if years_since_investment >= st_state.construction_time_large:
        tourism_benefits = st_state.tourism_contribution_percent / 100 * st_state.gdp_per_capita * arrays['urban_pop'][i] * st_state.increase_gdp_tourism_percent / 100
        benefits['Tourism'] = tourism_benefits

    return benefits