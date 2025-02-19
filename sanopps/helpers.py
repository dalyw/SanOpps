import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def switch_tab(tab):
    return f"""
    var tabGroup = window.parent.document.getElementsByClassName("stTabs")[0]
    var tab = tabGroup.getElementsByTagName("button")
    tab[{tab}].click()
    """



def create_pie_chart(components, title, colors):
    """Create pie chart with main components and legend for small values"""
    total = sum(components.values())
    main_components = {k:v for k,v in components.items() if (v/total)*100 >= 1}
    legend_components = {k:v for k,v in components.items() if (v/total)*100 < 1}
    
    fig = px.pie(
        values=list(main_components.values()),
        names=list(main_components.keys()),
        color_discrete_sequence=colors,
        hole=0.4 # Add hole in center
    )
    fig.update_traces(textposition='outside', textinfo='percent+label')
    
    # Add title in center of donut
    fig.update_layout(
        showlegend=False,
        height=350,
        margin=dict(t=50, b=50, l=50, r=50),
        annotations=[dict(text=title.replace('\n', '<br>'), x=0.5, y=0.5, font_size=14, showarrow=False)]
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
    total = sum(components.values())
    # Sort items by value in descending order
    sorted_items = sorted(components.items(), key=lambda x: x[1], reverse=True)
    names = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    cumsum = [sum(values[:i+1])/total*100 for i in range(len(values))]
    
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
        # Add margin to fix plot area size
        margin=dict(
            l=80,  # left margin
            r=80,  # right margin
            t=100, # top margin
            b=150  # bottom margin for rotated labels
        ),
        # Fix plot area size
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig