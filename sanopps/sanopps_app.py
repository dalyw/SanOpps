import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from streamlit.components import v1 as components
import time
import json
import os

# Load constants from CSV
constants = pd.read_csv("https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/params.csv", index_col="Indicator")

# Extract constants
rate_decadal_growth = constants.loc["Rate of decadal growth of population (in percentage)", "Value"]
fhtc_cost_per_household = constants.loc["FHTC cost per household", "Value"]
persons_per_wc_ct = constants.loc["Number of persons in slums per WC(CT)", "Value"]
# wc_ct_current = constants.loc["Number of WC(CT) (current)", "Value"]
capital_cost_wc_ct = constants.loc["Capital cost of construction per WC(CT)", "Value"]
persons_per_wc_pt = constants.loc["Number of persons (floating population) per WC(PT)", "Value"]
wc_pt_current = constants.loc["Number of WC(PT)(current)", "Value"]
capital_cost_wc_pt = constants.loc["Capital cost of construction per WC(PT)", "Value"]
cost_sewer_network = constants.loc["Cost of laying sewerage network", "Value"]
annual_maintenance_sewer_network = constants.loc["Annual Maintenance cost for Sewerage Network per KM", "Value"]
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

city_default_data = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/city_default_data.csv')

# Title of the application
st.title("SanOpps: The WASH Cost-Benefit Analysis Tool for Local Government")

# Create tabs for input and results
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
    
    config_name = st.text_input("Enter name for this configuration:")
    if config_name:
        with open(f'configs/{config_name}.json', 'w') as f:
            json.dump(config, f)
        st.success(f"Configuration saved as {config_name}")

def load_config():
    """Load configuration from JSON file"""
    config_files = [f for f in os.listdir('configs') if f.endswith('.json')]
    if config_files:
        selected_config = st.selectbox("Select configuration to load:", config_files)
        if selected_config:
            with open(f'configs/{selected_config}', 'r') as f:
                config = json.load(f)
            # Update session state with loaded config
            for key, value in config.items():
                st.session_state[key] = value
            st.success(f"Loaded configuration: {selected_config}")
    else:
        st.info("No saved configurations found")

with tab1:
    col1, col2 = st.columns([7,3], gap="large")
    with col1:
        st.write("This interactive tool is designed to support policy-makers, researchers, and stakeholders in assessing the economic viability and social impact of Water, Sanitation, and Hygiene (WASH) initiatives. It provides a comprehensive analysis of the present and future costs and benefits associated with implementing WASH projects, and helps identify the highest value-generating investments.")

        st.subheader("Why use SanOpps?")
        st.write("SanOpps provides a localized understanding of a global trend: that investment in WASH drives economic growth. The dashboard lays out the return on investment potential for WASH in your city.")

        st.subheader("SanOpps Features")

        # generating mermaid flowchart & class breakdown, using example from https://discuss.streamlit.io/t/st-markdown-does-not-render-mermaid-graphs/25576/9
        def mermaid(code: str) -> None:
            components.html(
                f"""
                <pre class="mermaid" style="width: 100%; height: 600px;">
                    {code}
                </pre>

                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ startOnLoad: true, theme: 'neutral', flowchart: {{ htmlLabels: true }}, fontSize: 18 }});
                </script>
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
                
    with col2:
        st.subheader("What is Water, Sanitation, and Hygiene (WASH)?")
        st.write("*WASH initiatives are aimed at improving access to clean Water, Sanitation, and Hygiene practices, particularly in low- and middle-income areas. Investing in WASH infrastructure is essential to improve public health, reduce poverty, promote equitable access to essential services, and enhance socio-economic development.*")

    # Add "Next" button to go to Input Parameters tab
    if st.button("Next: Input City Data"):
        # Create placeholder for script
        script_placeholder = st.empty()
        # Add script to switch tab
        html(f"<script>{switch_tab(1)}</script>", height=0)
        # Sleep briefly to allow script to execute
        time.sleep(0.1)
        # Clear the script
        script_placeholder.empty()

# Load the CSV files
input_labels = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/input_labels.csv')

def generate_inputs():
    # Configuration management
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Current Configuration"):
            save_config()
    with col2:
        if st.button("Load Configuration"):
            load_config()
            
    # Location selection first
    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.selectbox("Select Country", list(city_default_data['Country'].unique())+['Other'], key="country")
    with col2:
        state = st.selectbox("Select State/Province", list(city_default_data[city_default_data['Country']==country]['State/Province'].unique())+['Other'], key="state")
    with col3:
        # Store previous city value to detect changes
        prev_city = st.session_state.get('prev_city', None)
        city = st.selectbox("Select City", list(city_default_data[(city_default_data['Country']==country) & (city_default_data['State/Province']==state)]['City'].unique())+['Other'], key="city")
        
        # Check if city selection changed
        if city != prev_city and city in city_default_data['City'].values:
            city_data = city_default_data[city_default_data['City'] == city].iloc[0]
            # Update all session state values with new city data
            st.session_state.currency = city_data['Currency']
            st.session_state.urban_pop = city_data['Urban Population']
            st.session_state.current_year = city_data['Current Year']
            st.session_state.growth_rate = city_data['Rate of Decadal Growth (%)']
            st.session_state.target_year = city_data['Target Year']
            st.session_state.inflation = city_data['Inflation Rate (%)']
            # Store current city as previous
            st.session_state.prev_city = city

    # Pre-populate fields if city exists in data
    if city in city_default_data['City'].values:
        city_data = city_default_data[city_default_data['City'] == city].iloc[0]
        default_currency = city_data['Currency']
        default_population = city_data['Urban Population']
        default_year = city_data['Current Year']
        default_growth = city_data['Rate of Decadal Growth (%)']
        default_target = city_data['Target Year']
        default_inflation = city_data['Inflation Rate (%)']
    else:
        default_currency = ""
        default_population = None
        default_year = None
        default_growth = None
        default_target = None
        default_inflation = None

    # Generate inputs row by row
    for _, row in input_labels.iterrows():

        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write(row['label'])
        with col2:
            if row['key'] in ['currency', 'co_treat_avail', 'fstp_avail', 'co_treat_proposed']:
                options = ["INR", "USD", "EUR"] if row['key'] == 'currency' else ["NO", "YES"]
                st.selectbox("", options, key=row['key'], label_visibility="collapsed")
            else:
                st.number_input("", value=st.session_state.get(row['key'], float(row['default_value'])), 
                              label_visibility="collapsed", key=row['key'])
        with col3:
            print(row['unit'])
            if row['unit']:
                if 'currency' in str(row['unit']):
                    st.write(row['unit'].replace('currency', st.session_state.currency))
                else:
                    st.write(row['unit'])
            else:
                st.write("")

with tab2:
    st.markdown("""
    Please Enter Current Year Data to Ensure Precise Cost and Benefit Estimations
    """)
    # Use the function to generate inputs
    with st.expander("Input Parameters", expanded=True):
        generate_inputs()
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

            # st.session_state.current_year=int(st.session_state.current_year)      
            if empty_inputs:
                st.error("Please fill in all inputs before proceeding")
            else:
                # Initialize lists to store results for each year
                years = []
                benefit_to_cost_ratios = []
                results_data = []

                
                # Loop through the next 30 years
                for year in range(st.session_state.current_year, st.session_state.current_year + 31):
                    n = (year - st.session_state.current_year) / 10
                    pop_projected = st.session_state.urban_pop * (1 + rate_decadal_growth / 100) ** n
                    pop_additional = pop_projected - st.session_state.urban_pop

                    percentage_slum_pop_current = (st.session_state.slum_pop / st.session_state.urban_pop) * 100
                    percentage_slum_pop_projected = max(percentage_slum_pop_current - 10, 0)
                    slum_pop_projected = (percentage_slum_pop_projected / 100) * pop_projected

                    percentage_floating_pop_current = (st.session_state.floating_pop / st.session_state.urban_pop) * 100
                    floating_pop_projected = (percentage_floating_pop_current / 100) * pop_projected

                    urban_households_projected = pop_projected / (st.session_state.urban_pop / st.session_state.urban_households)
                    urban_households_tap_water_current = (st.session_state.tap_water_pct / 100) * st.session_state.urban_households
                    urban_households_fhtc = urban_households_projected - urban_households_tap_water_current
                    capital_cost_piped_water = urban_households_fhtc * st.session_state.fhtc_cost

                    wc_ct_projected = slum_pop_projected / persons_per_wc_ct
                    additional_wc_ct = wc_ct_projected - st.session_state.comm_toilets
                    total_capital_cost_wc_ct = additional_wc_ct * st.session_state.comm_toilet_cost

                    wc_pt_projected = floating_pop_projected / persons_per_wc_pt
                    additional_wc_pt = wc_pt_projected - st.session_state.public_toilets
                    total_capital_cost_wc_pt = additional_wc_pt * st.session_state.public_toilet_cost

                    pop_connected_sewer_current = (st.session_state.current_sewer_pop / 100) *st.session_state.urban_pop
                    length_sewer_per_person = (st.session_state.sewer_length * 1000) / pop_connected_sewer_current
                    pop_connected_sewer_projected = (st.session_state.projected_sewer_pop / 100) * pop_projected
                    sewer_network_projected = (length_sewer_per_person * pop_connected_sewer_projected) / 1000
                    gap_sewer_network = sewer_network_projected - st.session_state.sewer_length
                    capital_cost_sewer_network = gap_sewer_network * st.session_state.sewer_const_cost
                    annual_maint_sewer_network_total = gap_sewer_network * st.session_state.sewer_maint_cost

                    pop_connected_sewer_projected = (st.session_state.projected_sewer_pop / 100) * pop_projected * 0.8
                    sewage_generated_projected = 0.8 * pop_connected_sewer_projected * st.session_state.water_consumption / 1000000
                    gap_treatment_capacity = max(0, sewage_generated_projected - st.session_state.stp_capacity)
                    capital_cost_additional_stp = gap_treatment_capacity * st.session_state.stp_cost
                    annual_maint_stp_total = gap_treatment_capacity * st.session_state.stp_maint_cost

                    households_septic_tanks = urban_households_projected * (1 - st.session_state.projected_sewer_pop / 100)
                    septage_treated_per_day = households_septic_tanks * septage_emptied_per_household / (desludging_frequency * 300)
                    cost_co_treatment_total = septage_treated_per_day * cost_co_treatment
                    cost_fstp_total = septage_treated_per_day * st.session_state.fstp_cost
                    annual_maint_fstp_total = septage_treated_per_day * st.session_state.fstp_maint_cost

                    officials_capacity_building = (ulb_officials_trained / 100) * pop_projected
                    total_annual_cost_capacity_building = officials_capacity_building * st.session_state.training_cost
                    total_annual_cost_public_awareness = pop_projected * st.session_state.awareness_cost
                    total_training_outreach_cost = total_annual_cost_capacity_building + total_annual_cost_public_awareness

                    gdp_per_capita = st.session_state.gdp / st.session_state.urban_pop

                    # Calculate present value of total costs and benefits
                    present_value_total_cost = (
                        capital_cost_piped_water + total_capital_cost_wc_ct + total_capital_cost_wc_pt +
                        capital_cost_sewer_network + capital_cost_additional_stp + cost_fstp_total +
                        total_training_outreach_cost
                    ) / ((1 + discount_rate/100) ** (year - st.session_state.current_year))

                    present_value_total_benefits = (
                        (st.session_state.disease_incidence * st.session_state.treatment_cost) + (st.session_state.disease_incidence * st.session_state.transport_cost) +
                        (gdp_per_capita * st.session_state.working_age_pop / 100 * 5 * 8) +  # Productive time loss savings
                        (st.session_state.recycled_water_value * sewage_generated_projected * 365 * 1000) +  # Recycled water benefits
                        (st.session_state.tourism_contribution / 100 * gdp_per_capita * pop_projected)  # Tourism benefits
                    ) / ((1 + discount_rate/100) ** (year - st.session_state.current_year))

                    # Calculate benefit-to-cost ratio
                    benefit_to_cost_ratio = present_value_total_benefits / present_value_total_cost

                    # Store results
                    results_data.append({
                        "Year": year,
                        "Benefit-to-Cost Ratio": benefit_to_cost_ratio,
                        "Benefits_Per_Person": present_value_total_benefits /st.session_state.urban_pop,
                        "Costs_Per_Person": present_value_total_cost /st.session_state.urban_pop,
                        "Total_Benefits": present_value_total_benefits,
                        "Total_Costs": present_value_total_cost
                    })

                # Create DataFrame from results
                st.session_state.results_df = pd.DataFrame(results_data)
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
            
        # Only create and display table if we have data
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

definitions = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/sanitation_variables.csv')

with tab5:
    st.write("### Sanitation Variables Glossary")
    
    # Group by Variable Type and Description, combining Variable Names
    grouped_definitions = definitions.groupby(['Variable Type', 'Description'])['Variable Name'].agg(lambda x: ', '.join(x)).reset_index()
    
    # Create an AgGrid with custom column configurations
    st.write("""
    <style>
    .merged-cell {
        background-color: #f0f2f6;
        border-bottom: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display as HTML table with merged cells
    html_table = grouped_definitions.to_html(index=False, classes='dataframe', escape=False)
    
    # Add custom CSS for table styling
    st.markdown("""
    <style>
    table.dataframe {
        width: 100%;
        margin-bottom: 1rem;
        border-collapse: collapse;
    }
    table.dataframe th, table.dataframe td {
        padding: 8px;
        border: 1px solid #ddd;
    }
    table.dataframe th {
        background-color: #f8f9fa;
    }
    table.dataframe tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    

with tab6:
    st.write("Help")