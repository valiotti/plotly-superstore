import plotly.graph_objects as go
from funcs import filter_data, get_previous_dates
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pandas import Grouper, DatetimeIndex
from plotly.subplots import make_subplots


def create_figure(cy_value, yoy_value, kpi, current_year_data):

    prefix = ''
    suffix = ''
    value_format = '{}'
    if kpi in ["Profit", "Sales", "Sales Per Customer"]:
        prefix = '$'
    if kpi in ["Discount"]:
        suffix = '%'
        value_format = '.1f'
    if kpi in ["Sales Per Customer"]:
        fig = go.Figure(
            go.Scatter(
                x=sorted(current_year_data.groupby(pd.Grouper(key='Order Date',freq='M')).agg({'Sales':'mean'}).reset_index()["Order Date"].unique()),
                y=current_year_data.groupby(pd.Grouper(key='Order Date',freq='M')).agg({'Sales':'mean'}).reset_index()["Sales"],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                # text=[f'<b>{prefix}{y}{suffix}' for y in current_year_data.groupby("Customer Name").agg({'Sales': 'mean'})["Sales"]],
                hovertemplate='Динамика за выбранный период<br>%{text}',
            )
        )
    elif kpi in ["Customer Name"]:
        fig = go.Figure(
            go.Scatter(
                x=sorted(current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'count'}).reset_index()[
                        "Order Date"].unique()),
                y=current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'count'})[kpi],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                text=[f'<b>{prefix}{value_format.format(y)}{suffix}' for y in current_year_data[kpi]],
                hovertemplate='Динамика за выбранный период<br>%{text}',
            )
        )
    elif kpi in ["Discount"]:
        fig = go.Figure(
            go.Scatter(
                x=current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'mean'}).reset_index()["Order Date"].unique(),
                y=current_year_data.groupby(pd.Grouper(key='Order Date', freq='M')).agg({kpi: 'mean'}).reset_index()["Discount"],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                text=[f'<b>{prefix}{value_format.format(y)}{suffix}' for y in current_year_data[kpi]],
                hovertemplate='Динамика за выбранный период<br>%{text}',
            )
        )

    else:
        fig = go.Figure(
            go.Scatter(
                x=sorted(current_year_data.groupby(pd.Grouper(key='Order Date',freq='M')).agg({kpi:'sum'}).reset_index()["Order Date"].unique()),
                y=current_year_data.groupby(pd.Grouper(key='Order Date',freq='M')).agg({kpi:'sum'})[kpi],
                mode='lines',
                fill='tozeroy',
                line_color='#E8E8E8',
                name='',
                text=[f'<b>{prefix}{value_format.format(y)}{suffix}' for y in current_year_data[kpi]],
                hovertemplate='Динамика за выбранный период<br>%{text}',
            )
        )

    fig.add_trace(
        go.Indicator(
            mode='number+delta',
            value=cy_value,
            title={'text': kpi,
                   'font': {'size': 17, },
                   },
            number={'prefix': prefix,
                    'suffix': suffix,
                    'font': {'size': 17, },
                    },
            delta={'position': 'left',
                   'reference': yoy_value,
                   'relative': True,
                   # 'valueformat': "{:10.4f}",
                   'font': {'size': 13, },
                   },
            domain={'y': [0, 0.7], 'x': [0.25, 0.75]},
        )
    )

    # SET FONT
    fig.update_layout(autosize=True,
                      font={
                          'family': 'Lato',
                      },
                      )

    return fig


def get_indicator_plot(df, start_date, end_date, kpi, segment=None, category=None, sub_category=None):
    filtered_df = filter_data(category, sub_category,segment, start_date, end_date, df)
    prev_start_date, prev_end_date = get_previous_dates(start_date, end_date)
    yoy_df = filter_data(category, sub_category, segment, prev_start_date, prev_end_date, df)
    year_data = filter_data(category, sub_category, segment, prev_start_date, end_date, df)
    # data_for_graph = filter_data(category, sub_category, segment, prev_start_date, end_date, df)
    if kpi in ["Profit", "Sales"]:
        # print("YOY ", kpi, yoy_df[kpi].sum())
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
    filtered_df = filter_data(category, sub_category,segment, start_date, end_date, df)
    filtered_df = filtered_df.groupby("Province").agg({"Profit" : 'sum', "Sales": 'sum'}).reset_index()
    fig = px.treemap(filtered_df, path=['Province'], values=type)
    return fig


def get_sales_profit_graph(df, start_date, end_date, segment=None, category=None, sub_category=None):
    filtered_df = filter_data(category, sub_category,segment, None, None, df)
    prev_start_date, _ = get_previous_dates(start_date, end_date)
    filtered_df = filtered_df.groupby('month-year').agg({"Profit" : 'sum', "Sales": 'sum'}).reset_index()
    current_sales = filtered_df[filtered_df["month-year"] == start_date.strftime("%Y-%b")]["Sales"].values
    current_profit = filtered_df[filtered_df["month-year"] == start_date.strftime("%Y-%b")]["Profit"].values
    yoy_sales = filtered_df[filtered_df["month-year"] == prev_start_date.strftime("%Y-%b")]["Sales"].values
    yoy_profit = filtered_df[filtered_df["month-year"] == prev_start_date.strftime("%Y-%b")]["Profit"].values

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_df["month-year"].values, y=filtered_df["Sales"],
                             mode='lines',
                             name='Продажи'))
    fig.add_trace(go.Scatter(x=filtered_df["month-year"].values, y=filtered_df["Profit"],
                             mode='lines',
                             name='Прибыль'))
    fig.add_trace(go.Scatter(x=[start_date.strftime("%Y-%b")], y=current_sales, mode='markers', name='current_sales', marker={'size':10}))
    fig.add_trace(go.Scatter(x=[start_date.strftime("%Y-%b")], y=current_profit, mode='markers',name='current_profit', marker={'size':10}))
    fig.add_trace(go.Scatter(x=[prev_start_date.strftime("%Y-%b")], y=yoy_sales, mode='markers', name='yoy_sales', marker={'size':10}))
    fig.add_trace(go.Scatter(x=[prev_start_date.strftime("%Y-%b")], y=yoy_profit, mode='markers', name='yoy_profit', marker={'size':10}))
    return fig


def data_bars(df, column):
    n_bins = 100
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
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles
