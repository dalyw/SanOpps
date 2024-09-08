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
def __(mo):
    b = mo.ui.run_button()
    b
    return b,


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

    objs = {}
    for _, param_row in params.iterrows():
        if param_row['varname'] not in objs:
            objs[param_row['varname']] = {}
        cur_proj = param_row['current_projected']
        if param_row['varname'] == 'percent_sewerage':
           objs[param_row['varname']][cur_proj] = mo.ui.slider(
                start=param_row['start'],
                stop=param_row['stop'],
                step=param_row['step'],
                label=param_row['label'],
                show_value=True
            )
        else:
            objs[param_row['varname']][cur_proj] = mo.ui.number(
                start=param_row['start'],
                stop=param_row['stop'],
                step=param_row['step'],
                value=param_row['value'],
                label=param_row['label']
            )
    return cur_proj, objs, param_row, params


@app.cell
def input_data_ui(mo):
    mo.md(r"""Input Data""")
    return


@app.cell
def input_data_ui_accordion(mo, objs):
    # mo.accordion(
    #     {
    #         "Population": mo.vstack([objs['total_households']['current'],
    #                                  objs['total_households']['projected'],
    #                                  objs['population']['current'],
    #                                  objs['population']['projected']]),
    #         "Toilets and Sewerage Connection":
    #          mo.vstack([
    #           objs['households_with_toilet_access']['current'],
    #           objs['households_with_toilet_access']['projected'],
    #           objs['percent_sewerage']['current'],
    #           objs['public_toilets']['current'],
    #           objs['community_toilets']['current']])
    #     }
    # )

    mo.vstack([objs['total_households']['current'], 
               objs['total_households']['projected'], 
               objs['population']['current'], objs['population']['projected'],
               objs['households_with_toilet_access']['current'],
               objs['households_with_toilet_access']['projected'],
               objs['percent_sewerage']['current'],
               objs['public_toilets']['current'],
               objs['community_toilets']['current']])

    return


@app.cell
def calculate_additional_demand(b, mo, objs):
    mo.stop(not b.value, "Click `run` to submit")

    objs['population']['adtl'] = objs['population']['projected'].value - objs['population']['current'].value

    objs['public_toilets']['adtl'] = objs['public_toilets']['current'].value *(objs['population']['projected'].value / objs['population']['current'].value - 1)

    objs['community_toilets']['adtl'] = objs['community_toilets']['current'].value *(objs['population']['projected'].value / objs['population']['current'].value - 1)

    objs['households_with_toilet_access']['adtl'] = objs['households_with_toilet_access']['projected'].value - objs['households_with_toilet_access']['current'].value


    objs['stp_capacity'] = {
        'current': objs['stp_count']['current'].value * objs['stp_unit_capacity']['current'].value,
        'adtl': objs['stp_count']['current'].value * objs['stp_unit_capacity']['current'].value / objs['population']['current'].value * objs['population']['projected'].value
    }

    objs['percent_sewerage']['adtl'] = 1.0

    objs['sewerage_length'] = {
        'current': objs['percent_sewerage']['current'].value * objs['population']['current'].value,
        'adtl': objs['percent_sewerage']['adtl'] * objs['population']['adtl']
    }
    return


@app.cell
def calculate_costs(objs, pd):
    # Construction and Operational Costs
    costs = pd.read_csv('costs.csv')
    costs.set_index(costs.columns[0], inplace=True)

    costs_dict = {}
    for index, cost_row in costs.iterrows():
        costs_dict[index] = {
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
            'low': costs_dict[sub_key]['capital']['low'] * objs[varname]['adtl'],
            'high': costs_dict[sub_key]['capital']['high'] * objs[varname]['adtl'],
            'average': costs_dict[sub_key]['capital']['average'] * objs[varname]['adtl'],
            }
        operational_costs[sub_key] = {
            'low': costs_dict[sub_key]['operational']['low'] * objs[varname]['adtl'],
            'high': costs_dict[sub_key]['operational']['high'] * objs[varname]['adtl'],
            'average': costs_dict[sub_key]['operational']['average'] * objs[varname]['adtl'],
            }
    return (
        capital_costs,
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

    stacked_average_costs = pd.DataFrame(stacked_average_costs, copy=False)

    _cost_chart = alt.Chart(stacked_average_costs).mark_bar().encode(
            x=alt.X('Component:N', title='Components'),
            y=alt.Y('Cost:Q', title='Cost (INR)'),
            color='Type:N',
            tooltip=['Component:N', 'Cost:Q', 'Type:N']
        ).properties(
            title='Cost of Investment',
            width=500,
            height=300
        )

    cost_chart = mo.ui.altair_chart(_cost_chart)
    return cost_chart, error_bars, key, stacked_average_costs


@app.cell
def __(cost_chart):
    cost_chart
    return


if __name__ == "__main__":
    app.run()
