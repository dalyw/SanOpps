import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import time
import json
import os
import requests
import copy
from cost_functions import *
from app_functions import initialize_session_state, switch_tab, create_line_chart, create_pie_chart, create_bar_chart, conversion_rates

st.set_page_config(page_title="SanOpps", page_icon="💧", initial_sidebar_state="auto", menu_items=None)

# Set light mode
st.markdown("""
    <style>
        .stApp {
            background-color: white;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

read_local = False
if read_local:
    city_defaults = pd.read_csv('data/city_defaults.csv')
    variables = pd.read_csv('data/variables.csv')
    with open('sanopps/documentation.html', 'r') as f:
        doc_content = f.read()
    with open('data/methodology.markdown', 'r') as f:
        methodology_content = f.read()
else:
    city_defaults = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/city_defaults.csv')
    variables = pd.read_csv('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/variables.csv')
    doc_content = requests.get('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/sanopps/documentation.html').text
    methodology_content = requests.get('https://raw.githubusercontent.com/dalyw/SanOpps/refs/heads/main/data/methodology.markdown')

st.title("SanOpps: The WASH Cost-Benefit Analysis Tool for Local Government")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Home Page",
    "Data Input",
    "Dashboard",
    "Summary", 
    "Sensitivity",
    "Methodology",
    "Glossary",
    "Help"
])

# Initialize session state for calculations
initialize_session_state(['calculations_done', 'results_df', 'summary_data', 'sensitivity_results'], [False, None, None, None])

# Create configs directory if it doesn't exist
if not os.path.exists('configs'):
    os.makedirs('configs')
def save_config():
    """Save current configuration to JSON file"""
    config = {}
    for key in st.session_state:
        # Only save input parameters, not calculation results
        if key not in ['calculations_done', 'results_df', 'summary_data', 'sensitivity_results']:
            # Convert numpy types to native Python types to ensure JSON serialization
            if isinstance(st.session_state[key], (np.int64, np.int32, np.int16, np.int8)):
                config[key] = int(st.session_state[key])
            elif isinstance(st.session_state[key], (np.float64, np.float32, np.float16)):
                config[key] = float(st.session_state[key])
            else:
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
    with st.container(): # Use container to force full height for mermaid diagram
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
        key = row['key']
        
        with name_col:
            name_placeholder = st.empty()
            name_placeholder.write(row['label'])
        with percent_col:
            if pd.notna(row['percent_option']):
                percent_toggle = st.checkbox(f"Input as %", key=f"{key}_percent_toggle", value=row['unit']=='%')
            else:
                st.write("")
        with input_col:
            help_val = str(row['definition'])
            
            # Initialize with city data or default value if not already in session state
            if key not in st.session_state:
                if 'city_data' in st.session_state and key in st.session_state.city_data:
                    st.session_state[key] = st.session_state.city_data[key]
                    # For percent fields, initialize both raw and percent values
                    if pd.notna(row['percent_option']):
                        if row['unit'] == '%':
                            # For % default, store raw value without _percent
                            base_key = key.replace('_percent', '')
                            st.session_state[base_key] = st.session_state[key] / 100 * st.session_state.get(row['percent_option'], 1)
                        else:
                            # For raw default, store percent value with _percent
                            st.session_state[f"{key}_percent"] = st.session_state[key] / st.session_state.get(row['percent_option'], 1) * 100
                else:
                    # Default values as fallback
                    if row['value_type'] == 'float':
                        st.session_state[key] = 1.0
                    elif row['value_type'] == 'int':
                        st.session_state[key] = 1
                    else:
                        st.session_state[key] = "NO" if key in ['co_treat_avail', 'fstp_avail', 'co_treat_proposed', 'amortize_capex'] else "INR"
                
                if pd.notna(row['percent_option']):
                    if row['unit'] == '%':
                        base_key = key.replace('_percent', '')
                        st.session_state[base_key] = st.session_state[key] * st.session_state.get(row['percent_option'], 1) / 100
                    else:
                        st.session_state[f"{key}_percent"] = st.session_state[key] / st.session_state.get(row['percent_option'], 1) * 100

            # Define common kwargs for all inputs
            input_kwargs = {
                'label_visibility': 'collapsed',
                'help': help_val
            }
            
            if key in ['currency', 'co_treat_avail', 'fstp_avail', 'co_treat_proposed', 'amortize_capex']:
                options = ["INR", "USD", "EUR"] if key == 'currency' else ["NO", "YES"]
                current_value = st.session_state[key]
                if current_value not in options:
                    current_value = options[0]
                    st.session_state[key] = current_value
                    
                selected = st.selectbox(
                    f"select_{key}", 
                    options,
                    key=f"select_{key}",
                    index=options.index(current_value),
                    **input_kwargs
                )
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
                try:
                    current_value = float(st.session_state[key])
                except (ValueError, TypeError):
                    current_value = 0.0
                    st.session_state[key] = current_value
                    
                value = st.slider(
                    f"slider_{key}",
                    min_value=0.0, max_value=100.0,
                    value=current_value, **input_kwargs
                )
                st.session_state[key] = value
            else:
                if pd.notna(row['percent_option']):
                    # Get previous toggle state and percent option value
                    # prev_toggle = st.session_state.get(f"{key}_prev_toggle", percent_toggle)
                    percent_option_value = st.session_state.get(row['percent_option'], 1)
                    
                    is_percent_var = key.endswith('_percent') or row['unit'] == '%'
                    
                    # Calculate display value based on toggle state
                    if percent_toggle:
                        if is_percent_var: # percent is checked and var has _percent
                            # For percent variables, show the percent value directly
                            display_value = st.session_state[key]
                        else:
                            # For base variables, calculate and show the percent equivalent
                            display_value = st.session_state.get(f"{key}_percent", 
                                           st.session_state[key] / percent_option_value * 100)
                    else:
                        # When showing as base value
                        if is_percent_var:
                            # For percent variables, show the corresponding base value
                            base_key = key.replace('_percent', '')
                            display_value = st.session_state.get(base_key, 
                                           st.session_state[key] * percent_option_value / 100)
                        else:
                            # For base variables, show the base value directly
                            display_value = st.session_state[key]

                    # Create number input with calculated display value
                    if row['value_type'] == 'int':
                        value = st.number_input(
                            f"direct_{key}",
                            value=int(display_value),
                            key=f"direct_{key}_{percent_toggle}",  # Add toggle state to key to force refresh
                            step=1,  # Use step instead of format for integers
                            **input_kwargs
                        )
                    else:
                        value = st.number_input(
                            f"direct_{key}",
                            value=float(display_value),
                            key=f"direct_{key}_{percent_toggle}",  # Add toggle state to key to force refresh
                            format="%.1f",  # Format with thousands separator and 2 decimal places
                            **input_kwargs
                        )
                    
                    # Store the value based on toggle state
                    if percent_toggle: # toggle is checked
                        if is_percent_var:
                            # For percent variables, update the percent value and recalculate base
                            st.session_state[key] = value
                            base_key = key.replace('_percent', '')
                            st.session_state[base_key] = value * percent_option_value / 100
                        else:
                            # For base variables, update the percent value and recalculate base
                            st.session_state[f"{key}_percent"] = value
                            st.session_state[key] = value * percent_option_value / 100
                    else:
                        if is_percent_var:
                            # For percent variables, update the base value but keep percent unchanged
                            base_key = key.replace('_percent', '')
                            st.session_state[base_key] = value
                        else:
                            # For base variables, update the base value and recalculate percent
                            st.session_state[key] = value
                            st.session_state[f"{key}_percent"] = value / percent_option_value * 100
                    
                    # Update toggle state for next render
                    st.session_state[f"{key}_prev_toggle"] = percent_toggle

                else:
                    if row['value_type'] == 'int':
                        value = st.number_input(
                            f"input_{key}",
                            value=int(st.session_state[key]),
                            key=f"input_{key}",
                            **input_kwargs
                        )
                    else:
                        value = st.number_input(
                            f"input_{key}",
                            value=float(st.session_state[key]),
                            key=f"input_{key}",
                            format="%.1f",  # Format with thousands separator and 2 decimal places
                            **input_kwargs
                        )
                    st.session_state[key] = value

        with units_col:
            if pd.notna(row['percent_option']):
                # print(key)
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
        country = st.selectbox("Select Country", list(city_defaults['Country'].unique()), key="country")
    with state_col:
        state = st.selectbox("Select State/Province", list(city_defaults[city_defaults['Country'] == country]['State/Province'].unique()), key="state")
    with city_col:
        city = st.selectbox("Select City", list(city_defaults[(city_defaults['Country'] == country) & (city_defaults['State/Province'] == state)]['City'].unique()), key="city")
        
        # Only update values from city data if city has changed
        if city != st.session_state.get('prev_city'):
            if city in city_defaults['City'].values:
                city_data = city_defaults[city_defaults['City'] == city].iloc[0]
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
        if st.button("Reset City") and city in city_defaults['City'].values:
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
        empty_inputs = []
        out_of_bounds_inputs = []
        
        # Check for empty inputs
        for key, value in st.session_state.items():
            if key not in ['summary_data', 'results_df', 'prev_city', 'city_data']:
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    empty_inputs.append(key)
        
        # Check for out-of-bounds values
        for key, value in st.session_state.items():
            if key in variables['key'].values and isinstance(value, (int, float)):
                row = variables[variables['key'] == key].iloc[0]
                
                lower_bound = 0
                if pd.notna(row['lower_bound']):
                    lower_bound = row['lower_bound'] if isinstance(row['lower_bound'], (int, float)) else st.session_state.get(row['lower_bound'], 0)
                
                upper_bound = float('inf')
                if pd.notna(row['upper_bound']):
                    upper_bound = row['upper_bound'] if isinstance(row['upper_bound'], (int, float)) else st.session_state.get(row['upper_bound'], float('inf'))
                
                is_percent_var = key.endswith('_percent') or (row['unit'] == '%' and not pd.notna(row['percent_option']))
                
                if is_percent_var and (value < 0 or value > 100):
                    out_of_bounds_inputs.append(f"{key} (current value: {value})")
                elif not is_percent_var and (value < lower_bound or value > upper_bound):
                    out_of_bounds_inputs.append(f"{key} (current value: {value})")
        non_sensitivity_empty_inputs = [input_key for input_key in empty_inputs if input_key not in 'sensitivity_results']
        if non_sensitivity_empty_inputs:
            # Only throw an error if there are empty inputs that aren't sensitivity parameters
            if non_sensitivity_empty_inputs:
                st.error("Please fill in all required inputs before proceeding")
        elif out_of_bounds_inputs:
            st.error(f"The following inputs are outside their allowed bounds: {', '.join(out_of_bounds_inputs)}")
        else:
            results_df, state_snapshots = run_calculations(st.session_state)
            st.session_state.results_df = results_df
            st.session_state.state_snapshots = state_snapshots
            st.session_state.calculations_done = True
            
            # Initialize sensitivity results but don't run analysis yet
            st.session_state.sensitivity_results = {}
            
            # Get the base 10-year benefit-to-cost ratio for later use
            investment_year = st.session_state.investment_year
            target_year = investment_year + 10
            year_data = results_df[results_df['Year'] == target_year]
            if not year_data.empty:
                st.session_state.base_bcr = year_data.iloc[0]['Benefit_to_Cost_Ratio']
            else:
                st.session_state.base_bcr = None

            script_placeholder = st.empty()
            components.html(f"<script>{switch_tab(2)}</script>", height=0)
            time.sleep(0.2)
            script_placeholder.empty()
with tab3:
    if not st.session_state.get('calculations_done', False):
        st.warning('Please click "Submit" on Input Parameters tab')
    else:
        # Get benefit-to-cost ratio for 10 years after investment year
        ten_year_ratio = None
        investment_year = st.session_state.investment_year
        target_year = investment_year + 10
        
        year_data = st.session_state.results_df[st.session_state.results_df['Year'] == target_year]
        if not year_data.empty:
            ten_year_ratio = year_data.iloc[0]['Benefit_to_Cost_Ratio']
            
        if ten_year_ratio:
            st.info(f"1 {st.session_state.currency} of sanitation investment will yield {ten_year_ratio:.1f} {st.session_state.currency} of return in 10 years")
        
        st.subheader("Dashboard")

        # Add dropdown for value type selection
        value_type = st.selectbox(
            "Select value type", 
            ["City-wide values", "Per capita values"],
            index=0
        )
        show_per_capita = value_type == "Per capita values"
        
        # create cost / benefit / ratio line chart
        df = st.session_state.results_df
        fig = create_line_chart(df, show_per_capita, st.session_state.currency, investment_year)
        st.plotly_chart(fig)
        
        # Create pie charts of benefit and cost components
        if st.session_state.state_snapshots:
            # Get available years from snapshots
            summary_years = [2035, 2040, 2045, 2050, 2055, 2060]
            years = list(range(st.session_state.current_year, 2061))
            
            # Year selector
            selected_year = st.selectbox(
                "Select year to view cost and benefit breakdown:",
                summary_years,
                index=len(summary_years)-1,  # Default to latest year
                key="benefit_cost_year_selector"  # Add unique key to trigger rerun on change
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
                    # If showing per capita values, convert the components to per capita
                    if show_per_capita and 'urban_pop' in st.session_state:
                        per_capita_benefits = {k: v / st.session_state.urban_pop for k, v in selected_benefits.items()}
                        fig_benefits_bar = create_bar_chart(
                            per_capita_benefits,
                            "Cumulative Contribution to Benefits (Per Person)",
                            'green'
                        )
                    else:
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

                    # If showing per capita values, convert the components to per capita
                    if show_per_capita and 'urban_pop' in st.session_state:
                        per_capita_costs = {k: v / st.session_state.urban_pop for k, v in selected_costs.items()}
                        fig_costs_bar = create_bar_chart(
                            per_capita_costs,
                            "Cumulative Contribution to Costs (Per Person)",
                            'grey'
                        )
                    else:
                        fig_costs_bar = create_bar_chart(
                            selected_costs,
                            "Cumulative Contribution to Costs",
                            'grey'
                        )
                    st.plotly_chart(fig_costs_bar)

    # Add "Next" button to go to Input Parameters tabs
    if st.button("Next: Summary"):
        script_placeholder = st.empty()
        components.html(f"<script>{switch_tab(3)}</script>", height=0)
        script_placeholder.empty()

with tab4:
    if not st.session_state.get('calculations_done', False):
        st.warning('Please click "Submit" on Input Parameters tab')
    else:
        # Get benefit-to-cost ratio for 10 years after investment year
        ten_year_ratio = None
        investment_year = st.session_state.investment_year
        target_year = investment_year + 10
        
        year_data = st.session_state.results_df[st.session_state.results_df['Year'] == target_year]
        if not year_data.empty:
            ten_year_ratio = year_data.iloc[0]['Benefit_to_Cost_Ratio']
            
        if ten_year_ratio:
            st.info(f"1 {st.session_state.currency} of sanitation investment will yield {ten_year_ratio:.1f} {st.session_state.currency} of return in 10 years")
            
            # Calculate the number of households without treatment
            households_without_treatment = st.session_state.urban_households * (1 - st.session_state.urban_pop_with_sewer_percent/100)
            households_without_treatment_percent = (households_without_treatment / st.session_state.urban_households) * 100
            
            # Calculate the percentage addressed by sewer vs septic
            sewer_percent = st.session_state.sewer_vs_fstp_percent
            septic_percent = 100 - sewer_percent
            
            # Calculate the percentage of septage going to STP vs FSTP
            septage_to_stp_percent = st.session_state.septage_to_stp_percent if 'septage_to_stp_percent' in st.session_state else 0
            septage_to_fstp_percent = 100 - septage_to_stp_percent
            
            # Add explanatory notes
            st.write(f"There is a {households_without_treatment:,.0f}-household ({households_without_treatment_percent:.1f}%) gap in sanitation access. {sewer_percent:.1f}% of this will be addressed by sewer lines and {st.session_state.gap_treatment_capacity:.2f}MLD additional STP capacity. {septic_percent:.1f}% of this will be addressed by septic systems, with {septage_to_stp_percent:.1f}% of septage taken to STP and {septage_to_fstp_percent:.1f}% taken to FSTP.")
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
                        f'Per-capita Benefits ({st.session_state.currency})': year_data['Cumulative_Benefits_Per_Person'],
                        f'Per-capita Costs ({st.session_state.currency})': year_data['Cumulative_Costs_Per_Person'],
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
                # Update text based on current state before button click
                if 'show_benefits' not in st.session_state:
                    st.session_state.show_benefits = False
                benefits_text = "Hide Benefits Breakdown" if st.session_state.show_benefits else "Show Benefits Breakdown"
                if st.button(benefits_text, key="benefits_button"):
                    st.session_state.show_benefits = not st.session_state.show_benefits
                    st.rerun()

            with col2:
                # Update text based on current state before button click
                if 'show_costs' not in st.session_state:
                    st.session_state.show_costs = False
                costs_text = "Hide Costs Breakdown" if st.session_state.show_costs else "Show Costs Breakdown"
                if st.button(costs_text, key="costs_button"):
                    st.session_state.show_costs = not st.session_state.show_costs
                    st.rerun()

            def generate_breakdown_table(components, year, component_type, show_per_capita):
                """Generate breakdown table for benefits or costs"""
                st.subheader(f"Cumulative {component_type} Breakdown for {year}")
                df = pd.DataFrame({
                    'Component': components.keys(),
                    'Value': components.values()
                })
                if show_per_capita:
                    year_data = st.session_state.results_df[st.session_state.results_df['Year'] == year].iloc[0]
                    population = st.session_state.urban_pop  # Use urban population from session state
                    df['Value'] = df['Value'] / population
                
                # Format the Value column name with currency
                df = df.rename(columns={'Value': f'Value ({st.session_state.currency})'})
                
                st.table(df.style.format({f'Value ({st.session_state.currency})': '{:,.0f}'}).set_table_styles([
                    {'selector': 'thead tr th:first-child', 'props': [('display', 'none')]}, 
                    {'selector': 'tbody tr th:first-child', 'props': [('display', 'none')]}
                ]))

            if st.session_state.show_benefits or st.session_state.show_costs:
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
                    if st.session_state.show_benefits:
                        selected_benefits = None
                        for snapshot in st.session_state.state_snapshots:
                            if snapshot['year'] == selected_year and snapshot.get('cumulative_benefit_components'):
                                selected_benefits = snapshot['cumulative_benefit_components']
                                break
                        
                        if selected_benefits:
                            generate_breakdown_table(selected_benefits, selected_year, "Benefits", show_per_capita_2)

                    # Show costs breakdown if button clicked
                    if st.session_state.show_costs:
                        selected_costs = None
                        for snapshot in st.session_state.state_snapshots:
                            if snapshot['year'] == selected_year and snapshot.get('cumulative_cost_components'):
                                selected_costs = snapshot['cumulative_cost_components']
                                break
                        
                        if selected_costs:
                            generate_breakdown_table(selected_costs, selected_year, "Costs", show_per_capita_2)
        else:
            st.warning("No data available for summary years")

    # Add "Next" button to go to Sensitivity tab
    if st.button("Next: Sensitivity"):
        script_placeholder = st.empty()
        components.html(f"<script>{switch_tab(4)}</script>", height=0)
        script_placeholder.empty()
with tab5:
    # Define sensitivity parameters
    sensitivity_parameters = [
        'sewer_vs_fstp_percent',
        'disease_decrease_percent',
        'water_access_saved',
        'sanitation_access_saved',
        'increase_gdp_tourism_percent',
        'tourism_contribution_percent',
        'days_per_incidence',
        'percent_ulb_officials_trained'
    ]
    if not st.session_state.get('calculations_done', False):
        st.warning('Please click "Submit" on Input Parameters tab')
    else:
        st.subheader("Sensitivity Analysis")
        st.write("This analysis shows how the 10-year benefit-to-cost ratio changes when key parameters are increased or decreased by 20%.")
        
        # Parameter selection
        st.subheader("Select Parameters for Analysis")
        
        # Get all available parameters from variables dataframe that are float or int type
        numeric_parameters = variables[(variables['value_type'].isin(['float', 'int'])) & 
                                      (~variables['key'].isin(['current_year', 'investment_year']))]['key'].tolist()
        
        # Initialize selected parameters in session state if not already present
        if 'selected_sensitivity_params' not in st.session_state:
            # Filter the default sensitivity parameters to only include numeric ones
            default_params = [param for param in sensitivity_parameters if param in numeric_parameters]
            st.session_state.selected_sensitivity_params = default_params
        
        # Create multiselect dropdown for parameter selection
        selected_params = st.multiselect(
            "Choose parameters to include in sensitivity analysis:",
            options=numeric_parameters,
            default=st.session_state.selected_sensitivity_params,
            format_func=lambda x: x.replace('_', ' ').title(),
            key="sensitivity_param_selector"
        )
        
        # Update session state with selected parameters
        st.session_state.selected_sensitivity_params = selected_params
        
        # Display the number of selected parameters
        st.write(f"Selected {len(selected_params)} parameters for sensitivity analysis.")
        # Run sensitivity analysis when user visits this tab
        if st.button("Run Sensitivity Analysis"):
            if not st.session_state.selected_sensitivity_params:
                st.error("Please select at least one parameter for sensitivity analysis.")
            else:
                sensitivity_results = {}
                base_bcr = st.session_state.base_bcr
                
                if base_bcr is not None:
                    # Run sensitivity analysis for each selected parameter one at a time
                    for param in st.session_state.selected_sensitivity_params:
                        if param in st.session_state:
                            # Save original value
                            original_value = st.session_state[param]
                            
                            # Ensure current_year is properly set
                            if 'current_year' not in st.session_state and 'investment_year' in st.session_state:
                                st.session_state['current_year'] = st.session_state['investment_year']
                            
                            # Check if parameter is int type
                            param_type = variables[variables['key'] == param]['value_type'].values[0] if param in variables['key'].values else 'float'
                            
                            # Test with 20% decrease
                            if param_type == 'int':
                                st.session_state[param] = int(original_value * 0.8)
                            else:
                                st.session_state[param] = original_value * 0.8
                                
                            decrease_results, _ = run_calculations(st.session_state)
                            investment_year = st.session_state.investment_year
                            target_year = investment_year + 10
                            decrease_data = decrease_results[decrease_results['Year'] == target_year]
                            decrease_bcr = decrease_data.iloc[0]['Benefit_to_Cost_Ratio'] if not decrease_data.empty else None
                            
                            # Restore original value before testing increase
                            st.session_state[param] = original_value
                            
                            # Test with 20% increase
                            if param_type == 'int':
                                st.session_state[param] = int(original_value * 1.2)
                            else:
                                st.session_state[param] = original_value * 1.2
                                
                            increase_results, _ = run_calculations(st.session_state)
                            increase_data = increase_results[increase_results['Year'] == target_year]
                            increase_bcr = increase_data.iloc[0]['Benefit_to_Cost_Ratio'] if not increase_data.empty else None
                            
                            # Restore original value
                            st.session_state[param] = original_value
                            
                            # Calculate percent changes
                            if decrease_bcr is not None and increase_bcr is not None:
                                decrease_change = (decrease_bcr - base_bcr) / base_bcr * 100
                                increase_change = (increase_bcr - base_bcr) / base_bcr * 100
                                sensitivity_results[param] = {
                                    'decrease': decrease_change,
                                    'increase': increase_change
                                }
                
                # Update session state with results
                st.session_state.sensitivity_results = sensitivity_results
                st.rerun()
            
        if 'sensitivity_results' in st.session_state and st.session_state.sensitivity_results:
            # Create data for tornado chart
            parameters = []
            decrease_values = []
            increase_values = []
            
            # Sort parameters by absolute impact (average of increase and decrease)
            sorted_params = sorted(
                st.session_state.sensitivity_results.items(),
                key=lambda x: abs(x[1]['decrease']) + abs(x[1]['increase']),
                reverse=True
            )
            
            for param, values in sorted_params:
                # Make parameter name more readable
                readable_param = param.replace('_', ' ').title()
                parameters.append(readable_param)
                decrease_values.append(values['decrease'])
                increase_values.append(values['increase'])
            
            # Create tornado chart
            fig = go.Figure()
            
            # Add bars for decrease
            fig.add_trace(go.Bar(
                y=parameters,
                x=decrease_values,
                name='20% Decrease',
                orientation='h',
                marker=dict(color='red'),
                hovertemplate='%{y}: %{x:.1f}% change<extra></extra>'
            ))
            
            # Add bars for increase
            fig.add_trace(go.Bar(
                y=parameters,
                x=increase_values,
                name='20% Increase',
                orientation='h',
                marker=dict(color='green'),
                hovertemplate='%{y}: %{x:.1f}% change<extra></extra>'
            ))
            
            # Update layout to center the plot at x=0
            all_values = decrease_values + increase_values
            max_abs_value = max(abs(min(all_values)), abs(max(all_values)))
            
            fig.update_layout(
                title='Impact on 10-Year Benefit-to-Cost Ratio',
                xaxis=dict(
                    title='Percent Change in Benefit-to-Cost Ratio',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='black',
                    range=[-max_abs_value * 1.1, max_abs_value * 1.1]  # Symmetric range around zero
                ),
                yaxis=dict(
                    title='Parameter',
                    autorange="reversed"  # To have the largest impact at the top
                ),
                barmode='relative',
                bargap=0.1,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=500 + len(parameters) * 25  # Adjust height based on number of parameters
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.write("""
            ### How to interpret this chart:
            - The chart shows how the 10-year benefit-to-cost ratio changes when each parameter is increased or decreased by 20%.
            - Parameters are sorted by their overall impact (largest impact at the top).
            - Red bars (left of center) show the effect of decreasing the parameter by 20%.
            - Green bars (right of center) show the effect of increasing the parameter by 20%.
            - Longer bars indicate parameters that have a greater influence on the results.
            """)
            
            # Add table with numerical values
            st.subheader("Numerical Values")
            
            sensitivity_data = []
            for param, values in sorted_params:
                readable_param = param.replace('_', ' ').title()
                sensitivity_data.append({
                    'Parameter': readable_param,
                    '20% Decrease': f"{values['decrease']:.1f}%",
                    '20% Increase': f"{values['increase']:.1f}%"
                })
            
            sensitivity_df = pd.DataFrame(sensitivity_data)
            st.table(sensitivity_df)
        elif 'sensitivity_results' in st.session_state:
            st.warning("No sensitivity results available. Please run the sensitivity analysis.")
        else:
            st.info("Select parameters above and click 'Run Sensitivity Analysis' to see how changes in parameters affect the results.")
    
    # Add "Next" button to go to Methodology tab
    if st.button("Next: Methodology"):
        script_placeholder = st.empty()
        components.html(f"<script>{switch_tab(5)}</script>", height=0)
        script_placeholder.empty()

with tab6:
    st.markdown(methodology_content.text)
with tab7:
    st.write("#### Sanitation Variables Glossary")
    components.html(doc_content, height=1200, scrolling=True)
with tab8:
    st.write("For support with the SanOpps application, please contact the World Toilet Organization at https://worldtoilet.org")
