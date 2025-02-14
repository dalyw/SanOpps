import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from streamlit.components import v1 as components
import time
import json
import os

read_local=True
if read_local:
    city_default_data = pd.read_csv('../data/city_default_data.csv')
    input_labels = pd.read_csv('../data/input_labels.csv')
    definitions = pd.read_csv('../data/definitions.csv')
    constants = pd.read_csv('../data/params.csv')
else:
    city_default_data = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/city_default_data.csv')
    input_labels = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/input_labels.csv')
    definitions = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/definitions.csv')
    constants = pd.read_csv("https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/params.csv", index_col="Indicator")


# add constants to st.session_state
for _, row in constants.iterrows():
    if pd.notna(row['varname']): 
        st.session_state[row['varname']] = row['Value']

st.title("SanOpps: The WASH Cost-Benefit Analysis Tool for Local Government")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Home Page", "Input Parameters", "Dashboard", "Summary", "Definitions", "Help"])

def switch_tab(tab):
    return f"""
    var tabGroup = window.parent.document.getElementsByClassName("stTabs")[0]
    var tab = tabGroup.getElementsByTagName("button")
    tab[{tab}].click()
    """

# Initialize session state for calculations
if 'calculations_done' not in st.session_state:
    st.session_state.calculations_done = False
    
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
    
if 'summary_data' not in st.session_state:
    st.session_state.summary_data = None

# Create configs directory if it doesn't exist
if not os.path.exists('configs'):
    os.makedirs('configs')
    
def save_config():
    """Save current configuration to JSON file"""
    config = {}
    for key in st.session_state:
        # Only save input parameters, not calculation results
        if key not in ['calculations_done', 'results_df', 'summary_data']:
            config[key] = st.session_state[key]
    
    # Convert config to JSON string
    json_str = json.dumps(config)
    
    # Get filename from user
    filename = st.text_input("Enter filename (without .json extension)", "sanopps_config")
    
    if filename:  # Only show download button after filename is entered
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")
        
        # Create download button
        st.download_button(
            label="Download Configuration",
            data=json_str,
            file_name=f"{filename}.json",
            mime="application/json"
        )

def load_config():
    """Load configuration from JSON file"""
    uploaded_file = st.file_uploader("Upload configuration file", type=['json'])
    if uploaded_file is not None:
        config = json.load(uploaded_file)
        # Update session state with loaded config
        for key, value in config.items():
            st.session_state[key] = value
        st.success("Configuration loaded successfully")
        
with tab1:
    # Use container to force full height
    with st.container():
        col1, col2 = st.columns([7,3], gap="large")
        with col1:
            st.write("This interactive tool is designed to support policy-makers, researchers, and stakeholders in assessing the economic viability and social impact of Water, Sanitation, and Hygiene (WASH) initiatives. It provides a comprehensive analysis of the present and future costs and benefits associated with implementing WASH projects, and helps identify the highest value-generating investments.")

            st.subheader("Why use SanOpps?")
            st.write("SanOpps provides a localized understanding of a global trend: that investment in WASH drives economic growth. The dashboard lays out the return on investment potential for WASH in your city.")

            st.subheader("SanOpps Features")

            # Add vertical space before mermaid diagram
            st.markdown("<br><br>", unsafe_allow_html=True)
            # generating mermaid flowchart & class breakdown, using example from https://discuss.streamlit.io/t/st-markdown-does-not-render-mermaid-graphs/25576/9
            def mermaid(code: str) -> None:
                components.html(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; min-height: 400px;">
                        <pre class="mermaid" style="width: 100%; height: auto;">
                            {code}
                        </pre>

                        <script type="module">
                            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                            mermaid.initialize({{ startOnLoad: true, theme: 'neutral', flowchart: {{ htmlLabels: true }}, fontSize: 18 }});
                        </script>
                    </div>
                    """
                )

            mermaid("""
                classDiagram
                    direction TB
                    class Data_Inputs{
                        Interactive input allows for
                        customization of key variables,
                        tailoring the analysis to 
                        specific regions.
                    }
                    class Summary{
                        Presents a table cumulative cost 
                        and benefit values, broken down 
                        every 10 years after the initial 
                        investment.
                    }
                    class Dashboard{
                        Presents adaptable data views for 
                        cost and benefit figures, tracking 
                        investments from the initial year 
                        through a 30-year projection.
                    }
                    class Cost_Indicators{
                        Captures cost of water supply
                        systems, sanitation facilities,
                        and sewage management.
                    }
                    class Benefit_Indicators{
                        Captures benefits from improved
                        health, productivity gains,
                        convenience, and quality of life
                    }
                    Dashboard <|-- Cost_Indicators
                    Dashboard <|-- Benefit_Indicators
                    Data_Inputs --|> Summary
                    Summary --|> Dashboard
                    
            """)

            # Add vertical space after mermaid diagram
            st.markdown("<br><br>", unsafe_allow_html=True)
    with col2:
        st.subheader("What is Water, Sanitation, and Hygiene (WASH)?")
        st.write("*WASH initiatives are aimed at improving access to clean Water, Sanitation, and Hygiene practices, particularly in low- and middle-income areas. Investing in WASH infrastructure is essential to improve public health, reduce poverty, promote equitable access to essential services, and enhance socio-economic development.*")

    # Add "Next" button to go to Input Parameters tab, based on suggestions from mathcatsand https://discuss.streamlit.io/t/switch-tabs-programitically/37887/8
    if st.button("Next: Input City Data"):
        script_placeholder = st.empty() # placeholder
        html(f"<script>{switch_tab(1)}</script>", height=0) # adding script to switch tab
        time.sleep(0.1) # brief sleep for script to execute
        script_placeholder.empty() # clear script

with tab2:
    st.markdown("""
    Please Enter Current Year Data to Ensure Precise Cost and Benefit Estimations
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Current Configuration"):
            save_config()
    with col2:
        if st.button("Load Configuration"):
            load_config()
    

    country_col, state_col, city_col = st.columns(3)
    with country_col:
        country = st.selectbox("Select Country", list(city_default_data['Country'].unique())+['Other'], key="country")
    with state_col:
        state = st.selectbox("Select State/Province", list(city_default_data[city_default_data['Country']==country]['State/Province'].unique())+['Other'], key="state")
    with city_col:
        # Store previous city value to detect changes
        prev_city = st.session_state.get('prev_city', None)
        city = st.selectbox("Select City", list(city_default_data[(city_default_data['Country']==country) & (city_default_data['State/Province']==state)]['City'].unique())+['Other'], key="city")
        # Check if city selection changed
        if city != prev_city and city in city_default_data['City'].values:
            city_data = city_default_data[city_default_data['City'] == city].iloc[0]
            # Initialize session state values if they don't exist
            for key in ['currency', 'urban_pop', 'current_year', 'growth_rate', 'target_year', 'inflation']:
                if key not in st.session_state:
                    default_value = input_labels[input_labels['key']==key]['default_value'].iloc[0]
                    st.session_state[key] = city_data.get(key, default_value)
            # Store current city as previous
            st.session_state.prev_city = city

    # Use the function to generate inputs
    # Group inputs by category
    categories = input_labels['category'].unique()
    
    # First show required user inputs
    for category in categories:
        st.subheader(category)
        
        # Get user inputs for this category
        user_inputs = input_labels[
            (input_labels['category'] == category) & 
            (input_labels['type'] == 'user_input')
        ]
        
        # Generate inputs for each row
        for _, row in user_inputs.iterrows():
            name_col, input_col, units_col = st.columns([1,1,1])
            with name_col:
                st.write(row['label'])
            with input_col:
                key = row['key']
                # Initialize session state if not already set
                if key not in st.session_state:
                    print(key)
                    st.session_state[key] = float(row['default_value']) if row['value_type'] == 'float' else int(row['default_value']) if row['value_type'] == 'int' else str(row['default_value'])
                
                if key in ['currency', 'co_treat_avail', 'fstp_avail', 'co_treat_proposed']:
                    options = ["INR", "USD", "EUR"] if key == 'currency' else ["NO", "YES"]
                    st.selectbox("", options, key=key, label_visibility="collapsed")
                else:
                    value = st.number_input("", 
                        value=float(st.session_state[key]) if row['value_type'] == 'float' else int(st.session_state[key]) if row['value_type'] == 'int' else str(st.session_state[key]),
                        label_visibility="collapsed", 
                        key=f"input_{key}")  # Use unique key
                    st.session_state[key] = value  # Update session state
            with units_col:
                if row['unit']:
                    if 'currency' in str(row['unit']):
                        st.write(row['unit'].replace('currency', st.session_state.currency))
                    else:
                        st.write(row['unit'])
                else:
                    st.write("")
        
        # Show optional inputs in expander
        optional_inputs = input_labels[
            (input_labels['category'] == category) & 
            (input_labels['type'] == 'optional_input')
        ]
        
        if not optional_inputs.empty:
            with st.expander(f"Optional {category} Parameters"):
                for _, row in optional_inputs.iterrows():
                    name_col, input_col, units_col = st.columns([1,1,1])
                    with name_col:
                        st.write(row['label'])
                    with input_col:
                        key = row['key']
                        print(key)
                        # Initialize session state if not already set
                        if key not in st.session_state:
                            st.session_state[key] = float(row['default_value']) if row['value_type'] == 'float' else int(row['default_value']) if row['value_type'] == 'int' else str(row['default_value'])
                            
                        if key in ['currency', 'co_treat_avail', 'fstp_avail', 'co_treat_proposed']:
                            options = ["INR", "USD", "EUR"] if key == 'currency' else ["NO", "YES"]
                            st.selectbox("", options, key=key, label_visibility="collapsed")
                        else:
                            value = st.number_input("", 
                                value=st.session_state[key],
                                label_visibility="collapsed", 
                                key=f"input_opt_{key}")  # Use unique key
                            st.session_state[key] = value  # Update session state
                    with units_col:
                        if row['unit']:
                            if 'currency' in str(row['unit']):
                                st.write(row['unit'].replace('currency', st.session_state.currency))
                            else:
                                st.write(row['unit'])
                        else:
                            st.write("")

    # Submit Button
    if st.button("Submit"):
        # Check for empty inputs
        empty_inputs = []
        for key in st.session_state:
            if st.session_state[key] is None or (isinstance(st.session_state[key], str) and st.session_state[key].strip() == ""):
                if key == 'summary_data' or key == 'results_df':
                    pass
                else:
                    empty_inputs.append(key)

        if empty_inputs:
            st.error("Please fill in all inputs before proceeding")
        else:
            # Initialize lists to store results for each year
            years = list(range(st.session_state.current_year, 2061))
            benefit_to_cost_ratios = []
            results_data = []
            state_snapshots = []  # Store state at each timestep

            # Calculate base values
            percentage_slum_pop_current = (st.session_state.slum_pop / st.session_state.urban_pop) * 100
            gdp_per_capita = st.session_state.gdp / st.session_state.urban_pop
            
            # Pre-calculate arrays for all years
            n_years = [(year - st.session_state.current_year) / 10 for year in years]
            pop_array = [st.session_state.urban_pop * (1 + st.session_state.growth_rate/100) ** n for n in n_years]
            
            # Slum population array
            percentage_slum_pop_array = [max(percentage_slum_pop_current - 10, 0) for _ in years]
            slum_pop_array = [(pct / 100) * pop for pct, pop in zip(percentage_slum_pop_array, pop_array)]
            
            # Floating population array
            percentage_floating_pop_current = (st.session_state.floating_pop / st.session_state.urban_pop) * 100
            floating_pop_array = [(percentage_floating_pop_current / 100) * pop for pop in pop_array]
            
            # Households array
            household_ratio = st.session_state.urban_pop / st.session_state.urban_households
            urban_households_array = [pop / household_ratio for pop in pop_array]
            
            # Water connections array
            urban_households_tap_water_current = (st.session_state.tap_water_pct / 100) * st.session_state.urban_households
            urban_households_fhtc_array = [households - urban_households_tap_water_current for households in urban_households_array]
            
            # Sewer calculations array
            pop_connected_sewer_current = (st.session_state.current_sewer_pop / 100) * st.session_state.urban_pop
            length_sewer_per_person = (st.session_state.sewer_length * 1000) / pop_connected_sewer_current
            pop_connected_sewer_array = [(st.session_state.projected_sewer_pop / 100) * pop for pop in pop_array]
            sewer_network_array = [(length_sewer_per_person * pop) / 1000 for pop in pop_connected_sewer_array]
            gap_sewer_network_array = [network - st.session_state.sewer_length for network in sewer_network_array]
            
            # Treatment capacity array
            sewage_generated_array = [0.8 * pop * st.session_state.water_consumption / 1000000 for pop in pop_connected_sewer_array]
            gap_treatment_capacity_array = [max(0, sewage - st.session_state.stp_capacity) for sewage in sewage_generated_array]
            
            # FSTP calculations array
            households_septic_tanks_array = [households * (1 - st.session_state.projected_sewer_pop / 100) for households in urban_households_array]
            septage_treated_per_day_array = [households * st.session_state.septage_emptied_per_household / (st.session_state.desludging_frequency * 300) 
                                           for households in households_septic_tanks_array]

            # Loop through years for cost-benefit calculations
            for i, year in enumerate(years):
                present_value_total_cost = 0
                present_value_total_benefits = 0

                # Add capital costs only in investment year
                if year == st.session_state.investment_year:
                    # Water supply capital costs
                    capital_cost_piped_water = urban_households_fhtc_array[i] * st.session_state.fhtc_cost
                    
                    # Toilet capital costs
                    wc_ct = slum_pop_array[i] / st.session_state.persons_per_wc_ct
                    additional_wc_ct = wc_ct - st.session_state.comm_toilets
                    total_capital_cost_wc_ct = additional_wc_ct * st.session_state.comm_toilet_cost

                    wc_pt = floating_pop_array[i] / st.session_state.persons_per_wc_pt
                    additional_wc_pt = wc_pt - st.session_state.public_toilets
                    total_capital_cost_wc_pt = additional_wc_pt * st.session_state.public_toilet_cost

                    # Sewer and treatment capital costs
                    capital_cost_sewer_network = gap_sewer_network_array[i] * st.session_state.sewer_const_cost
                    capital_cost_additional_stp = gap_treatment_capacity_array[i] * st.session_state.stp_cost
                    cost_fstp_total = septage_treated_per_day_array[i] * st.session_state.fstp_cost

                    # Training costs
                    officials_capacity_building = (st.session_state.ulb_officials_trained / 100) * pop_array[i]
                    total_annual_cost_capacity_building = officials_capacity_building * st.session_state.training_cost
                    total_awareness_cost = pop_array[i] * st.session_state.awareness_cost
                    total_training_outreach_cost = total_annual_cost_capacity_building + total_awareness_cost

                    # Sum all capital costs
                    present_value_total_cost = (
                        capital_cost_piped_water + total_capital_cost_wc_ct + total_capital_cost_wc_pt +
                        capital_cost_sewer_network + capital_cost_additional_stp + cost_fstp_total +
                        total_training_outreach_cost
                    ) / ((1 + st.session_state.discount_rate/100) ** (year - st.session_state.current_year))

                # Add operating costs and benefits after investment year
                elif year > st.session_state.investment_year:
                    # Operating costs
                    annual_maint_sewer_network_total = gap_sewer_network_array[i] * st.session_state.sewer_maint_cost
                    annual_maint_stp_total = gap_treatment_capacity_array[i] * st.session_state.stp_maint_cost
                    annual_maint_fstp_total = septage_treated_per_day_array[i] * st.session_state.fstp_maint_cost
                    
                    present_value_total_cost = (
                        annual_maint_sewer_network_total + annual_maint_stp_total + 
                        annual_maint_fstp_total + total_training_outreach_cost
                    ) / ((1 + st.session_state.discount_rate/100) ** (year - st.session_state.current_year))

                    # Calculate individual benefit components
                    health_benefits = (st.session_state.disease_incidence * st.session_state.treatment_cost) + \
                                    (st.session_state.disease_incidence * st.session_state.transport_cost)
                    productivity_benefits = gdp_per_capita * st.session_state.working_age_pop / 100 * 5 * 8
                    recycled_water_benefits = st.session_state.recycled_water_value * sewage_generated_array[i] * 365 * 1000
                    tourism_benefits = st.session_state.tourism_contribution / 100 * gdp_per_capita * pop_array[i]

                    # Calculate present value of benefits
                    discount_factor = 1 / ((1 + st.session_state.discount_rate/100) ** (year - st.session_state.current_year))
                    present_value_total_benefits = (health_benefits + productivity_benefits + recycled_water_benefits + tourism_benefits) * discount_factor

                    # Store benefit components for pie chart
                    benefit_components = {
                        'Health Benefits': health_benefits * discount_factor,
                        'Productivity Benefits': productivity_benefits * discount_factor,
                        'Recycled Water Benefits': recycled_water_benefits * discount_factor,
                        'Tourism Benefits': tourism_benefits * discount_factor
                    }

                # Calculate benefit-to-cost ratio (avoid division by zero)
                benefit_to_cost_ratio = present_value_total_benefits / present_value_total_cost if present_value_total_cost != 0 else 0

                # Store state snapshot
                state_snapshot = {
                    'pop_in_target_year': pop_array[i],
                    'slum_pop_in_target_year': slum_pop_array[i],
                    'floating_pop_in_target_year': floating_pop_array[i],
                    'urban_households_in_target_year': urban_households_array[i],
                    'sewage_generated_in_target_year': sewage_generated_array[i],
                    'benefit_components': benefit_components if year > st.session_state.investment_year else None,
                    'year': year
                }
                state_snapshots.append(state_snapshot)

                # Store results
                results_data.append({
                    "Year": year,
                    "Benefit-to-Cost Ratio": benefit_to_cost_ratio,
                    "Benefits_Per_Person": present_value_total_benefits / st.session_state.urban_pop,
                    "Costs_Per_Person": present_value_total_cost / st.session_state.urban_pop,
                    "Total_Benefits": present_value_total_benefits,
                    "Total_Costs": present_value_total_cost
                })

            # Create DataFrame from results
            st.session_state.results_df = pd.DataFrame(results_data)
            st.session_state.state_snapshots = state_snapshots
            st.session_state.calculations_done = True

            # Switch to Dashboard tab
            script_placeholder = st.empty()
            html(f"<script>{switch_tab(2)}</script>", height=0)
            time.sleep(0.1)
            script_placeholder.empty()

with tab3:
    if not st.session_state.get('calculations_done', False):
        st.warning('Please click "Submit" on Input Parameters tab')
    else:
        st.subheader("Dashboard")
        
        # Create figure with secondary y-axis
        fig = px.line(st.session_state.results_df, x="Year", y=["Benefits_Per_Person", "Costs_Per_Person"])
        
        # Add benefit-to-cost ratio on secondary y-axis
        fig.add_scatter(x=st.session_state.results_df["Year"], 
                    y=st.session_state.results_df["Benefit-to-Cost Ratio"],
                    name="Benefit-to-Cost Ratio",
                    yaxis="y2")

        # Update layout with secondary y-axis and styling
        fig.update_layout(
            title="Return on WASH Investment",
            xaxis_title="Year",
            yaxis_title=f"{st.session_state.currency}/person",
            yaxis2=dict(
                title="Benefit-to-Cost Ratio",
                overlaying="y",
                side="right"
            ),
            xaxis=dict(
                dtick=10  # Set x-axis tick interval to 10 years
            ),
            showlegend=True,
            hovermode='x unified'
        )

        # Update line colors and add markers
        fig.data[0].update(line_color='green', name='Benefits', mode='lines+markers')  # Benefits line
        fig.data[1].update(line_color='grey', name='Costs', mode='lines+markers')      # Costs line
        fig.data[2].update(line_color='blue', mode='lines+markers')                    # Ratio line
        st.plotly_chart(fig)

        # Create pie charts of benefit and cost components
        if st.session_state.state_snapshots:
            # Get available years from snapshots
            summary_years = [2030, 2040, 2050, 2060]
            years = list(range(st.session_state.current_year, 2061))
            
            # Year selector
            selected_year = st.selectbox(
                "Select year to view cost and benefit breakdown:",
                summary_years,
                index=len(summary_years)-1  # Default to latest year
            )

            # Get index corresponding to selected year
            year_index = years.index(selected_year)

            col1, col2 = st.columns(2)
            
            with col1:
                # Get benefit components for selected year
                selected_benefits = None
                for snapshot in st.session_state.state_snapshots:
                    print(snapshot.keys())
                    if snapshot['year'] == selected_year and snapshot.get('benefit_components'):
                        selected_benefits = snapshot['benefit_components']
                        break
                
                if selected_benefits:
                    fig_benefits = px.pie(
                        values=list(selected_benefits.values()),
                        names=list(selected_benefits.keys()),
                        title=f"Distribution of Net Present Value Benefits ({selected_year})",
                        color_discrete_sequence=['#004d40', '#00695c', '#00796b', '#00897b', '#009688', '#26a69a', '#4db6ac']  # Shades of green
                    )
                    fig_benefits.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_benefits)

            with col2:
                # Get cost components for selected year
                selected_costs = None
                for snapshot in st.session_state.state_snapshots:
                    if snapshot['year'] == selected_year and snapshot.get('cost_components'):
                        selected_costs = snapshot['cost_components']
                        break
                
                if selected_costs:
                    fig_costs = px.pie(
                        values=list(selected_costs.values()),
                        names=list(selected_costs.keys()),
                        title=f"Distribution of Net Present Value Costs ({selected_year})", 
                        color_discrete_sequence=['#b71c1c', '#c62828', '#d32f2f', '#e53935', '#f44336', '#ef5350', '#e57373']  # Shades of red
                    )
                    fig_costs.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_costs)

