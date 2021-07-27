from datetime import datetime
from funcs import filter_data, get_previous_dates, kpi_rus
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def get_available_categories(category, df, type_to_get):
    type = ""
    if type_to_get == "Product Category":
        type = "Product Sub-Category"
    elif type_to_get == "Product Sub-Category":
        type = "Product Category"
    if category is not None:
        avlbl_categories = df[df[type] == category][type_to_get].unique()
    else:
        avlbl_categories = df[type_to_get].unique()
    return [{'label': categ, 'value': categ} for categ in sorted(avlbl_categories)]


def create_figure(cy_value, yoy_value, kpi, current_year_data):
    prefix = ''
    suffix = ''
    if kpi in ["Profit", "Sales", "Sales Per Customer"]:
        prefix = '$'
    if kpi in ["Discount"]:
        suffix = '%'
    if kpi in ["Sales Per Customer"]:
        fig = go.Figure(
            go.Scatter(
                x=sorted(current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg(
                    {'Sales': 'mean'}).reset_index()["Order Date"].unique()),
                y=
                current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({'Sales': 'mean'}).reset_index()[
                    "Sales"],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                hoverinfo='skip',
            )
        )
    elif kpi in ["Customer Name"]:
        fig = go.Figure(
            go.Scatter(
                x=sorted(
                    current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'count'}).reset_index()[
                        "Order Date"].unique()),
                y=current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'count'})[kpi],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                hoverinfo='skip',
            )
        )
    elif kpi in ["Discount"]:
        fig = go.Figure(
            go.Scatter(
                x=current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'mean'}).reset_index()[
                    "Order Date"].unique(),
                y=current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'mean'}).reset_index()[
                    "Discount"],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                hoverinfo='skip',
            )
        )

    else:
        fig = go.Figure(
            go.Scatter(
                x=sorted(
                    current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'sum'}).reset_index()[
                        "Order Date"].unique()),
                y=current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'sum'})[kpi],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                hoverinfo='skip',
            )
        )
    fig.add_trace(
        go.Indicator(
            mode='number+delta',
            value=cy_value,
            title={'text': kpi_rus[kpi],
                   'font': {'size': 18,
                            'family': 'sans-serif',
                            },
                   },
            number={'prefix': prefix,
                    'suffix': suffix,
                    'font': {'size': 18,
                             'family': 'sans-serif',
                             },
                    },
            delta={'position': 'left',
                   'reference': yoy_value,
                   'relative': True,
                   'font': {'size': 14,
                            'family': 'sans-serif',
                            },
                   },
            domain={'y': [0, 0.7], 'x': [0.25, 0.75]},
        )
    )

    # SET FONT
    fig.update_layout(autosize=True,
                      font={
                          'family': 'Roboto',
                      },
                      )

    return fig


def get_indicator_plot(df, start_date, end_date, kpi, segment=None, category=None, sub_category=None, province=None):
    prev_start_date, prev_end_date = get_previous_dates(start_date, end_date)
    filtered_df = filter_data(category, sub_category, segment, start_date, end_date, df, province)
    yoy_df = filter_data(category, sub_category, segment, prev_start_date, prev_end_date, df, province)
    year_data = filter_data(category, sub_category, segment, prev_start_date, end_date, df, province)
    if kpi in ["Profit", "Sales"]:
        fig = create_figure(filtered_df[kpi].sum(), yoy_df[kpi].sum(), kpi, year_data)
    elif kpi in ["Discount"]:
        fig = create_figure(filtered_df[kpi].mean() * 100, yoy_df[kpi].mean() * 100, kpi, year_data)
    elif kpi in ["Order ID", "Customer Name"]:
        fig = create_figure(len(filtered_df[kpi].unique()), len(yoy_df[kpi].unique()), kpi, year_data)
    elif kpi in ["Sales Per Customer"]:
        try:
            cy_value = filtered_df["Sales"].sum() / len(filtered_df["Customer Name"].unique())
            yoy_value = yoy_df["Sales"].sum() / len(yoy_df["Customer Name"].unique())
        except ZeroDivisionError:
            cy_value = 0
            yoy_value = 0
        fig = create_figure(cy_value, yoy_value, kpi, year_data)

    fig.update_layout(
        xaxis={'showgrid': False,
               'showticklabels': False},
        yaxis={'showgrid': False,
               'showticklabels': False},
        plot_bgcolor='#FFFFFF',
        margin=dict(l=0, r=0, b=0, t=15),
        autosize=True,
    )
    return fig


