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
from cost_functions import *
from app_functions import *

read_local = False
if read_local:
    city_default_data = pd.read_csv('data/city_default_data.csv')
    variables = pd.read_csv('data/variables.csv')
    with open('sanopps/documentation.html', 'r') as f:
        doc_content = f.read()
    with open('data/methodology.markdown', 'r') as f:
        methodology_content = f.read()
else:
    city_default_data = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/city_default_data.csv')
    variables = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/variables.csv')
    doc_content = requests.get('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/sanopps/documentation.html').text
    methodology_content = requests.get('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/sanopps/data/methodology.markdown')

st.title("SanOpps: The WASH Cost-Benefit Analysis Tool for Local Government")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Home Page",
    "Data Input",
    "Dashboard",
    "Summary", 
    "Definitions",
    "Help"
])

# Initialize session state for calculations
initialize_session_state(['calculations_done', 'results_df', 'summary_data'], [False, None, None])

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
    
    # Get filename from user using a key to maintain state
    if 'config_filename' not in st.session_state:
        st.session_state.config_filename = "sanopps_config"
    
    # Create text input and download button in columns to prevent collapsing
    col1, col2 = st.columns([2,1])
    with col1:
        filename = st.text_input(
            "Enter filename", 
            value=st.session_state.config_filename,
            key="config_filename"
        )
    
    with col2:
        st.download_button(
            label="Download",
            data=json_str,
            file_name=f"{filename.replace(' ', '_')}.json",
            mime="application/json",
            key="download_config_button",
            use_container_width=True
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
        col1, col2 = st.columns([7.5,2.5], gap="medium")
        with col1:
            st.write("This tool is designed to support policy-makers, researchers, and nonprofits assess the economic viability and social impact of Water, Sanitation, and Hygiene (WASH) initiatives. It provides a comprehensive analysis of the present and future costs and benefits associated with WASH projects, and helps identify the highest value-generating investments.")

            st.subheader("Why use SanOpps?")
            st.write("SanOpps provides a localized understanding of a global trend: that investment in WASH drives economic growth. The dashboard lays out the return on investment potential for WASH in your city.")

            st.image("images/sanopps_phases.png", use_container_width=True, width=100)

        with col2:
            st.markdown("#### *What is WASH?*")
            st.image("images/sanopps_wash.png", use_container_width=True, width=100)
            st.write("<small>*WASH initiatives improve access to clean Water, Sanitation, and Hygiene practices, particularly in low- and middle-income areas. Investing in WASH infrastructure is essential to improve public health, reduce poverty, promote equitable access to essential services, and enhance socio-economic development.*</small>", unsafe_allow_html=True)
    
        st.subheader("SanOpps Features")
        # Render mermaid diagram with fixed height container
        mermaid_code = """
        classDiagram
            direction LR
            class Cost_Indicators{
                Cost of water supply, 
                sanitation facilities,
                and sewage management.
            }
            class Benefit_Indicators{
                Benefits from improved
                health, productivity,
                convenience, and 
                quality of life
            }
            class Data_Inputs{
                Interactive input for key
                variables, tailoring the 
                analysis to your region.
            }
            class Summary{
                Table of cumulative cost and
                benefit values, broken down
                every 5 years after the 
                initial investment.
            }
            class Dashboard{
                Adaptable data views for cost
                and benefit figures, tracking 
                investments through a 30-year 
                projection.
            }
            Cost_Indicators --> Summary
            Data_Inputs --> Summary
            Benefit_Indicators --> Summary
            Summary --> Dashboard
            %%{init: {'theme':'neutral', 'themeVariables': {'classBorder':'#9370DB', 'classText':'#000000', 'classFill':'#E6E6FA'}}}%%
            style Data_Inputs fill:#800080,color:#fff
            style Summary fill:#008000,color:#fff
            style Dashboard fill:#808080,color:#fff
        """

        components.html(
            f"""
            <div style="height: 500px; overflow: visible;">
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
            height=500,
        )

    st.write("---")
    st.subheader("Developers")
    logo_col1, logo_col2, logo_col3 = st.columns(3)
    
    with logo_col1:
        st.image("images/ecosan.jpeg", use_container_width=True, width=100)
    
    with logo_col2:
        st.image("images/mit.png", use_container_width=True, width=100)
        
    with logo_col3:
        st.image("images/wto.png", use_container_width=True, width=100)

    # Add "Next" button to go to Input Parameters tabs
    if st.button("Next: Input City Data"):
        script_placeholder = st.empty()
        components.html(f"<script>{switch_tab(1)}</script>", height=0)
        time.sleep(0.1)
        script_placeholder.empty()
        
def generate_inputs(variables, category, input_type):
    inputs = variables[(variables['category'] == category) & (variables['type'] == input_type)]
    
    for _, row in inputs.iterrows():
        name_col, input_col, units_col, percent_col = st.columns([1.2, 1.1, 1.0, 0.7])
        with name_col:
            st.write(row['label'])
        with input_col:
            key = row['key']
            
            # Initialize with city data or default value if not already in session state
            if key not in st.session_state:
                if 'city_data' in st.session_state and key in st.session_state.city_data:
                    st.session_state[key] = st.session_state.city_data[key]
                    # For percent fields, initialize both raw and percent values
                    if pd.notna(row['percent_option']):
                        if row['unit'] == '%':
                            # For % default, store raw value without _percent
                            base_key = key.replace('_percent', '')
                            st.session_state[base_key] = st.session_state[key] * st.session_state.get(row['percent_option'], 1) / 100
                        else:
                            # For raw default, store percent value with _percent
                            st.session_state[f"{key}_percent"] = st.session_state[key] / st.session_state.get(row['percent_option'], 1) * 100
                else:
                    print(key)
                    # Default values as fallback
                    if row['value_type'] == 'float':
                        st.session_state[key] = 1.0
                    elif row['value_type'] == 'int':
                        st.session_state[key] = 1
                    else:
                        st.session_state[key] = "NO" if key in ['co_treat_avail', 'fstp_avail', 'co_treat_proposed'] else "INR"
                
                if pd.notna(row['percent_option']):
                    if row['unit'] == '%':
                        base_key = key.replace('_percent', '')
                        st.session_state[base_key] = st.session_state[key] * st.session_state.get(row['percent_option'], 1) / 100
                    else:
                        st.session_state[f"{key}_percent"] = st.session_state[key] / st.session_state.get(row['percent_option'], 1) * 100
            
            if key in ['currency', 'co_treat_avail', 'fstp_avail', 'co_treat_proposed']:
                options = ["INR", "USD", "EUR"] if key == 'currency' else ["NO", "YES"]
                # Ensure session state value is valid before using as index
                current_value = st.session_state[key]
                if current_value not in options:
                    current_value = options[0]
                    st.session_state[key] = current_value
                    
                selected = st.selectbox(f"select_{key}", options, key=f"select_{key}", 
                                     index=options.index(current_value),
                                     label_visibility="collapsed")
                st.session_state[key] = selected
                
                if key == 'currency' and selected != st.session_state.get('prev_currency'):
                    if 'prev_currency' in st.session_state:
                        old_rate = conversion_rates[st.session_state.prev_currency]
                        new_rate = conversion_rates[selected]
                        conversion_factor = old_rate / new_rate
                        
                        for monetary_key in st.session_state:
                            if isinstance(st.session_state[monetary_key], (int, float)):
                                monetary_label = variables[variables['key'] == monetary_key]
                                if not monetary_label.empty and 'currency' in str(monetary_label.iloc[0]['unit']):
                                    st.session_state[monetary_key] *= conversion_factor
                    
                    st.session_state.prev_currency = selected
            elif row['value_type'] == 'slider':
                # Ensure value is numeric before using in slider
                try:
                    current_value = float(st.session_state[key])
                except (ValueError, TypeError):
                    current_value = 0.0
                    st.session_state[key] = current_value
                    
                value = st.slider(f"slider_{key}", 
                                min_value=0.0, 
                                max_value=100.0,
                                value=current_value,
                                label_visibility="collapsed",
                                key=f"slider_{key}")
                st.session_state[key] = value
            else:
                if pd.notna(row['percent_option']):
                    percent_toggle = st.session_state.get(f"{key}_percent_toggle", row['unit'] == '%')
                    if percent_toggle:
                        value = st.number_input(
                            f"percent_{key}",
                            value=float(st.session_state[key+"_percent"] if not row['unit'] == '%' else st.session_state[key]),
                            label_visibility="collapsed",
                            key=f"percent_{key}"
                        )
                        if row['unit'] == '%':
                            st.session_state[key] = value
                            base_key = key.replace('_percent', '')
                            st.session_state[base_key] = value * st.session_state.get(row['percent_option'], 1) / 100
                        else:
                            st.session_state[key+"_percent"] = value
                            st.session_state[key] = value * st.session_state.get(row['percent_option'], 1) / 100
                    else:
                        if row['value_type'] == 'int':
                            value = st.number_input(f"direct_{key}", value=int(st.session_state[key]), label_visibility="collapsed", key=f"direct_{key}")
                        else:
                            value = st.number_input(f"direct_{key}", value=float(st.session_state[key]), label_visibility="collapsed", key=f"direct_{key}")
                        st.session_state[key] = value
                        st.session_state[key+"_percent"] = value/st.session_state.get(row['percent_option'], 1)*100
                else:
                    if row['value_type'] == 'int':
                        value = st.number_input(f"input_{key}", value=int(st.session_state[key]), label_visibility="collapsed", key=f"input_{key}")
                    else:
                        value = st.number_input(f"input_{key}", value=float(st.session_state[key]), label_visibility="collapsed", key=f"input_{key}")
                    st.session_state[key] = value
        with units_col:
            if pd.notna(row['percent_option']):
                if st.session_state.get(f"{key}_percent_toggle", row['unit'] == '%'):
                    matching_rows = variables[variables['key'] == row['percent_option']]
                    percent_option_label = matching_rows.iloc[0]['label'] if not matching_rows.empty else row['percent_option']
                    st.write(f"% of {percent_option_label}")
                else:
                    ref_var = variables[variables['key'] == row['percent_option']]
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
                        
with tab2:
    st.markdown("Please enter data below. All data inputs (including population, financial, and current infrastucture) should be entered for the *current* year")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Current Configuration"):
            save_config()
    with col2:
        if st.button("Load Configuration"):
            load_config()

    country_col, state_col, city_col, reset_col = st.columns([1,1,1,0.5])
    with country_col:
        country = st.selectbox("Select Country", list(city_default_data['Country'].unique()), key="country")
    with state_col:
        state = st.selectbox("Select State/Province", list(city_default_data[city_default_data['Country'] == country]['State/Province'].unique()), key="state")
    with city_col:
        city = st.selectbox("Select City", list(city_default_data[(city_default_data['Country'] == country) & (city_default_data['State/Province'] == state)]['City'].unique()), key="city")
        
        # Only update values from city data if city has changed
        if city != st.session_state.get('prev_city'):
            if city in city_default_data['City'].values:
                city_data = city_default_data[city_default_data['City'] == city].iloc[0]
                st.session_state.city_data = city_data.to_dict()
                # Update all values from city data
                for key in city_data.keys():
                    st.session_state[key] = city_data[key]
                    if key in variables['key'].values:
                        row = variables[variables['key'] == key].iloc[0]
                        if pd.notna(row['percent_option']):
                            st.session_state[key+"_percent"] = city_data[key]/st.session_state.get(row['percent_option'], 1)*100
            st.session_state.prev_city = city

    with reset_col:
        if st.button("Reset City") and city in city_default_data['City'].values:
            if 'city_data' in st.session_state:
                for key, value in st.session_state.city_data.items():
                    st.session_state[key] = value
                    if key in variables['key'].values:
                        row = variables[variables['key'] == key].iloc[0]
                        if pd.notna(row['percent_option']):
                            st.session_state[key+"_percent"] = value/st.session_state.get(row['percent_option'], 1)*100

    categories = variables['category'].unique()
    for category in categories:
        st.subheader(category)
        generate_inputs(variables, category, 'user_input')
        
        with st.expander(f"Optional {category} Parameters"):
            generate_inputs(variables, category, 'optional_input')

    # Submit Button
    if st.button("Submit"):
        # Check for empty inputs
        empty_inputs = []
        for key in st.session_state:
            if st.session_state[key] is None or (isinstance(st.session_state[key], str) and st.session_state[key].strip() == ""):
                if key not in ['summary_data', 'results_df', 'prev_city', 'city_data']:
                    empty_inputs.append(key)

        # Check for negative values
        negative_inputs = []
        for key, value in st.session_state.items():
            if isinstance(value, (int, float)) and value < 0:
                negative_inputs.append(key)

        if empty_inputs:
            st.error("Please fill in all inputs before proceeding")
        elif negative_inputs:
            st.error(f"The following inputs cannot be negative: {', '.join(negative_inputs)}")
        else:
            # Initialize lists to store results for each year
            years = list(range(st.session_state.current_year, 2061))
            benefit_to_cost_ratios, results_data, state_snapshots = [], [], []

            # Calculate base values
            gdp = st.session_state.gdp_per_capita * st.session_state.urban_pop
            st.session_state.hourly_monetary_income = st.session_state.gdp_per_capita/(8*5*52) # 8 hours per day, 5 days per week, 52 weeks per year

            # Population projections
            n_years = [(year - st.session_state.current_year) / 10 for year in years]
            
            # Create arrays dictionary
            arrays = {}
            
            # Population arrays
            arrays['pop'] = [st.session_state.urban_pop * (1 + st.session_state.growth_rate/100) ** n for n in n_years]
            percentage_slum_pop_current = st.session_state.slum_pop / st.session_state.urban_pop
            percentage_floating_pop_current = st.session_state.floating_pop / st.session_state.urban_pop
            percentage_slum_pop_array = [max(percentage_slum_pop_current - 0.1, 0) for _ in years]
            arrays['slum_pop'] = [pct * pop for pct, pop in zip(percentage_slum_pop_array, arrays['pop'])]
            arrays['floating_pop'] = [percentage_floating_pop_current * pop for pop in arrays['pop']]
            household_ratio = st.session_state.urban_pop / st.session_state.urban_households
            arrays['urban_households'] = [pop / household_ratio for pop in arrays['pop']]
            
            # Water connections array
            arrays['urban_households_without_fhtc'] = [households - st.session_state.urban_households_with_fhtp for households in arrays['urban_households']]

            # Toilet calculations
            arrays['ct'] = [slum_pop / st.session_state.persons_per_wc for slum_pop in arrays['slum_pop']]
            arrays['pt'] = [floating_pop / st.session_state.persons_per_pt for floating_pop in arrays['floating_pop']]
            arrays['additional_ct'] = [ct - st.session_state.comm_toilets * st.session_state.wc_per_ct for ct in arrays['ct']]
            arrays['additional_pt'] = [pt - st.session_state.public_toilets * st.session_state.wc_per_ct for pt in arrays['pt']]

            # Sewer calculations
            arrays['pop_connected_sewer'] = [(st.session_state.urban_households_with_sewer_percent/100) * pop for pop in arrays['pop']]
            if st.session_state.urban_households_with_sewer_percent == 0 or st.session_state.urban_pop == 0:
                sewer_length_per_person = 0
            else:
                sewer_length_per_person = st.session_state.sewer_length / ((st.session_state.urban_households_with_sewer_percent/100) * st.session_state.urban_pop)
            arrays['sewer_network'] = [(pop * sewer_length_per_person) / 1000 for pop in arrays['pop_connected_sewer']]
            arrays['gap_sewer_network'] = [max(0, network - st.session_state.sewer_length) for network in arrays['sewer_network']]
            
            # Treatment capacity
            arrays['sewage_generated'] = [(1-st.session_state.wastewater_reuse_pct) * pop * st.session_state.water_consumption / 1000000 for pop in arrays['pop_connected_sewer']]
            arrays['gap_treatment_capacity'] = [max(0, sewage - st.session_state.stp_capacity) for sewage in arrays['sewage_generated']]
            
            # FSTP calculations
            arrays['households_septic_tanks'] = [households * (1 - st.session_state.urban_households_with_sewer_percent/100) for households in arrays['urban_households']]
            arrays['septage_treated_per_day'] = [(households * st.session_state.septage_emptied_per_household) / (st.session_state.desludging_freq * 300) for households in arrays['households_septic_tanks']]

            # Initialize component dictionaries
            cost_components = dict.fromkeys([
                'Tap Water Supply', 'Community Toilets', 'Public Toilets',
                'Sewer', 'Sewage Treatment Plant', 'Fecal Sludge Treatment Plant',
                'Training Officials', 'Public Awareness'
            ], 0)

            benefit_components = dict.fromkeys([
                'Reduced Healtcare Costs', 'Productivity from Healthcare',
                'Time Saved from Water Collection', 'Time Saved from Sanitation Access',
                'Recycled Water', 'Tourism'
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
                    cost_components = add_capital_cost(year, arrays, i, st.session_state)
                    present_value_total_cost = sum(cost_components.values()) * discount_factor
                    cumulative_present_value_total_cost = present_value_total_cost

                # Add operating costs and benefits after investment year

                                # Add capital costs only in investment year
                elif year < st.session_state.investment_year + st.session_state.construction_time:
                    cost_components = add_operating_cost(i, arrays, st.session_state)
                    present_value_total_cost = sum(cost_components.values()) * discount_factor

                # Add operating costs and benefits after investment year
                elif year > st.session_state.investment_year + st.session_state.construction_time:
                    cost_components = add_operating_cost(i, arrays, st.session_state)
                    benefit_components = add_annual_benefit(i, arrays, st.session_state)

                    present_value_total_cost = sum(cost_components.values()) * discount_factor
                    present_value_total_benefits = sum(benefit_components.values()) * discount_factor

                    # Update cumulative values
                    for key in cost_components:
                        cumulative_cost_components[key] += cost_components[key] * discount_factor
                    for key in benefit_components:
                        cumulative_benefit_components[key] += benefit_components[key] * discount_factor

                    cumulative_present_value_total_cost += present_value_total_cost
                    cumulative_present_value_total_benefit += present_value_total_benefits

                # Calculate benefit-to-cost ratio
                benefit_to_cost_ratio = cumulative_present_value_total_benefit / cumulative_present_value_total_cost if cumulative_present_value_total_cost != 0 else 0

                # Store state snapshot
                state_snapshot = {
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
                    "Benefits_Per_Person": present_value_total_benefits / arrays['pop'][i] if present_value_total_benefits > 0 else 0,
                    "Costs_Per_Person": present_value_total_cost / arrays['pop'][i] if present_value_total_cost > 0 else 0,
                    "Total_Benefit": present_value_total_benefits,
                    "Total_Costs": present_value_total_cost,
                    "Cumulative_Total_Benefit": cumulative_present_value_total_benefit,
                    "Cumulative_Total_Cost": cumulative_present_value_total_cost,
                    "Cumulative_Benefits_Per_Person": cumulative_present_value_total_benefit / arrays['pop'][i] if cumulative_present_value_total_benefit > 0 else 0,
                    "Cumulative_Costs_Per_Person": cumulative_present_value_total_cost / arrays['pop'][i] if cumulative_present_value_total_cost > 0 else 0,
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
                    y=st.session_state.results_df["Benefit_to_Cost_Ratio"],
                    name="Benefit-to-Cost Ratio",
                    yaxis="y2")

        # Find intersection year where benefits exceed costs
        df = st.session_state.results_df
        if show_per_capita:
            benefits = df["Cumulative_Benefits_Per_Person"]
            costs = df["Cumulative_Costs_Per_Person"]
        else:
            benefits = df["Cumulative_Total_Benefit"] 
            costs = df["Cumulative_Total_Cost"]
            
        # Find first year where benefits exceed costs
        intersection_year = None
        for i in range(len(df)):
            if benefits.iloc[i] >= costs.iloc[i] and benefits.iloc[i] > 0 and costs.iloc[i] > 0:
                intersection_year = df["Year"].iloc[i]
                break
                
        if intersection_year:
            # Add vertical line at intersection that stops at 0
            fig.add_shape(
                type="line",
                x0=intersection_year,
                x1=intersection_year,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color="black")
            )
            
            # Add annotation for ROI years
            roi_years = intersection_year - st.session_state.investment_year
            fig.add_annotation(
                x=intersection_year + 4,
                y=0.8,
                yref="paper",
                text=f"{roi_years}-year ROI",
                showarrow=False,
                font=dict(color='black', size=16)
            )

        # Update layout with secondary y-axis and styling
        fig.update_layout(
            title=dict(
                text="Return on WASH Investment",
                font=dict(size=24)
            ),
            xaxis_title=dict(
                text="Year",
                font=dict(size=18)
            ),
            yaxis_title=dict(
                text=f"{st.session_state.currency}/person" if show_per_capita else st.session_state.currency,
                font=dict(size=18)
            ),
            yaxis2=dict(
                title=dict(
                    text="Benefit-to-Cost Ratio",
                    font=dict(size=18)
                ),
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(size=14)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgrey',
                tickfont=dict(size=14)
            ),
            xaxis=dict(
                dtick=10,  # Set x-axis tick interval to 10 years
                showgrid=False,
                tickfont=dict(size=14)
            ),
            showlegend=False,
            hovermode='x unified',
            hoverlabel=dict(font_size=14)
        )

        # Update line colors and add markers
        fig.data[0].update(line_color='green', name='Cumulative Benefits', mode='lines')  # Benefits line
        fig.data[1].update(line_color='grey', name='Cumulative Costs', mode='lines')      # Costs line
        fig.data[2].update(line_color='blue', mode='lines', line=dict(width=5), yaxis='y2')  # Ratio line on secondary axis

        # Add text labels at the end of each line
        last_x = df["Year"].iloc[-1]
        for trace in fig.data:
            last_y = trace.y[-1]
            # Put Benefit-to-Cost Ratio label on left side
            if trace.name == "Benefit-to-Cost Ratio":
                x_pos = last_x - 3
                x_anchor = 'right'
                y_ref = 'y2'  # Use secondary y-axis reference for ratio label
            else:
                x_pos = last_x + 2
                x_anchor = 'left'
                y_ref = 'y'  # Use primary y-axis reference for other labels
                
            fig.add_annotation(
                x=x_pos,
                y=last_y,
                text=trace.name,
                showarrow=False,
                font=dict(
                    color=trace.line.color,
                    size=16
                ),
                xanchor=x_anchor,
                yanchor='middle',
                yref=y_ref  # Specify y-axis reference for each label
            )

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
                        'Ratio': year_data["Benefit_to_Cost_Ratio"]
                    }
                else:
                    row = {
                        'Year': year,
                        f'Total Benefits ({st.session_state.currency})': year_data['Cumulative_Total_Benefit'],
                        f'Total Costs ({st.session_state.currency})': year_data['Cumulative_Total_Cost'],
                        'Benefit-to-Cost Ratio': year_data["Benefit_to_Cost_Ratio"]
                    }
                            
                summary_data.append(row)
            
        # Create and display main summary table if we have data
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Format all numeric columns
            numeric_cols = summary_df.select_dtypes(include=['float64', 'int64']).columns
            format_dict = {col: '{:,.0f}' for col in numeric_cols}
            # Override format for benefit-to-cost ratio column
            if 'Benefit-to-Cost Ratio' in numeric_cols:
                format_dict['Benfit-to-Cost Ratio'] = '{:,.1f}'
            if 'Year' in numeric_cols:
                format_dict['Year'] = '{:.0f}'
            
            # Display summary table without index
            st.table(summary_df.style.format(format_dict).set_table_styles([{'selector': 'thead tr th:first-child', 'props': [('display', 'none')]}, {'selector': 'tbody tr th:first-child', 'props': [('display', 'none')]}]))

            # Add buttons for detailed breakdowns
            col1, col2 = st.columns(2)
            
            with col1:
                benefits_text = "Hide Benefits Breakdown" if st.session_state.get('show_benefits', False) else "Show Benefits Breakdown"
                show_benefits = st.button(benefits_text)
            with col2:
                costs_text = "Hide Costs Breakdown" if st.session_state.get('show_costs', False) else "Show Costs Breakdown"
                show_costs = st.button(costs_text)

            # Store button states in session state
            if show_benefits:
                st.session_state.show_benefits = not st.session_state.get('show_benefits', False)
            if show_costs:
                st.session_state.show_costs = not st.session_state.get('show_costs', False)

            def generate_breakdown_table(components, year, component_type, show_per_capita):
                """Generate breakdown table for benefits or costs"""
                st.subheader(f"{component_type} Breakdown for {year}")
                df = pd.DataFrame({
                    'Component': components.keys(),
                    f'Value ({st.session_state.currency})': components.values()
                })
                if show_per_capita:
                    year_data = st.session_state.results_df[st.session_state.results_df['Year'] == year].iloc[0]
                    df['Value'] = df['Value'] / year_data['Population']
                st.table(df.style.format({'Value': '{:,.0f}'}).set_table_styles([
                    {'selector': 'thead tr th:first-child', 'props': [('display', 'none')]}, 
                    {'selector': 'tbody tr th:first-child', 'props': [('display', 'none')]}
                ]))

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
                            generate_breakdown_table(selected_benefits, selected_year, "Benefits", show_per_capita_2)

                    # Show costs breakdown if button clicked
                    if st.session_state.get('show_costs', False):
                        selected_costs = None
                        for snapshot in st.session_state.state_snapshots:
                            if snapshot['year'] == selected_year and snapshot.get('cumulative_cost_components'):
                                selected_costs = snapshot['cumulative_cost_components']
                                break
                        
                        if selected_costs:
                            generate_breakdown_table(selected_costs, selected_year, "Costs", show_per_capita_2)
        else:
            st.warning("No data available for summary years")

with tab5:
    st.write("### Sanitation Variables Glossary")
        
    # Display HTML content directly using streamlit components
    components.html(doc_content, height=1200, scrolling=True)
    st.write("### Methodology")
    st.markdown(methodology_content)
    
with tab6:
    st.write("For support with the SanOpps application, please contact the World Toilet Organization at ")
