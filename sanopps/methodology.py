import marimo

__generated_with = "0.8.9"
app = marimo.App()


@app.cell
def __():
    import pandas as pd
    import matplotlib.pyplot as plt
    import marimo as mo
    import altair as alt
    return alt, mo, pd, plt


@app.cell
def __(mo):
    mo.sidebar(
        [
            mo.md("# SanOpps"),
            mo.nav_menu(
                {
                    "#/home": f"{mo.icon('lucide:home')} Home",
                    "#/about": f"{mo.icon('lucide:user')} World Toilet Organization",
                    "#/contact": f"{mo.icon('lucide:phone')} Documentation",
                    "Documentation": {
                        "https://twitter.com/marimo_io": "Twitter",
                        "https://github.com/dalyw/SanOpps": "GitHub",
                    },
                },
                orientation="vertical",
            ),
        ]
    )
    return


@app.cell
def __(mo):
    # Initialize all mo.ui.numbers first
    current_total_households = mo.ui.number(start=1, stop=1000000, step=1, value=506353, label="Current Total Households")
    projected_total_households = mo.ui.number(start=1, stop=1000000, step=1, value=848750, label="Projected Total Households")

    current_fraction_households_with_toilet_access = mo.ui.number(start=0.0, stop=1.0, step=0.01, value=1.0, label="Current Fraction Households with Toilet Access")
    projected_fraction_households_with_toilet_access = mo.ui.number(start=0.0, stop=1.0, step=0.01, value=1.0, label="Projected Fraction Households with Toilet Access")

    current_population = mo.ui.number(start=1, stop=10000000, step=1, value=2405665, label="Current Population")
    projected_population = mo.ui.number(start=1, stop=10000000, step=1, value=4074000, label="Projected Population")

    stp_count = mo.ui.number(start=1, stop=100, step=1, value=4, label="STP Count")
    stp_capacity_mld = mo.ui.number(start=1, stop=1000, step=1, value=340, label="STP Capacity (mld)")

    total_solid_waste_per_day_tpd = mo.ui.number(start=0, stop=5000, step=0.1, value=1316.023, label="Total Solid Waste per Day (tpd)")
    swm_tpd_per_person = mo.ui.number(start=0.0, stop=1.0, step=0.0001, value=0.0005, label="SWM per Person (tpd)")
    additional_sw_2030_tpd = mo.ui.number(start=0.0, stop=1000.0, step=0.1, value=834.1675, label="Additional SWM 2030 (tpd)")
    addition_total_sw_2030_tpy = mo.ui.number(start=0.0, stop=1000000.0, step=1.0, value=333122.8744, label="Additional SWM 2030 (tpy)")

    current_total_number_public_toilets = mo.ui.number(start=1, stop=1000, step=1, value=88, label="Current Total Number of Public Toilets")
    current_total_number_community_toilets = mo.ui.number(start=1, stop=1000, step=1, value=60, label="Current Total Number of Community Toilets")

    current_percent_sewerage_connections = mo.ui.number(start=0.0, stop=1.0, step=0.01, value=0.15, label="Current Percent of Sewerage Connections")

    # Define dictionaries
    total_households = {
        'current': current_total_households,
        'projected': projected_total_households
    }
    fraction_households_with_toilet_access = {
        'current': current_fraction_households_with_toilet_access,
        'projected': projected_fraction_households_with_toilet_access
    }

    population = {
        'current': current_population,
        'projected': projected_population
    }

    total_number_public_toilets = {
        'current': current_total_number_public_toilets,
    }
    total_number_community_toilets = {
        'current': current_total_number_community_toilets,
    }

    percent_sewerage_connections = {
        'current': current_percent_sewerage_connections,
        'additional': 1.0
    }
    return (
        addition_total_sw_2030_tpy,
        additional_sw_2030_tpd,
        current_fraction_households_with_toilet_access,
        current_percent_sewerage_connections,
        current_population,
        current_total_households,
        current_total_number_community_toilets,
        current_total_number_public_toilets,
        fraction_households_with_toilet_access,
        percent_sewerage_connections,
        population,
        projected_fraction_households_with_toilet_access,
        projected_population,
        projected_total_households,
        stp_capacity_mld,
        stp_count,
        swm_tpd_per_person,
        total_households,
        total_number_community_toilets,
        total_number_public_toilets,
        total_solid_waste_per_day_tpd,
    )


@app.cell
def __(mo):
    mo.md(r"""Input Data""")
    return


@app.cell
def __(
    current_fraction_households_with_toilet_access,
    current_percent_sewerage_connections,
    current_population,
    current_total_households,
    current_total_number_community_toilets,
    current_total_number_public_toilets,
    mo,
    projected_fraction_households_with_toilet_access,
    projected_population,
    projected_total_households,
):
    mo.accordion(
        {
            "Population": mo.vstack([current_total_households,
              projected_total_households,
              current_population,
              projected_population])
    ,
            "Toilets and Sewerage Connection":
             mo.vstack([
              current_fraction_households_with_toilet_access,
              projected_fraction_households_with_toilet_access,
              current_percent_sewerage_connections,
              current_total_number_public_toilets,
              current_total_number_community_toilets])
        }
    )
    return


@app.cell
def __(
    fraction_households_with_toilet_access,
    percent_sewerage_connections,
    population,
    stp_capacity_mld,
    stp_count,
    total_households,
    total_number_community_toilets,
    total_number_public_toilets,
):
    total_number_households_with_toilet_access = {
        'current': total_households['current'].value * fraction_households_with_toilet_access['current'].value,
        'projected': total_households['projected'].value * fraction_households_with_toilet_access['projected'].value,
        'additional': total_households['projected'].value * fraction_households_with_toilet_access['projected'].value - total_households['current'].value * fraction_households_with_toilet_access['current'].value
        }
    population['additional'] = population['projected'].value - population['current'].value

    total_number_public_toilets['additional'] = total_number_public_toilets['current'].value *(population['projected'].value / population['current'].value - 1)
    total_number_community_toilets['additional'] = total_number_community_toilets['current'].value *(population['projected'].value / population['current'].value - 1)

    stp_total_mld = {
        'current': stp_count.value * stp_capacity_mld.value,
        }

    sewerage_connection_length = {
        'current': percent_sewerage_connections['current'].value * population['current'].value,
        'additional': percent_sewerage_connections['additional'] * population['additional']
    }
    return (
        sewerage_connection_length,
        stp_total_mld,
        total_number_households_with_toilet_access,
    )


@app.cell
def __(
    pd,
    sewerage_connection_length,
    total_number_community_toilets,
    total_number_households_with_toilet_access,
    total_number_public_toilets,
):
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