def get_top_province_graph(df, start_date, end_date, segment=None, category=None, sub_category=None, type="Sales"):
    filtered_df = filter_data(category, sub_category, segment, start_date, end_date, df, None)
    filtered_df = filtered_df.groupby(["Province"]).agg({"Profit": 'sum', "Sales": 'sum'}).reset_index()
    filtered_df["Sales_lbls"] = ["{}<br>${:.0f}".format(y[1]["Province"],y[1]["Sales"]) for y in filtered_df.iterrows()]
    fig = px.treemap(filtered_df, path=['Sales_lbls'], values=type, custom_data=["Province"], names=type,
                     color=type, color_continuous_scale=px.colors.sequential.Blues,
                     )

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        autosize=True,
    )

    fig.data[0].hovertemplate = '<b></b>%{label}'
    return fig


def get_sales_profit_graph(df, start_date, end_date, segment=None, category=None, sub_category=None, type="Sales",
                           province=None):
    prev_start_date, _ = get_previous_dates(start_date, end_date)
    start_date = datetime.strptime(start_date, '%Y-%m-%d')

    filtered_df = filter_data(category, sub_category, segment, None, None, df, province)
    filtered_df = filtered_df.groupby(pd.Grouper(key='Order Date', freq='M')).agg(
        {type: 'sum'}).reset_index()
    filtered_df_cy = filtered_df[(filtered_df["Order Date"].dt.month == start_date.month) & (
            filtered_df["Order Date"].dt.year == start_date.year)]
    filtered_df_ly = filtered_df[(filtered_df["Order Date"].dt.month == prev_start_date.month) & (
            filtered_df["Order Date"].dt.year == prev_start_date.year)]
    current_value = filtered_df_cy[type].values
    yoy_value = filtered_df_ly[type].values
    filtered_df["formatted_date"] = filtered_df["Order Date"].dt.strftime("%b-%Y")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sorted(filtered_df["Order Date"].values),
                             y=filtered_df[type],
                             mode='lines',
                             name=kpi_rus[type],
                             line={'color': '#0074D9'},
                             text=filtered_df["formatted_date"],
                             hovertemplate='Date %{text}<br>Value: %{y:$.0f}'
                             )
                  )

    fig.add_trace(go.Scatter(x=filtered_df_cy["Order Date"].values,
                             y=current_value, mode='markers',
                             name=f'{kpi_rus[type]} текущий год',
                             marker={'size': 10,
                                     'color': '#0074D9'},
                             text=[start_date.strftime("%b-%Y")],
                             hovertemplate='Date %{text}<br>Value: %{y:$.0f}'
                             ))
    fig.add_trace(go.Scatter(x=filtered_df_ly["Order Date"].values,
                             y=yoy_value,
                             mode='markers',
                             name=f'{kpi_rus[type]} YOY',
                             marker={'size': 10,
                                     'color': '#77dde7'},
                             text=[prev_start_date.strftime("%b-%Y")],
                             hovertemplate='Date %{text}<br>Value: %{y:$.0f}'
                             ))

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        autosize=True,
        yaxis={
            'title': kpi_rus[type],
            'gridcolor': '#e5e5e5',
        },
        xaxis={
            'title': 'Дата',
            'tickmode': 'array',
            'tickvals': sorted([date for i, date in enumerate(filtered_df["Order Date"].values) if i % 2 == 0]),
            'ticktext': [date for i, date in enumerate(filtered_df["formatted_date"]) if i % 2 == 0],
            'tickangle': 30,
            'gridcolor': '#e5e5e5',
        },
        plot_bgcolor='white',
    )

    return fig


def data_bars(df, column):
    n_bins = len(df[column])
    if n_bins == 0:
        return []
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min()
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #0074D9 0%,
                    #0074D9 {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 4,
            'paddingTop': 4
        })

    return styles


def data_bars_diverging(df, column, color_above='#0074D9', color_below='#FF4136'):
    neg_count = len(df[df[column] <= 0]) + 1
    pos_count = len(df[df[column] > 0])
    bounds_neg = np.linspace(0, 0.5, neg_count)
    bounds_pos = np.linspace(0.5, 1, pos_count)
    bounds = np.concatenate((bounds_neg, bounds_pos), axis=0)

    ranges = df[column].to_list()
    ranges.append(0)
    ranges = sorted(ranges)
    midpoint = 0

    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        min_bound_percentage = bounds[i - 1] * 100
        max_bound_percentage = bounds[i] * 100
        style = {
            'if': {
                'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'paddingBottom': 8,
            'paddingTop': 8,
        }
        if max_bound > midpoint:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white 50%,
                    {color_above} 50%,
                    {color_above} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(
                    max_bound_percentage=max_bound_percentage,
                    color_above=color_above
                )
            )
        else:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white {min_bound_percentage}%,
                    {color_below} {min_bound_percentage}%,
                    {color_below} 50%,
                    white 50%,
                    white 100%)
                """.format(
                    min_bound_percentage=min_bound_percentage,
                    color_below=color_below
                )
            )
        style['background'] = background
        styles.append(style)
    return styles
