import marimo

__generated_with = "0.8.9"
app = marimo.App()


@app.cell
def import_libraries():
    # import necessary libraries
    import pandas as pd
    import matplotlib.pyplot as plt
    import marimo as mo
    import altair as alt
    return alt, mo, pd, plt


@app.cell
def sidebar(mo):
    mo.sidebar(
        [
            mo.md("# SanOpps"),
            mo.nav_menu(
                {
                    "#/home": f"{mo.icon('lucide:home')} [Home](https://www.worldtoilet.org/)",
                    "#/about": f"{mo.icon('lucide:droplet')} [World Toilet Organization](https://www.worldtoilet.org/)",
                    "Documentation": {
                        "https://dalyw.github.io/SanOpps/documentation.html": f"{mo.icon('lucide:book-open-text')}Glossary",
                        "https://github.com/dalyw/SanOpps": f"{mo.icon('lucide:code')}Source Code",
                    },
                },
                orientation="vertical",
            ),
        ]
    )
    return


@app.cell
def input_data(mo, pd):
    params = pd.read_csv('params.csv')

    number_objects = {}
    for _, param_row in params.iterrows():
        if param_row['varname'] == 'current_percent_sewerage':
            number_objects[param_row['varname']] = mo.ui.slider(
                start=param_row['start'],
                stop=param_row['stop'],
                step=param_row['step'],
                value=param_row['value'],
                label=param_row['label']
            )
        else:
            number_objects[param_row['varname']] = mo.ui.number(
                start=param_row['start'],
                stop=param_row['stop'],
                step=param_row['step'],
                value=param_row['value'],
                label=param_row['label']
            )

    number_objects['total_households'] = {
        'current': number_objects["current_total_households"],
        'projected': number_objects["projected_total_households"]
    }
    number_objects['household_toilet_access'] = {
        'current': number_objects["current_households_with_toilet_access"],
        'projected': number_objects["projected_households_with_toilet_access"]
    }
    number_objects['population'] = {
        'current': number_objects["current_population"],
        'projected': number_objects["projected_population"]
    }
    number_objects['public_toilets'] = {
        'current': number_objects["current_public_toilets"],
    }
    number_objects['community_toilets'] = {
        'current': number_objects["current_community_toilets"],
    }
    number_objects['percent_sewerage_connections'] = {
        'current': number_objects["current_percent_sewerage"],
        'adtl': 1.0
    }
    return number_objects, param_row, params


@app.cell
def __(params):
    print(params['varname'].tolist())
    return


@app.cell
def input_data_ui(mo):
    mo.md(r"""Input Data""")
    return


@app.cell
def input_data_ui_accordion(mo, number_objects):
    mo.accordion(
        {
            "Population": mo.vstack([number_objects['total_households']['current'],
                                     number_objects['total_households']['projected'],
                                     number_objects['population']['current'],
                                     number_objects['population']['projected']]),
            "Toilets and Sewerage Connection":
             mo.vstack([
              number_objects['household_toilet_access']['current'],
              number_objects['household_toilet_access']['projected'],
              number_objects['percent_sewerage_connections']['current'],
              number_objects['public_toilets']['current'],
              number_objects['community_toilets']['current']])
        }
    )
    return


@app.cell
def calculate_additional_demand(number_objects):
    number_objects['population']['adtl'] = number_objects['population']['projected'].value - number_objects['population']['current'].value

    number_objects['public_toilets']['adtl'] = number_objects['public_toilets']['current'].value *(number_objects['population']['projected'].value / number_objects['population']['current'].value - 1)

    number_objects['community_toilets']['adtl'] = number_objects['community_toilets']['current'].value *(number_objects['population']['projected'].value / number_objects['population']['current'].value - 1)

    number_objects['household_toilet_access']['adtl'] = number_objects['household_toilet_access']['projected'].value - number_objects['household_toilet_access']['current'].value

    number_objects['stp_capacity'] = {
        'current': number_objects['stp_count'].value * number_objects['stp_unit_capacity'].value
    }

    number_objects['sewerage_length'] = {
        'current': number_objects['percent_sewerage_connections']['current'].value * number_objects['population']['current'].value,
        'adtl': number_objects['percent_sewerage_connections']['adtl'] * number_objects['population']['adtl']
    }
    return


@app.cell
def calculate_costs(number_objects, pd):
    # Construction and Operational Costs
    costs = pd.read_csv('costs.csv')

    costs_dict = {}
    for index, cost_row in costs.iterrows():
        cost_item = cost_row['Cost Item']
        costs_dict[cost_item] = {
            'capital': {
                'low': cost_row['Low Unit Cost'],
                'high': cost_row['High Unit Cost'],
                'average': cost_row['Avg Unit Cost'],
                'unit': cost_row['Capital Cost Unit']
            },
            'operational': {
                'low': cost_row['Low Op Cost'],
                'high': cost_row['High Op Cost'],
                'average': cost_row['Avg Op Cost'],
                'unit': cost_row['Operational Cost Unit']
            },
            'varname': cost_row['varname']
        }

    capital_costs = {}
    operational_costs = {}
    sub_keys = ['Household Toilet','Community Toilet','Public Toilet','Sewerage Connections']
    for sub_key in sub_keys:
        varname = costs_dict[sub_key]['varname']
        capital_costs[sub_key] = {
            'low': costs_dict[sub_key]['capital']['low'] * number_objects[varname]['adtl'],
            'high': costs_dict[sub_key]['capital']['high'] * number_objects[varname]['adtl'],
            'average': costs_dict[sub_key]['capital']['average'] * number_objects[varname]['adtl'],
            }
        operational_costs[sub_key] = {
            'low': costs_dict[sub_key]['operational']['low'] * number_objects[varname]['adtl'],
            'high': costs_dict[sub_key]['operational']['high'] * number_objects[varname]['adtl'],
            'average': costs_dict[sub_key]['operational']['average'] * number_objects[varname]['adtl'],
            }
    return (
        capital_costs,
        cost_item,
        cost_row,
        costs,
        costs_dict,
        index,
        operational_costs,
        sub_key,
        sub_keys,
        varname,
    )


@app.cell
def plot_costs(alt, capital_costs, mo, operational_costs, pd):
    stacked_average_costs = []
    error_bars = []
    for key in capital_costs.keys():
        stacked_average_costs.append({
            'Component': key,
            'Cost': capital_costs[key]['average'],
            'Type': 'capital'
        })
        stacked_average_costs.append({
            'Component': key,
            'Cost': operational_costs[key]['average'],
            'Type': 'operational'
        })
        error_bars.append({
            'Component': key,
            'Cost': capital_costs[key]['high'] - capital_costs[key]['average'],
            'Type': 'high'
        })
        error_bars.append({
            'Component': key,
            'Cost': capital_costs[key]['average'] - capital_costs[key]['low'],
            'Type': 'low'
        })

    stacked_average_costs = pd.DataFrame(stacked_average_costs)

    # Create stacked bar chart using Altair
    _cost_chart = alt.Chart(stacked_average_costs).mark_bar().encode(
            x=alt.X('Component:N', title='Components'),
            y=alt.Y('Cost:Q', title='Cost (INR)'),
            color='Type:N',
            tooltip=['Component:N', 'Cost:Q', 'Type:N']
        ).properties(
            title='Cost of Investment',
            width=500,
            height=300
        ).transform_calculate(
            y_error='datum.Type === "capital" ? ' + str(error_bars) + ' : 0'  
        )

    cost_chart = mo.ui.altair_chart(_cost_chart)
    return cost_chart, error_bars, key, stacked_average_costs


@app.cell
def __(cost_chart, mo):
    mo.vstack([cost_chart, cost_chart.value])
    return


if __name__ == "__main__":
    app.run()
