import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import time
import json
import os
import requests
import copy
import plotly.graph_objects as go
from helpers import *

# Function to initialize session state
def initialize_session_state(keys, default_values):
    for key, default_value in zip(keys, default_values):
        if key not in st.session_state:
            st.session_state[key] = default_value

read_local = False
if read_local:
    city_default_data = pd.read_csv('data/city_default_data.csv')
    input_labels = pd.read_csv('data/input_labels.csv')
    definitions = pd.read_csv('data/definitions.csv')
    params = pd.read_csv('data/params.csv')
    with open('sanopps/documentation.html', 'r') as f:
        doc_content = f.read()
else:
    city_default_data = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/city_default_data.csv')
    input_labels = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/input_labels.csv')
    definitions = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/definitions.csv')
    params = pd.read_csv("https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/params.csv")
    doc_content = requests.get('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/sanopps/documentation.html').text

# add params to st.session_state
for _, row in params.iterrows():
    if pd.notna(row['varname']): 
        st.session_state[row['varname']] = row['value']

st.title("SanOpps: The WASH Cost-Benefit Analysis Tool for Local Government")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Home Page", "Input Parameters", "Dashboard", "Summary", "Definitions", "Help"])

# Initialize session state for calculations
initialize_session_state(['calculations_done', 'results_df', 'summary_data'], [False, None, None])

# Create configs directory if it doesn't exist
if not os.path.exists('configs'):
    os.makedirs('configs')
# Function to handle input generation
def generate_inputs(input_labels, category, input_type):
    inputs = input_labels[(input_labels['category'] == category) & (input_labels['type'] == input_type)]
    
    # Currency conversion rates (hardcoded for now, could be made dynamic)
    conversion_rates = {
        'INR': 1,
        'USD': 83.28,  # 1 USD = 83.28 INR
        'EUR': 89.13   # 1 EUR = 89.13 INR
    }
    
    for _, row in inputs.iterrows():
        name_col, input_col, units_col, percent_col = st.columns([1, 1, 1, 1])
        with name_col:
            st.write(row['label'])
        with input_col:
            key = row['key']
            if key not in st.session_state:
                default_value = float(row['default_value']) if row['value_type'] == 'float' else int(row['default_value']) if row['value_type'] == 'int' else str(row['default_value'])
                st.session_state[key] = default_value
                if pd.notna(row['percent_option']):
                    st.session_state[key+"_percent"] = default_value/st.session_state.get(row['percent_option'], 1)*100 if row['unit'] != '%' else default_value
            
            if key in ['currency', 'co_treat_avail', 'fstp_avail', 'co_treat_proposed']:
                options = ["INR", "USD", "EUR"] if key == 'currency' else ["NO", "YES"]
                selected = st.selectbox("", options, key=f"select_{key}", label_visibility="collapsed")
                if key == 'currency' and selected != st.session_state.get('prev_currency'):
                    # Convert all monetary values when currency changes
                    if 'prev_currency' in st.session_state:
                        old_rate = conversion_rates[st.session_state.prev_currency]
                        new_rate = conversion_rates[selected]
                        conversion_factor = old_rate / new_rate
                        
                        # Convert all monetary inputs
                        for monetary_key in st.session_state:
                            if isinstance(st.session_state[monetary_key], (int, float)):
                                # Check if the key corresponds to a monetary value
                                monetary_label = input_labels[input_labels['key'] == monetary_key]
                                if not monetary_label.empty and 'currency' in str(monetary_label.iloc[0]['unit']):
                                    st.session_state[monetary_key] *= conversion_factor
                    
                    st.session_state.prev_currency = selected
            else:
                if pd.notna(row['percent_option']):
                    percent_toggle = st.session_state.get(f"{key}_percent_toggle", row['unit'] == '%')
                    if percent_toggle:
                        value = st.number_input(
                            "",
                            value=st.session_state[key+"_percent"],
                            label_visibility="collapsed",
                            key=f"percent_{key}"
                        )
                        st.session_state[key+"_percent"] = value
                        st.session_state[key] = value * st.session_state.get(row['percent_option'], 0) / 100 if row['unit'] != '%' else value
                    else:
                        value = st.number_input("", value=st.session_state[key], label_visibility="collapsed", key=f"direct_{key}")
                        st.session_state[key] = value
                        st.session_state[key+"_percent"] = value/st.session_state.get(row['percent_option'], 1)*100
                else:
                    value = st.number_input("", value=st.session_state[key], label_visibility="collapsed", key=f"input_{key}")
                    st.session_state[key] = value
        with units_col:
            if pd.notna(row['percent_option']):
                if st.session_state.get(f"{key}_percent_toggle", row['unit'] == '%'):
                    st.write(f"% of {row['percent_option']}")
                else:
                    # Get the unit of the referenced variable
                    ref_var = input_labels[input_labels['key'] == row['percent_option']]
                    if not ref_var.empty:
                        ref_var_unit = ref_var.iloc[0]['unit']
                        st.write(ref_var_unit)
                    else:
                        st.write("")
            elif row['unit']:
                st.write(row['unit'].replace('currency', st.session_state.currency) if 'currency' in str(row['unit']) else row['unit'])
            else:
                st.write("")
        with percent_col:
            if pd.notna(row['percent_option']):
                st.checkbox(f"Input as %", key=f"{key}_percent_toggle", value=row['unit']=='%')
            else:
                st.write("")

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
    filename = st.text_input("Enter filename (without .json extension)", "sanopps_config", label="Configuration filename")
    
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
    uploaded_file = st.file_uploader("Upload configuration file", type=['json'], label="Configuration file")
    if uploaded_file is not None:
        config = json.load(uploaded_file)
        # Update session state with loaded config
        for key, value in config.items():
            st.session_state[key] = value
        st.success("Configuration loaded successfully")  

with tab1:
    # Use container to force full height
    with st.container():
        col1, col2 = st.columns([7.5,2.5], gap="medium")
        with col1:
            st.write("This interactive tool is designed to support policy-makers, researchers, and stakeholders in assessing the economic viability and social impact of Water, Sanitation, and Hygiene (WASH) initiatives. It provides a comprehensive analysis of the present and future costs and benefits associated with implementing WASH projects, and helps identify the highest value-generating investments.")

            st.subheader("Why use SanOpps?")
            st.write("SanOpps provides a localized understanding of a global trend: that investment in WASH drives economic growth. The dashboard lays out the return on investment potential for WASH in your city.")

            st.image("data/sanopps_phases.png", use_container_width=True, width=100)

            st.subheader("SanOpps Features")
            
            # Render mermaid diagram with fixed height container
            mermaid_code = """
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
            """

            components.html(
                f"""
                <div style="height: 700px; overflow: visible;">
                    <pre class="mermaid">
                        {mermaid_code}
                    </pre>
                    <script type="module">
                        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                        mermaid.initialize({{ 
                            startOnLoad: true,
                            theme: 'neutral',
                            flowchart: {{ htmlLabels: true }},
                            fontSize: 18,
                            securityLevel: 'loose'
                        }});
                    </script>
                </div>
                """,
                height=700,
            )

        with col2:
            st.subheader("*What is Water, Sanitation, and Hygiene (WASH)?*", anchor=False, help=None)
            st.image("data/sanopps_wash.png", use_container_width=True, width=100)
            st.write("*WASH initiatives are aimed at improving access to clean Water, Sanitation, and Hygiene practices, particularly in low- and middle-income areas. Investing in WASH infrastructure is essential to improve public health, reduce poverty, promote equitable access to essential services, and enhance socio-economic development.*")
    st.write("---")
    st.subheader("Developers")
    logo_col1, logo_col2, logo_col3 = st.columns(3)
    
    with logo_col1:
        st.image("data/ecosan.jpeg", use_container_width=True, width=100)
    
    with logo_col2:
        st.image("data/mit.png", use_container_width=True, width=100)
        
    with logo_col3:
        st.image("data/wto.png", use_container_width=True, width=100)

    # Add "Next" button to go to Input Parameters tabs
    if st.button("Next: Input City Data"):
        script_placeholder = st.empty()
        components.html(f"<script>{switch_tab(1)}</script>", height=0)
        time.sleep(0.1)
        script_placeholder.empty()
        
with tab2:
    st.markdown("Please Enter Current Year Data to Ensure Precise Cost and Benefit Estimations")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Current Configuration"):
            save_config()
    with col2:
        if st.button("Load Configuration"):
            load_config()

    country_col, state_col, city_col = st.columns(3)
    with country_col:
        country = st.selectbox("Select Country", list(city_default_data['Country'].unique()) + ['Other'], key="country")
    with state_col:
        state = st.selectbox("Select State/Province", list(city_default_data[city_default_data['Country'] == country]['State/Province'].unique()) + ['Other'], key="state")
    with city_col:
        prev_city = st.session_state.get('prev_city', None)
        city = st.selectbox("Select City", list(city_default_data[(city_default_data['Country'] == country) & (city_default_data['State/Province'] == state)]['City'].unique()) + ['Other'], key="city")
        if city != prev_city and city in city_default_data['City'].values:
            city_data = city_default_data[city_default_data['City'] == city].iloc[0]
            keys = ['currency', 'urban_pop', 'current_year', 'growth_rate', 'target_year', 'inflation']
            for key in keys:
                if key in city_data:
                    st.session_state[key] = city_data[key]
            st.session_state.prev_city = city

    categories = input_labels['category'].unique()
    for category in categories:
        st.subheader(category)
        category_inputs = input_labels[input_labels['category'] == category]
        
        # Handle required inputs
        required_inputs = category_inputs[category_inputs['type'] == 'user_input']
        for _, row in required_inputs.iterrows():
            generate_inputs(input_labels[input_labels['key'] == row['key']], category, 'user_input')
        
        # Handle optional inputs in expander
        with st.expander(f"Optional {category} Parameters"):
            optional_inputs = category_inputs[category_inputs['type'] == 'optional_input']
            for _, row in optional_inputs.iterrows():
                generate_inputs(input_labels[input_labels['key'] == row['key']], category, 'optional_input')

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
            benefit_to_cost_ratios, results_data, state_snapshots = [], [], []

            # Calculate base values
            gdp = st.session_state.gdp_per_capita * st.session_state.urban_pop
            hourly_monetary_income = st.session_state.gdp_per_capita/(8*5*52) # 8 hours per day, 5 days per week, 52 weeks per year

            # Population projections
            n_years = [(year - st.session_state.current_year) / 10 for year in years]

            
            # Population arrays - slum population decreases by 10% by target year
            pop_array = [st.session_state.urban_pop * (1 + st.session_state.growth_rate/100) ** n for n in n_years]
            percentage_slum_pop_current = st.session_state.slum_pop / st.session_state.urban_pop
            percentage_floating_pop_current = st.session_state.floating_pop / st.session_state.urban_pop 
            percentage_slum_pop_array = [max(percentage_slum_pop_current - 0.1, 0) for _ in years]
            slum_pop_array = [pct * pop for pct, pop in zip(percentage_slum_pop_array, pop_array)]
            floating_pop_array = [percentage_floating_pop_current * pop for pop in pop_array]
            household_ratio = st.session_state.urban_pop / st.session_state.urban_households
            urban_households_array = [pop / household_ratio for pop in pop_array]
            
            # Water connections array - target 100% FHTC coverage
            # urban_households_with_fhtc = (st.session_state.urban_households_with_fhtp_percent/100) * st.session_state.urban_households
            urban_households_without_fhtc = [households - st.session_state.urban_households_with_fhtp for households in urban_households_array]

            # Toilet calculations - 30 persons per WC as per SBM 2.0
            # persons_per_wc = 30
            ct_array = [slum_pop / st.session_state.persons_per_wc for slum_pop in slum_pop_array]
            pt_array = [floating_pop / st.session_state.persons_per_pt for floating_pop in floating_pop_array]
            additional_ct_array = [ct - st.session_state.comm_toilets * st.session_state.wc_per_ct for ct in ct_array] # Assuming 20 WCs per CT block
            additional_pt_array = [pt - st.session_state.public_toilets * st.session_state.wc_per_ct for pt in pt_array]

            # Sewer calculations array - maintain current coverage %
            pop_connected_sewer_array = [(st.session_state.urban_households_with_sewer_percent/100) * pop for pop in pop_array]
            sewer_length_per_person = st.session_state.sewer_length / ((st.session_state.urban_households_with_sewer_percent/100) * st.session_state.urban_pop)
            sewer_network_array = [(pop * sewer_length_per_person) / 1000 for pop in pop_connected_sewer_array] # Convert m to km
            gap_sewer_network_array = [max(0, network - st.session_state.sewer_length) for network in sewer_network_array]
            
            # Treatment capacity array - 80% of water consumption becomes sewage
            sewage_generated_array = [0.8 * pop * st.session_state.water_consumption / 1000000 for pop in pop_connected_sewer_array]
            gap_treatment_capacity_array = [max(0, sewage - st.session_state.stp_capacity) for sewage in sewage_generated_array]
            
            # FSTP calculations array
            households_septic_tanks_array = [households * (1 - st.session_state.urban_households_with_sewer_percent/100) for households in urban_households_array]
            septage_treated_per_day_array = [(households * st.session_state.septage_emptied_per_household) / (st.session_state.desludging_frequency * 300) for households in households_septic_tanks_array] # 3KL per household, 10 year desludging, 300 working days
            # Initialize component dictionaries
            
            cost_components = dict.fromkeys([
                'Tap Water Supply',
                'Community Toilets', 
                'Public Toilets',
                'Sewer',
                'STP',
                'Fecal Sludge Treatment Plant',
                'Training',
                'Public Awareness'
            ], 0)

            benefit_components = dict.fromkeys([
                'Reduced Healtcare Costs',
                'Productivity from Healthcare',
                'Time Saved from Water Collection', 
                'Time Saved from Sanitation Access',
                'Recycled Water',
                'Tourism'
            ], 0)

            cumulative_benefit_components = copy.deepcopy(benefit_components)
            cumulative_cost_components = copy.deepcopy(cost_components)
            cumulative_present_value_total_cost = 0
            cumulative_present_value_total_benefit = 0

            # Loop through years for cost-benefit calculations
            for i, year in enumerate(years):
                present_value_total_cost = 0
                present_value_total_benefits = 0
                discount_factor = 1 / ((1 + st.session_state.discount_rate/100) ** (year - st.session_state.current_year))

                # Add capital costs only in investment year
                if year == st.session_state.investment_year:
                    # Water supply capital costs
                    capital_cost_piped_water = urban_households_without_fhtc[i] * st.session_state.fhtc_cost
                    
                    # Toilet capital costs
                    total_capital_cost_ct = additional_ct_array[i] * st.session_state.capital_cost_wc
                    total_capital_cost_pt = additional_pt_array[i] * st.session_state.capital_cost_wc

                    # Sewer and treatment capital costs
                    # Determine sewer length per person based on population
                    if pop_array[i] <= 20000:
                        sewer_length_per_person = st.session_state.sewer_length_small
                    elif pop_array[i] <= 100000:
                        sewer_length_per_person = st.session_state.sewer_length_medium
                    else:
                        sewer_length_per_person = st.session_state.sewer_length_large
                        
                    # Recalculate sewer network array with new length per person
                    sewer_network = (pop_connected_sewer_array[i] * sewer_length_per_person) / 1000 # Convert m to km
                    gap_sewer_network = max(0, sewer_network - st.session_state.sewer_length)
                    capital_cost_sewer_network = max(0, gap_sewer_network * st.session_state.cost_sewer_network)
                    capital_cost_additional_stp = max(0, gap_treatment_capacity_array[i] * st.session_state.stp_cost)
                    
                    # FSTP costs
                    if st.session_state.co_treat_avail == "NO":
                        cost_fstp_total = max(0, septage_treated_per_day_array[i] * st.session_state.cost_fstp) / 1000
                    else:
                        cost_fstp_total = max(0, septage_treated_per_day_array[i] * st.session_state.cost_co_treatment) / 1000

                    # Training costs
                    officials_capacity_building = (st.session_state.percent_ulb_officials_trained/100) * pop_array[i]
                    total_annual_cost_capacity_building = max(0, officials_capacity_building * st.session_state.annual_cost_capacity_building)

                    # Awareness costs
                    total_awareness_cost = max(0, pop_array[i] * st.session_state.awareness_cost)

                    present_value_total_cost = (
                        capital_cost_piped_water + total_capital_cost_ct + total_capital_cost_pt +
                        capital_cost_sewer_network + capital_cost_additional_stp + cost_fstp_total +
                        total_awareness_cost + total_annual_cost_capacity_building
                    ) * discount_factor

                    cumulative_present_value_total_cost = present_value_total_cost

                # Add operating costs and benefits after investment year
                elif year > st.session_state.investment_year:
                    # Operating costs
                    annual_maint_sewer_network_total = max(0, gap_sewer_network_array[i] * st.session_state.sewer_maint_cost)
                    annual_maint_stp_total = max(0, gap_treatment_capacity_array[i] * st.session_state.stp_maint_cost)
                    annual_maint_fstp_total = max(0, septage_treated_per_day_array[i] * st.session_state.fstp_maint_cost) / 1000
                    
                    discount_factor = 1 / ((1 + st.session_state.discount_rate/100) ** (year - st.session_state.current_year))
                    
                    present_value_total_cost = (
                        annual_maint_sewer_network_total + annual_maint_stp_total + 
                        annual_maint_fstp_total + total_awareness_cost + total_annual_cost_capacity_building
                    ) * discount_factor

                    # Store cost components
                    cost_components = {
                        'Tap Water Supply': max(0, capital_cost_piped_water * discount_factor if year == st.session_state.investment_year else 0),
                        'Community Toilets': max(0, total_capital_cost_ct * discount_factor if year == st.session_state.investment_year else 0),
                        'Public Toilets': max(0, total_capital_cost_pt * discount_factor if year == st.session_state.investment_year else 0),
                        'Sewer': max(0, (capital_cost_sewer_network * discount_factor if year == st.session_state.investment_year else 0) + annual_maint_sewer_network_total * discount_factor),
                        'STP': max(0, (capital_cost_additional_stp * discount_factor if year == st.session_state.investment_year else 0) + annual_maint_stp_total * discount_factor),
                        'Fecal Sludge Treatment Plant': max(0, (cost_fstp_total * discount_factor if year == st.session_state.investment_year else 0) + annual_maint_fstp_total * discount_factor),
                        'Training': max(0, total_annual_cost_capacity_building * discount_factor),
                        'Public Awareness': total_awareness_cost * discount_factor
                    }

                    # Calculate benefits
                    # Health benefits - reduced to be more conservative
                    health_benefits = st.session_state.disease_incidence * (st.session_state.cost_per_visit + st.session_state.commute_cost_doctor) * 0.6
                    
                    # Productivity benefits - 5 days lost per case
                    working_age_ratio = st.session_state.working_age_pop / 100
                    productivity_benefits_working = hourly_monetary_income * working_age_ratio * 5 * 8 * pop_array[i] * 0.6
                    productivity_benefits_nonworking = hourly_monetary_income * (1 - working_age_ratio) * 5 * 8 * 0.15 * pop_array[i]
                    
                    # Time saved benefits
                    time_saved_working = hourly_monetary_income * working_age_ratio * 0.6 * (
                        st.session_state.water_collection_time * urban_households_array[i] + 
                        st.session_state.sanitation_access_saved * pop_array[i]
                    )
                    time_saved_nonworking = hourly_monetary_income * (1 - working_age_ratio) * 0.15 * (
                        st.session_state.water_collection_time * urban_households_array[i] + 
                        st.session_state.sanitation_access_saved * pop_array[i]
                    )
                    
                    # Recycled water benefits - 20% reuse
                    recycled_water_benefits = st.session_state.wastewater_reuse_pct/100 * sewage_generated_array[i] * 365 * 1000 * st.session_state.treated_water_price
                    
                    # Tourism benefits - 10% GDP increase from improved sanitation
                    tourism_benefits = 0.091 * st.session_state.gdp_per_capita * pop_array[i] * 0.1

                    present_value_total_benefits = (
                        health_benefits + productivity_benefits_working + productivity_benefits_nonworking + 
                        time_saved_working + time_saved_nonworking + recycled_water_benefits + tourism_benefits
                    ) * discount_factor

                    # Store benefit components
                    benefit_components = {
                        'Reduced Healtcare Costs': health_benefits * discount_factor,
                        'Productivity from Healthcare': (productivity_benefits_working + productivity_benefits_nonworking) * discount_factor,
                        'Time Saved from Water Collection': time_saved_working * discount_factor,
                        'Time Saved from Sanitation Access': time_saved_nonworking * discount_factor,
                        'Recycled Water': recycled_water_benefits * discount_factor,
                        'Tourism': tourism_benefits * discount_factor
                    }

                    # Update cumulative values
                    for key in cost_components:
                        cumulative_cost_components[key] += cost_components[key]
                    for key in benefit_components:
                        cumulative_benefit_components[key] += benefit_components[key]

                    cumulative_present_value_total_cost += present_value_total_cost
                    cumulative_present_value_total_benefit += present_value_total_benefits

                # Calculate benefit-to-cost ratio
                benefit_to_cost_ratio = cumulative_present_value_total_benefit / cumulative_present_value_total_cost if cumulative_present_value_total_cost != 0 else 0

                # Store state snapshot
                state_snapshot = {
                    'pop_in_target_year': pop_array[i],
                    'slum_pop_in_target_year': slum_pop_array[i],
                    'floating_pop_in_target_year': floating_pop_array[i],
                    'urban_households_in_target_year': urban_households_array[i],
                    'sewage_generated_in_target_year': sewage_generated_array[i],
                    'benefit_components': benefit_components.copy() if year > st.session_state.investment_year else None,
                    'cost_components': cost_components.copy() if year > st.session_state.investment_year else None,
                    'cumulative_benefit': cumulative_present_value_total_benefit,
                    'cumulative_cost': cumulative_present_value_total_cost,
                    'cumulative_benefit_components': cumulative_benefit_components.copy() if year > st.session_state.investment_year else None,
                    'cumulative_cost_components': cumulative_cost_components.copy() if year > st.session_state.investment_year else None,
                    'year': year,
                    'benefit_to_cost_ratio': benefit_to_cost_ratio
                }
                state_snapshots.append(state_snapshot)

                # Store results
                results_data.append({
                    "Year": year,
                    "Benefit-to-Cost Ratio": benefit_to_cost_ratio,
                    "Benefits_Per_Person": present_value_total_benefits / st.session_state.urban_pop if present_value_total_benefits > 0 else 0,
                    "Costs_Per_Person": present_value_total_cost / st.session_state.urban_pop if present_value_total_cost > 0 else 0,
                    "Total_Benefit": present_value_total_benefits,
                    "Total_Costs": present_value_total_cost,
                    "Cumulative_Total_Benefit": cumulative_present_value_total_benefit,
                    "Cumulative_Total_Cost": cumulative_present_value_total_cost,
                    "Cumulative_Benefits_Per_Person": cumulative_present_value_total_benefit / st.session_state.urban_pop if cumulative_present_value_total_benefit > 0 else 0,
                    "Cumulative_Costs_Per_Person": cumulative_present_value_total_cost / st.session_state.urban_pop if cumulative_present_value_total_cost > 0 else 0,
                    "Benefit_to_Cost_Ratio": benefit_to_cost_ratio
                })

            # Create DataFrame from results and ensure all columns exist
            st.session_state.results_df = pd.DataFrame(results_data)
            st.session_state.state_snapshots = state_snapshots
            st.session_state.calculations_done = True

            # Switch to Dashboard tab
            script_placeholder = st.empty()
            components.html(f"<script>{switch_tab(2)}</script>", height=0)
            time.sleep(0.1)
            script_placeholder.empty()
