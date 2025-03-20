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

# Plotting functions developed with support from Claude 3.7
def create_line_chart(df, show_per_capita, currency, investment_year):
    """
    Create a line chart showing cumulative benefits, costs, and benefit-to-cost ratio.
    
    Parameters:
    - df: DataFrame containing the results data
    - show_per_capita: Boolean indicating whether to show per capita values
    - currency: Currency symbol to use in labels
    - investment_year: The year when investment started
    
    Returns:
    - fig: Plotly figure object ready to be displayed
    """
    # Create figure with secondary y-axis
    if show_per_capita:
        fig = px.line(df, x="Year", y=["Cumulative_Benefits_Per_Person", "Cumulative_Costs_Per_Person"])
    else:
        fig = px.line(df, x="Year", y=["Cumulative_Total_Benefit", "Cumulative_Total_Cost"])
    
    # Add benefit-to-cost ratio on secondary y-axis
    fig.add_scatter(
        x=df["Year"], 
        y=df["Benefit_to_Cost_Ratio"],
        name="Benefit-to-Cost Ratio",
        yaxis="y2",
        hovertemplate='%{y:,.1f}<extra></extra>'
    )

    # Find intersection year where benefits exceed costs
    benefits = df["Cumulative_Benefits_Per_Person"] if show_per_capita else df["Cumulative_Total_Benefit"]
    costs = df["Cumulative_Costs_Per_Person"] if show_per_capita else df["Cumulative_Total_Cost"]
        
    # Find first year where benefits exceed costs
    intersection_year = None
    for i in range(len(df)):
        if benefits.iloc[i] >= costs.iloc[i] and benefits.iloc[i] > 0 and costs.iloc[i] > 0:
            intersection_year = df["Year"].iloc[i]
            break
            
    if intersection_year:
        # Add vertical line at intersection and ROI annotation
        fig.add_shape(
            type="line", x0=intersection_year, x1=intersection_year,
            y0=0, y1=1, yref="paper", line=dict(color="black")
        )
        
        fig.add_annotation(
            x=intersection_year + 4, y=0.8, yref="paper",
            text=f"{intersection_year - investment_year}-year ROI",
            showarrow=False, font=dict(color='black', size=16)
        )

    # Update layout
    fig.update_layout(
        title=dict(text="Return on WASH Investment", font=dict(size=24)),
        xaxis_title=dict(text="Year", font=dict(size=18)),
        yaxis_title=dict(
            text=f"Cost and Benefit in {currency}/person" if show_per_capita else currency,
            font=dict(size=18)
        ),
        yaxis2=dict(
            title=dict(text="Benefit-to-Cost Ratio", font=dict(size=18, color='blue')),
            overlaying="y", side="right", showgrid=False, tickfont=dict(size=14, color='blue')
        ),
        yaxis=dict(showgrid=True, gridcolor='lightgrey', tickfont=dict(size=14, color='black')),
        xaxis=dict(dtick=10, showgrid=False, tickfont=dict(size=14)),
        showlegend=False,
        hovermode='x unified',
        hoverlabel=dict(font_size=14)
    )

    # Update line styles for benefits and costs
    fig.data[0].update(line_color='green', name='Cumulative Benefits', mode='lines', hovertemplate='Cumulative: %{y:,.0f}<extra></extra>')
    fig.data[1].update(line_color='grey', name='Cumulative Costs', mode='lines', hovertemplate='Cumulative: %{y:,.0f}<extra></extra>')
    fig.data[2].update(line_color='blue', mode='lines', line=dict(width=5), yaxis='y2')

    # Add text labels at end of lines
    last_x = df["Year"].iloc[-1]
    
    # Label for benefits and costs
    for i in range(2):
        trace = fig.data[i]
        last_y = trace.y[-1]
        x_pos = last_x + 2
        
        fig.add_annotation(
            x=x_pos, y=last_y, text=trace.name,
            showarrow=False, font=dict(color=trace.line.color, size=16),
            xanchor='left', yanchor='middle', yref='y'
        )
    
    # Label for benefit-to-cost ratio
    last_ratio = df["Benefit_to_Cost_Ratio"].iloc[-1]
    fig.add_annotation(
        x=last_x - 3, y=last_ratio, text="Benefit-to-Cost Ratio",
        showarrow=False, font=dict(color='blue', size=16),
        xanchor='right', yanchor='middle', yref='y2'
    )
    
    return fig


def create_pie_chart(components, title, colors):
    """Create pie chart with main components of cost / benefit """
    filtered_components = {k: v for k, v in components.items() if k != 'Total'}
    total = components['Total']
    formatted_components = {}
    for k, v in filtered_components.items():
        if len(k) > 20:  # add line breaks to longer components
            words = k.split()
            total_chars = sum(len(word) for word in words) + len(words) - 1
            chars_per_line = total_chars / (len(k) // 20 + 1)
            
            current_line = ""
            split_k = ""
            
            for word in words:
                if len(current_line) + len(word) > chars_per_line and current_line:
                    split_k += current_line.strip() + "<br>"
                    current_line = ""
                current_line += word + " "
            
            split_k += current_line.strip()
            k = split_k
        formatted_components[k] = v
    
    main_components = {k: v for k, v in formatted_components.items() 
                      if (v/total)*100 >= 1}
    legend_components = {k: v for k, v in formatted_components.items() 
                        if (v/total)*100 < 1}
    fig = px.pie(
        values=list(main_components.values()),
        names=list(main_components.keys()),
        color_discrete_sequence=colors,
        hole=0.6
    )
    fig.update_traces(textposition='outside', textinfo='percent+label', textfont_color='black', hovertemplate='%{label}<br>Value: %{value:,.0f}<extra></extra>')
    fig.update_layout(
        showlegend=False,
        height=450,
        margin=dict(t=50, b=50, l=100, r=100), # increased left and right margins for labels
        annotations=[dict(text=title.replace('\n', '<br>'), x=0.5, y=0.5, font_size=14, showarrow=False, font=dict(color='black'))],
        autosize=False,
        width=600  # make pie chart slightly smaller to allow room for labels
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
        marker_color=bar_color,
        hovertemplate='%{x}<br>Value: %{y:,.0f}<extra></extra>'
    )
    fig.add_scatter(
        x=names,
        y=cumsum,
        name="Cumulative %",
        yaxis="y2",
        line=dict(color='black'),
        hovertemplate='%{x}<br>Cumulative: %{y:,.0f}%<extra></extra>'
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