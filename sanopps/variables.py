import pandas as pd

# Variables
total_households = {
    'current': 506353,
    'projected': 848750
}
fraction_households_with_toilet_access = {
    'current': 1,
    'projected': 1
}

total_number_households_with_toilet_access = {
    'current': total_households['current'] * fraction_households_with_toilet_access['current'],
    'projected': total_households['projected'] * fraction_households_with_toilet_access['projected']
}

population = {
    'current': 2405665,
    'projected': 4074000
}

# STP (Sewage Treatment Plant) data
stp_count = 4
stp_capacity_mld = 340
stp_total_mld = {
    'current': stp_count * stp_capacity_mld,
}

additional_population_2030 = population['projected'] - population['current']
mld_per_person = stp_capacity_mld / population['current']
additional_total_mld_2030 = mld_per_person * additional_population_2030

# Solid Waste Management
total_solid_waste_per_day_tpd = 1316.023
population_swm = {
    'current': 2405665,
    'projected': 2405665 + 1668335  # current + additional
}
swm_tpd_per_person = 0.0005
additional_sw_2030_tpd = 834.1675
addition_total_sw_2030_tpy = 333122.8744

# Training and Outreach Cost
community_training_cost_per_person = 5000
public_awareness_cost_per_person_annually = 10
total_population_2030 = 4074000
total_community_training_cost = 20370000000
total_public_awareness_cost = 40740000
total_training_outreach_cost = 20410740000

total_number_public_toilets = {
    'current': 88,
}
total_number_community_toilets = {
    'current': 60,
}

percent_sewerage_connections = {
    'current': 0.15,
    'additional': 1.0
}
sewerage_connection_length = {
    'current': percent_sewerage_connections['current'] * population['current'],
    'additional': percent_sewerage_connections['additional'] * additional_population_2030
}

# additional hh to be served
total_households['additional'] = total_households['projected'] - total_households['current']

# calculate additional toilets needed
total_number_public_toilets['additional'] = total_number_public_toilets['current'] * (population['projected'] / population['current'] - 1)
total_number_community_toilets['additional'] = total_number_community_toilets['current'] * (population['projected'] / population['current'] - 1)
total_number_households_with_toilet_access['additional'] = total_number_households_with_toilet_access['current'] * (population['projected'] / population['current'] - 1)
sewerage_connection_length['additional'] = sewerage_connection_length['current'] * (population['projected'] / population['current'] - 1)

# Construction and Operational Costs
costs = pd.read_csv('capital_costs.csv')

costs_dict = {}
for index, row in costs.iterrows():
    cost_item = row['Cost Item']
    costs_dict[cost_item] = {
        'capital': {
            'low': row['Low Unit Cost'],
            'high': row['High Unit Cost'],
            'average': row['Avg Unit Cost'],
            'unit': row['Capital Cost Unit']
        },
        'operational': {
            'low': row['Low Op Cost'],
            'high': row['High Op Cost'],
            'average': row['Avg Op Cost'],
            'unit': row['Operational Cost Unit']
        }
    }

print(costs_dict)

capital_costs = {
    'household_toilet': costs_dict['Household Toilet']['capital']['average'] * total_number_households_with_toilet_access['additional'],
    'public_toilet': costs_dict['Public Toilet']['capital']['average'] * total_number_public_toilets['additional'],
    'community_toilet': costs_dict['Community Toilet']['capital']['average'] * total_number_community_toilets['additional'],
    'sewer': costs_dict['Sewerage Connections']['capital']['average'] * sewerage_connection_length['additional']
}
operational_costs = {
    'household_toilet': costs_dict['Household Toilet']['operational']['average'] * total_number_households_with_toilet_access['additional'],
    'public_toilet': costs_dict['Public Toilet']['operational']['average'] * total_number_public_toilets['additional'],
    'community_toilet': costs_dict['Community Toilet']['operational']['average'] * total_number_community_toilets['additional'],
    'sewer': costs_dict['Sewerage Connections']['operational']['average'] * sewerage_connection_length['additional']
}

import matplotlib.pyplot as plt

# Calculate total costs
total_capital_cost = sum(capital_costs.values())
total_operational_cost = sum(operational_costs.values())
total_cost = total_capital_cost + total_operational_cost

# Prepare data for plotting
components = list(capital_costs.keys())
capital_values = list(capital_costs.values())
operational_values = list(operational_costs.values())

# Create stacked bar chart
fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(components, capital_values, label='Capital Cost')
ax.bar(components, operational_values, bottom=capital_values, label='Operational Cost')

ax.set_ylabel('Cost (INR)')
ax.set_title('Breakdown of Total Cost by Component')
ax.legend()

# Add total cost labels on top of each bar
for i, component in enumerate(components):
    total = capital_values[i] + operational_values[i]
    ax.text(i, total, f'{total:.2e}', ha='center', va='bottom')

plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Print total costs
print(f"Total Capital Cost: {total_capital_cost:.2e} INR")
print(f"Total Operational Cost: {total_operational_cost:.2e} INR")
print(f"Total Cost: {total_cost:.2e} INR")

plt.show()