with tab3:
    if not st.session_state.get('calculations_done', False):
        st.warning('Please click "Submit" on Input Parameters tab')
    else:
        st.subheader("Dashboard")

        # Add dropdown for value type selection
        value_type = st.selectbox(
            "Select value type",
            ["City-wide values", "Per capita values"],
            index=0
        )
        show_per_capita = value_type == "Per capita values"
        
        # Create figure with secondary y-axis
        if show_per_capita:
            fig = px.line(st.session_state.results_df, x="Year", y=["Cumulative_Benefits_Per_Person", "Cumulative_Costs_Per_Person"])
        else:
            fig = px.line(st.session_state.results_df, x="Year", y=["Cumulative_Total_Benefit", "Cumulative_Total_Cost"])
        
        # Add benefit-to-cost ratio on secondary y-axis
        fig.add_scatter(x=st.session_state.results_df["Year"], 
                    y=st.session_state.results_df["Benefit-to-Cost Ratio"],
                    name="Benefit-to-Cost Ratio",
                    yaxis="y2")

        # Update layout with secondary y-axis and styling
        fig.update_layout(
            title="Return on WASH Investment",
            xaxis_title="Year",
            yaxis_title=f"{st.session_state.currency}/person" if show_per_capita else st.session_state.currency,
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
        fig.data[0].update(line_color='green', name='Cumulative Benefits', mode='lines+markers')  # Benefits line
        fig.data[1].update(line_color='grey', name='Cumulative Costs', mode='lines+markers')      # Costs line
        fig.data[2].update(line_color='blue', mode='lines+markers')                    # Ratio line
        st.plotly_chart(fig)
        # Create pie charts of benefit and cost components
        if st.session_state.state_snapshots:
            # Get available years from snapshots
            summary_years = [2035, 2040,2045, 2050, 2055, 2060]
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
                    if snapshot['year'] == selected_year and snapshot.get('cumulative_benefit_components'):
                        selected_benefits = snapshot['cumulative_benefit_components']
                        break
                
                if selected_benefits:
                    benefit_colors = ['#006400', '#008000', '#228B22', '#32CD32', '#90EE90', '#98FB98', '#ADFF2F']
                    fig_benefits = create_pie_chart(
                        selected_benefits,
                        f"Cumulative\nBenefits\n({selected_year})",
                        benefit_colors
                    )
                    st.plotly_chart(fig_benefits)

                    fig_benefits_bar = create_bar_chart(
                        selected_benefits,
                        "Cumulative Contribution to Benefits",
                        'green'
                    )
                    # Make benefit-to-cost ratio line thicker
                    fig_benefits_bar.data[1].update(line=dict(width=3))
                    st.plotly_chart(fig_benefits_bar)

            with col2:
                # Get cost components for selected year
                selected_costs = None
                for snapshot in st.session_state.state_snapshots:
                    if snapshot['year'] == selected_year and snapshot.get('cumulative_cost_components'):
                        selected_costs = snapshot['cumulative_cost_components']
                        break
                
                if selected_costs:
                    cost_colors = ['#1a1a1a', '#333333', '#4d4d4d', '#666666', '#808080', '#999999', '#b3b3b3']
                    fig_costs = create_pie_chart(
                        selected_costs,
                        f"Cumulative\nCosts\n({selected_year})",
                        cost_colors
                    )
                    st.plotly_chart(fig_costs)

                    fig_costs_bar = create_bar_chart(
                        selected_costs,
                        "Cumulative Contribution to Costs",
                        'grey'
                    )
                    st.plotly_chart(fig_costs_bar)
with tab4:
    if not st.session_state.get('calculations_done', False):
        st.warning('Please click "Submit" on Input Parameters tab')
    else:
        # Add dropdown for value type selection
        value_type_2 = st.selectbox(
            "Select value type",
            ["City-wide values", "Per capita values"],
            index=0,
            key="summary_value_type"  # Added unique key
        )
        show_per_capita_2 = value_type_2 == "Per capita values"
        
        # Create summary data using the stored results
        summary_years = [2030, 2040, 2050, 2060]
        summary_data = []
        
        for year in summary_years:
            # Get matching rows for this year
            year_rows = st.session_state.results_df[st.session_state.results_df['Year'] == year]
            
            # Only add data if we have results for this year
            if not year_rows.empty:
                year_data = year_rows.iloc[0]
                
                if show_per_capita_2:
                    row = {
                        'Year': year,
                        'Benefits': year_data['Benefits_Per_Person'],
                        'Total Costs': year_data['Costs_Per_Person'],
                        'Ratio': year_data['Benefit-to-Cost Ratio']
                    }
                else:
                    row = {
                        'Year': year,
                        'Benefits': year_data['Cumulative_Total_Benefit'],
                        'Total Costs': year_data['Cumulative_Total_Cost'],
                        'Ratio': year_data['Benefit-to-Cost Ratio']
                    }
                            
                summary_data.append(row)
            
        # Create and display main summary table if we have data
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Format all numeric columns
            numeric_cols = summary_df.select_dtypes(include=['float64', 'int64']).columns
            format_dict = {col: '{:,.0f}' for col in numeric_cols}
            
            # Display summary table without index
            st.table(summary_df.style.format(format_dict).set_table_styles([{'selector': 'thead tr th:first-child', 'props': [('display', 'none')]}, {'selector': 'tbody tr th:first-child', 'props': [('display', 'none')]}]))

            # Add buttons for detailed breakdowns
            col1, col2 = st.columns(2)
            
            with col1:
                show_benefits = st.button("Show Benefits Breakdown")
            with col2:
                show_costs = st.button("Show Costs Breakdown")

            # Store button states in session state
            if show_benefits:
                st.session_state.show_benefits = True
            if show_costs:
                st.session_state.show_costs = True

            if st.session_state.get('show_benefits', False) or st.session_state.get('show_costs', False):
                # Create container for year selection
                year_select_container = st.container()
                
                # Let user select year for breakdown
                selected_year = year_select_container.selectbox(
                    "Select year to view breakdown:",
                    summary_years,
                    index=len(summary_years)-1,
                    key="breakdown_year"
                )

                # Create container for tables
                tables_container = st.container()

                with tables_container:
                    # Show benefits breakdown if button clicked
                    if st.session_state.get('show_benefits', False):
                        selected_benefits = None
                        for snapshot in st.session_state.state_snapshots:
                            if snapshot['year'] == selected_year and snapshot.get('cumulative_benefit_components'):
                                selected_benefits = snapshot['cumulative_benefit_components']
                                break
                        
                        if selected_benefits:
                            st.subheader(f"Benefits Breakdown for {selected_year}")
                            benefits_df = pd.DataFrame({
                                'Component': selected_benefits.keys(),
                                'Value': selected_benefits.values()
                            })
                            if show_per_capita_2:
                                year_data = st.session_state.results_df[st.session_state.results_df['Year'] == selected_year].iloc[0]
                                benefits_df['Value'] = benefits_df['Value'] / year_data['Population']
                            st.table(benefits_df.style.format({'Value': '{:,.0f}'}).set_table_styles([{'selector': 'thead tr th:first-child', 'props': [('display', 'none')]}, {'selector': 'tbody tr th:first-child', 'props': [('display', 'none')]}]))

                    # Show costs breakdown if button clicked
                    if st.session_state.get('show_costs', False):
                        selected_costs = None
                        for snapshot in st.session_state.state_snapshots:
                            if snapshot['year'] == selected_year and snapshot.get('cumulative_cost_components'):
                                selected_costs = snapshot['cumulative_cost_components']
                                break
                        
                        if selected_costs:
                            st.subheader(f"Costs Breakdown for {selected_year}")
                            costs_df = pd.DataFrame({
                                'Component': selected_costs.keys(),
                                'Value': selected_costs.values()
                            })
                            if show_per_capita_2:
                                year_data = st.session_state.results_df[st.session_state.results_df['Year'] == selected_year].iloc[0]
                                costs_df['Value'] = costs_df['Value'] / year_data['Population']
                            st.table(costs_df.style.format({'Value': '{:,.0f}'}).set_table_styles([{'selector': 'thead tr th:first-child', 'props': [('display', 'none')]}, {'selector': 'tbody tr th:first-child', 'props': [('display', 'none')]}]))
        else:
            st.warning("No data available for summary years")

with tab5:
    st.write("### Sanitation Variables Glossary")
        
    # Display HTML content directly using streamlit components
    components.html(doc_content, height=1200, scrolling=True)
    
with tab6:
    st.write("Help")
