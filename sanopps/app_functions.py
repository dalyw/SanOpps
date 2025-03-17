import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

conversion_rates = {
    'INR': 1,
    'USD': 83.28,  # 1 USD = 83.28 INR
    'EUR': 89.13   # 1 EUR = 89.13 INR
}

def initialize_session_state(keys, default_values):
    for key, default_value in zip(keys, default_values):
        if key not in st.session_state:
            st.session_state[key] = default_value

def switch_tab(tab):
    """ Used to trigger a button to switch to a different tab """
    return f"""
    var tabGroup = window.parent.document.getElementsByClassName("stTabs")[0]
    var tab = tabGroup.getElementsByTagName("button")
    tab[{tab}].click()
    """


def create_pie_chart(components, title, colors):
    """Create pie chart with main components of cost / benefit """
    filtered_components = {k: v for k, v in components.items() if k != 'Total'}
    total = components['Total']
    
    formatted_components = {}
    for k,v in filtered_components.items():
        if len(k) > 10: # add line breaks to longer components based on multiples of 10 characters
            num_splits = (len(k) - 1) // 10
            split_k = k
            for i in range(num_splits):
                start_pos = i * 10
                space_index = split_k.find(' ', start_pos)
                if space_index != -1:
                    split_k = split_k[:space_index] + '<br>' + split_k[space_index+1:]
            k = split_k
        formatted_components[k] = v
    main_components = {k:v for k,v in formatted_components.items() if (v/total)*100 >= 1}
    legend_components = {k:v for k,v in formatted_components.items() if (v/total)*100 < 1}
    
    fig = px.pie(
        values=list(main_components.values()),
        names=list(main_components.keys()),
        color_discrete_sequence=colors,
        hole=0.4
    )
    fig.update_traces(textposition='outside', textinfo='percent+label', textfont_color='black')
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(t=50, b=50, l=80, r=80), # add buffer to left and right to avoid cutting off labels
        annotations=[dict(text=title.replace('\n', '<br>'), x=0.5, y=0.5, font_size=14, showarrow=False, font=dict(color='black'))]
    )
    
    if legend_components:
        for name, value in legend_components.items():
            percentage = (value/total)*100
            fig.add_trace(go.Pie(
                values=[value],
                name=f"{name} ({percentage:.1f}%)",
                showlegend=False,
                visible=False
            ))
    return fig

def create_bar_chart(components, title, bar_color):
    """Create bar chart with cumulative percentage line"""
    filtered_components = {k: v for k, v in components.items() if k != 'Total'}
    
    # Sort items by value in descending order
    sorted_items = sorted(filtered_components.items(), key=lambda x: x[1], reverse=True)
    names = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    cumsum = [sum(values[:i+1])/ components['Total']*100 for i in range(len(values))]
    
    fig = go.Figure()
    fig.add_bar(
        x=names,
        y=values,
        name="Value",
        marker_color=bar_color
    )
    fig.add_scatter(
        x=names,
        y=cumsum,
        name="Cumulative %",
        yaxis="y2",
        line=dict(color='black')
    )
    fig.update_layout(
        title=title,
        yaxis=dict(title=f"Value ({st.session_state.currency})"),
        yaxis2=dict(
            title="Cumulative %", 
            overlaying="y", 
            side="right", 
            range=[0,105],
            tickfont=dict(color='black'),
            titlefont=dict(color='black')
        ),
        showlegend=False,
        height=400,
        width=800,
        xaxis=dict(
            tickangle=45
        ),
        margin=dict(
            l=80,  # left margin
            r=80,  # right margin
            t=100, # top margin
            b=150  # bottom margin for rotated labels
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig