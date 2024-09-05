import marimo

__generated_with = "0.8.9"
app = marimo.App()


@app.cell
def __():
    # import necessary libraries
    import pandas as pd
    import matplotlib.pyplot as plt
    import marimo as mo
    import altair as alt
    return alt, mo, pd, plt


@app.cell
# create sidebar of links to source code and resources
def __(mo):
    mo.sidebar(
        [
            mo.md("# SanOpps"),
            mo.nav_menu(
                {
                    "#/home": f"{mo.icon('lucide:home')} Home",
                    "#/about": f"{mo.icon('lucide:user')} World Toilet Organization",
                    "https://www.worldtoilet.org/": "World Toilet Organization",
                    "Documentation": {
                        "https://dalyw.github.io/SanOpps/": "Glossary",
                        "https://github.com/dalyw/SanOpps": "Source Code",
                    },
                },
                orientation="vertical",
            ),
        ]
    )
    return


@app.cell
# define user-input number values
def __(mo):
    current_households = mo.ui.number(start=1, stop=1000000, step=1, value=506353, label="Current Total Households")
    projected_households = mo.ui.number(start=1, stop=1000000, step=1, value=848750, label="Projected Total Households")

    current_fraction_household_toilet_access = mo.ui.number(start=0.0, stop=1.0, step=0.01, value=1.0, label="Current Fraction Households with Toilet Access")
    projected_fraction_household_toilet_access = mo.ui.number(start=0.0, stop=1.0, step=0.01, value=1.0, label="Projected Fraction Households with Toilet Access")

    current_population = mo.ui.number(start=1, stop=10000000, step=1, value=2405665, label="Current Population")
    projected_population = mo.ui.number(start=1, stop=10000000, step=1, value=4074000, label="Projected Population")

    stp_count = mo.ui.number(start=1, stop=100, step=1, value=4, label="STP Count")
    stp_capacity_mld = mo.ui.number(start=1, stop=1000, step=1, value=340, label="STP Capacity (mld)")

    solid_waste_per_person_per_day = mo.ui.number(start=0.0, stop=1.0, step=0.0001, value=0.0005, label="Solid Waste per Person per Day (tpd)")

    current_public_toilets = mo.ui.number(start=1, stop=1000, step=1, value=88, label="Current Total Number of Public Toilets")
    current_community_toilets = mo.ui.number(start=1, stop=1000, step=1, value=60, label="Current Total Number of Community Toilets")

    current_percent_sewerage_connections = mo.ui.number(start=0.0, stop=1.0, step=0.01, value=0.15, label="Current Percent of Sewerage Connections")

    # Define dictionaries
    total_households = {
        'current': current_households,
        'projected': projected_households
    }
    fraction_household_toilet_access = {
        'current': current_fraction_household_toilet_access,
        'projected': projected_fraction_household_toilet_access
    }

    population = {
        'current': current_population,
        'projected': projected_population
    }

    public_toilets = {
        'current': current_public_toilets,
    }
    community_toilets = {
        'current': current_community_toilets,
    }

    percent_sewerage_connections = {
        'current': current_percent_sewerage_connections,
        'additional': 1.0
    }
    return (
        current_fraction_household_toilet_access,
        current_percent_sewerage_connections,
        current_population,
        current_households,
        current_community_toilets,
        current_public_toilets,
        fraction_household_toilet_access,
        percent_sewerage_connections,
        population,
        projected_fraction_household_toilet_access,
        projected_population,
        projected_households,
        stp_capacity_mld,
        stp_count,
        solid_waste_per_person_per_day,
        total_households,
        community_toilets,
        public_toilets,
    )


@app.cell
def __(mo):
    mo.md(r"""Input Data""")
    return


@app.cell
def __(
    mo,
    current_fraction_household_toilet_access,
    current_percent_sewerage_connections,
    current_population,
    current_households,
    current_community_toilets,
    current_public_toilets,
    projected_fraction_household_toilet_access,
    projected_population,
    projected_households,
):
    mo.accordion(
        {
            "Population": mo.vstack([current_households,
              projected_households,
              current_population,
              projected_population])
    ,
            "Toilets and Sewerage Connection":
             mo.vstack([
              current_fraction_household_toilet_access,
              projected_fraction_household_toilet_access,
              current_percent_sewerage_connections,
              current_public_toilets,
              current_community_toilets])
        }
    )
    return


