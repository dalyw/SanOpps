import pandas as pd

# Load constants from CSV
constants = pd.read_csv("params.csv", index_col="Indicator")

# Extract constants
# population_current = constants.loc["Population(current)", "Value"]
year_current = constants.loc["Year(current)", "Value"]
rate_decadal_growth = constants.loc["Rate of decadal growth of population (in percentage)", "Value"]
target_year = constants.loc["Target Year (Date of commission of WASH interventions)", "Value"]
# slum_population_current = constants.loc["Slum Population (current)", "Value"]
# percentage_floating_population_current = constants.loc["Percentage of floating population (current)", "Value"]
fhtc_cost_per_household = constants.loc["FHTC cost per household", "Value"]
# urban_households_current = constants.loc["Number of Urban Households (Current)", "Value"]
# percentage_urban_households_tap_water = constants.loc["Percentage of Urban Households having tap water supply(current)", "Value"]
persons_per_wc_ct = constants.loc["Number of persons in slums per WC(CT)", "Value"]
wc_ct_current = constants.loc["Number of WC(CT) (current)", "Value"]
capital_cost_wc_ct = constants.loc["Capital cost of construction per WC(CT)", "Value"]
persons_per_wc_pt = constants.loc["Number of persons (floating population) per WC(PT)", "Value"]
wc_pt_current = constants.loc["Number of WC(PT)(current)", "Value"]
capital_cost_wc_pt = constants.loc["Capital cost of construction per WC(PT)", "Value"]
# sewer_network_current = constants.loc["Network of sewer in Km (current)", "Value"]
# percentage_sewer_connection_current = constants.loc["Percentage of population connected to sewerage network (current)", "Value"]
cost_sewer_network = constants.loc["Cost of laying sewerage network", "Value"]
annual_maintenance_sewer_network = constants.loc["Annual Maintenance cost for Sewerage Network per KM", "Value"]
# percentage_sewered_sanitation_current = constants.loc["Percentage of population connected to sewered sanitation(current)", "Value"]
# water_consumption_per_capita = constants.loc["Water consumption per capita", "Value"]
# stp_capacity_current = constants.loc["Current Cumulative Design Capacity of STPs", "Value"]
cost_stp_per_mld = constants.loc["Cost of STP per MLD of wastewater", "Value"]
annual_maintenance_stp = constants.loc["Annual maintenance cost of STP per MLD of waste water", "Value"]
desludging_frequency = constants.loc["Desludging frequency for servicing household having septic tanks", "Value"]
septage_emptied_per_household = constants.loc["Septage emptied per household during desludging of septic tank", "Value"]
cost_co_treatment = constants.loc["Cost of co treatment facility at STP", "Value"]
cost_fstp = constants.loc["Cost of FSTP", "Value"]
annual_maintenance_fstp = constants.loc["Total annual maintenance cost of FSTP", "Value"]
ulb_officials_trained = constants.loc["ULB officials to be trained", "Value"]
annual_cost_capacity_building = constants.loc["Annual Cost of capacity building per person(projected)", "Value"]
annual_cost_public_awareness = constants.loc["Annual cost of public awareness campaign per person (projected)", "Value"]
discount_rate = constants.loc["Discount Rate", "Value"]

# Calculations
n = (target_year - year_current) / 10
# population_projected = population_current * (1 + rate_decadal_growth / 100) ** n
# population_additional = population_projected - population_current

# percentage_slum_population_current = (slum_population_current / population_current) * 100
# percentage_slum_population_projected = percentage_slum_population_current - 10
# slum_population_projected = (percentage_slum_population_projected / 100) * population_projected

# floating_population_projected = (percentage_floating_population_current / 100) * population_projected

# urban_households_projected = population_projected / (population_current / urban_households_current)
# urban_households_tap_water_current = (percentage_urban_households_tap_water / 100) * urban_households_current
# urban_households_fhtc = urban_households_projected - urban_households_tap_water_current
# capital_cost_piped_water = urban_households_fhtc * fhtc_cost_per_household

# wc_ct_projected = slum_population_projected / persons_per_wc_ct
# additional_wc_ct = wc_ct_projected - wc_ct_current
# total_capital_cost_wc_ct = additional_wc_ct * capital_cost_wc_ct

# wc_pt_projected = floating_population_projected / persons_per_wc_pt
# additional_wc_pt = wc_pt_projected - wc_pt_current
# total_capital_cost_wc_pt = additional_wc_pt * capital_cost_wc_pt

# population_connected_sewer_current = (percentage_sewer_connection_current / 100) * population_current
# length_sewer_per_person = (sewer_network_current * 1000) / population_connected_sewer_current
# population_connected_sewer_projected = (percentage_sewer_connection_current / 100) * population_projected
# sewer_network_projected = (length_sewer_per_person * population_connected_sewer_projected) / 1000
# gap_sewer_network = sewer_network_projected - sewer_network_current
# capital_cost_sewer_network = gap_sewer_network * cost_sewer_network
# annual_maintenance_sewer_network_total = gap_sewer_network * annual_maintenance_sewer_network

# population_connected_sewer_projected = (percentage_sewered_sanitation_current / 100) * population_projected * 0.8
# sewage_generated_projected = 0.8 * population_connected_sewer_projected * water_consumption_per_capita / 1000000
# gap_treatment_capacity = max(0, sewage_generated_projected - stp_capacity_current)
# capital_cost_additional_stp = gap_treatment_capacity * cost_stp_per_mld
# annual_maintenance_stp_total = gap_treatment_capacity * annual_maintenance_stp

# households_septic_tanks = urban_households_projected * (1 - percentage_sewered_sanitation_current / 100)
# septage_treated_per_day = households_septic_tanks * septage_emptied_per_household / (desludging_frequency * 300)
# cost_co_treatment_total = septage_treated_per_day * cost_co_treatment
# cost_fstp_total = septage_treated_per_day * cost_fstp
# annual_maintenance_fstp_total = septage_treated_per_day * annual_maintenance_fstp

# officials_capacity_building = (ulb_officials_trained / 100) * population_projected
# total_annual_cost_capacity_building = officials_capacity_building * annual_cost_capacity_building
# total_annual_cost_public_awareness = population_projected * annual_cost_public_awareness
# total_training_outreach_cost = total_annual_cost_capacity_building + total_annual_cost_public_awareness