with tab4:
    if not st.session_state.get('calculations_done', False):
        st.warning('Please click "Submit" on Input Parameters tab')
    else:
        # Add toggle for absolute vs per capita values
        show_per_capita = st.checkbox("Show per capita values", value=False)
        
        # Create summary data using the stored results
        summary_years = [2030, 2040, 2050, 2060]
        summary_data = []
        
        for year in summary_years:
            # Get matching rows for this year
            year_rows = st.session_state.results_df[st.session_state.results_df['Year'] == year]
            
            # Only add data if we have results for this year
            if not year_rows.empty:
                year_data = year_rows.iloc[0]
                
                if show_per_capita:
                    row = {
                        'Year': year,
                        'Benefits': year_data['Benefits_Per_Person'],
                        'Costs': year_data['Costs_Per_Person'],
                        'Ratio': year_data['Benefit-to-Cost Ratio']
                    }
                else:
                    row = {
                        'Year': year,
                        'Benefits': year_data['Total_Benefits'],
                        'Costs': year_data['Total_Costs'],
                        'Ratio': year_data['Benefit-to-Cost Ratio']
                    }
                summary_data.append(row)
            
        # Create and display table if we have data
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Display summary table
            st.table(summary_df.style.format({
                'Benefits': '{:,.2f}',
                'Costs': '{:,.2f}',
                'Ratio': '{:,.2f}'
            }))
        else:
            st.warning("No data available for summary years")


with tab5:
    st.write("### Sanitation Variables Glossary")
    
    # Import documentation.html
    with open('documentation.html', 'r') as f:
        doc_content = f.read()
        
    # Display HTML content directly using streamlit components
    components.html(doc_content, height=1200, scrolling=True)
    
with tab6:
    st.write("Help")