@app.cell
def __(
    fraction_household_toilet_access,
    percent_sewerage_connections,
    population,
    stp_capacity_mld,
    stp_count,
    total_households,
    community_toilets,
    public_toilets,
):
    total_number_households_with_toilet_access = {
        'current': total_households['current'].value * fraction_household_toilet_access['current'].value,
        'projected': total_households['projected'].value * fraction_household_toilet_access['projected'].value,
        'additional': total_households['projected'].value * fraction_household_toilet_access['projected'].value - total_households['current'].value * fraction_household_toilet_access['current'].value
        }
    population['additional'] = population['projected'].value - population['current'].value

    public_toilets['additional'] = public_toilets['current'].value *(population['projected'].value / population['current'].value - 1)
    community_toilets['additional'] = community_toilets['current'].value *(population['projected'].value / population['current'].value - 1)

    stp_total_mld = {
        'current': stp_count.value * stp_capacity_mld.value,
        }

    sewerage_length = {
        'current': percent_sewerage_connections['current'].value * population['current'].value,
        'additional': percent_sewerage_connections['additional'] * population['additional']
    }
    return (
        sewerage_length,
        stp_total_mld,
        total_number_households_with_toilet_access,
    )


@app.cell
def __(
    pd,
    sewerage_length,
    community_toilets,
    total_number_households_with_toilet_access,
    public_toilets,
):
    # Construction and Operational Costs
    costs = pd.read_csv('costs.csv')

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


    capital_costs = {
        'household_toilet': costs_dict['Household Toilet']['capital']['average'] * total_number_households_with_toilet_access['additional'],
        'public_toilet': costs_dict['Public Toilet']['capital']['average'] * public_toilets['additional'],
        'community_toilet': costs_dict['Community Toilet']['capital']['average'] * community_toilets['additional'],
        'sewer': costs_dict['Sewerage Connections']['capital']['average'] * sewerage_length['additional']
    }
    operational_costs = {
        'household_toilet': costs_dict['Household Toilet']['operational']['average'] * total_number_households_with_toilet_access['additional'],
        'public_toilet': costs_dict['Public Toilet']['operational']['average'] * public_toilets['additional'],
        'community_toilet': costs_dict['Community Toilet']['operational']['average'] * community_toilets['additional'],
        'sewer': costs_dict['Sewerage Connections']['operational']['average'] * sewerage_length['additional']
    }

    # Calculate total costs
    total_capital_cost = sum(capital_costs.values())
    total_operational_cost = sum(operational_costs.values())
    total_cost = total_capital_cost + total_operational_cost

    # Prepare data for plotting
    components = list(capital_costs.keys())
    capital_values = list(capital_costs.values())
    operational_values = list(operational_costs.values())
    return (
        capital_costs,
        capital_values,
        components,
        cost_item,
        costs,
        costs_dict,
        index,
        operational_costs,
        operational_values,
        row,
        total_capital_cost,
        total_cost,
        total_operational_cost,
    )


@app.cell
def __(alt, capital_values, components, mo, operational_values, pd):
    # Prepare data for Altair
    data = pd.DataFrame({
        'Component': components,
        'Capital Cost': capital_values,
        'Operational Cost': operational_values
    })

    # Create stacked bar chart using Altair
    chart = alt.Chart(data).transform_fold(
        ['Capital Cost', 'Operational Cost'],
        as_=['Cost Type', 'Value']
    ).mark_bar().encode(
        x=alt.X('Component:N', title='Components'),
        y=alt.Y('sum(Value):Q', title='Cost (Million INR)'),
        color='Cost Type:N',
        tooltip=['Component:N', 'sum(Value):Q']
    ).properties(
        title='Breakdown of Total Cost by Component',
        width=600,
        height=400
    ).transform_calculate(
        Value='datum.Value / 1000000'  # Convert to millions
    )

    # Display the chart
    cost_chart = mo.ui.altair_chart(chart, chart_selection='point')
    cost_chart
    return chart, cost_chart, data


if __name__ == "__main__":
    app.run()
