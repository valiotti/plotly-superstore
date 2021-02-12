import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import date
import json
import dash_table
from dash_table.Format import Format, Scheme, Symbol

from funcs import filter_data, get_previous_dates
from graphs_drawer import get_indicator_plot, get_top_province_graph, get_sales_profit_graph, data_bars
from datetime import datetime

pd.options.display.float_format = '${:.2f}'.format
card_height_s = '18rem'

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server
with open('config.json', 'r') as f:
    config_file = json.load(f)

tablename = config_file['tablename']

df = pd.read_csv("superstore.csv", sep=';')
df = df.dropna()
df["Order Date"] = pd.to_datetime(df["Order Date"]).dt.date
df = df.sort_values("Order Date")
print(df.columns)

available_categories = sorted(df["Product Category"].unique())
available_sub_categories = sorted(df["Product Sub-Category"].unique())
available_segments = sorted(df["Customer Segment"].unique())

# FILTERS
date_filter = dbc.FormGroup([
    dbc.Label("Период", html_for="date-filter"),
    dcc.DatePickerRange(
        id="date-filter",
        start_date=date(2010, 4, 1),
        end_date=date(2010, 4, 30),
        display_format='D MMM YYYY',
    )]
)

category_filter = dbc.FormGroup(
    [
        dbc.Label("Категория товара", html_for="category_dropdown"),
        dcc.Dropdown(
            id="category_dropdown",
            placeholder='Все категории',
            value=None,
            options=[{'label': category, 'value': category} for category in available_categories]
        ),
    ],
    className='form-group col-md-6',
)

sub_category_filter = dbc.FormGroup(
    [
        dbc.Label("Подкатегория товара", html_for="sub_category_dropdown"),
        dcc.Dropdown(
            id="sub_category_dropdown",
            placeholder='Все подкатегории',
            value=None,
            options=[{'label': sub_category, 'value': sub_category} for sub_category in available_sub_categories]
        ),
    ],
    className='form-group col-md-6',
)

segment_filter = dbc.FormGroup([
    dbc.Label("Сегмент клиента", html_for="segment_dropdown"),
    dcc.Dropdown(
        id="segment_dropdown",
        placeholder='Все сегменты',
        value=None,
        options=[{'label': segment, 'value': segment} for segment in available_segments],
    ),
],
    style={'max-width': '100%'},
    className='form-group col-md-6',
)

sales_profit_filter = dbc.FormGroup([
    dcc.Dropdown(
        id="sales_profit_dropdown",
        value="Sales",
        options=[{'label': 'Продажи', 'value': 'Sales'}, {'label': 'Прибыль', 'value': 'Profit'}],
    ),

],
    style={'max-width': '100%'},
    # className = 'form-group col-md-6',
)
# -------------------------------------------------
# MARKUP ELEMENTS
kpis_indicators = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H2("KPI",
                        style={'font-size': 24,
                               'text-align': 'left',
                               },
                        ),
                html.H6("Изменение ключевых показателей YoY по отношению к аналогичному месяцу прошлого года. "
                        "На фоне отображена динамика за последний год",
                        style={'font-size': 14,
                               'text-align': 'left',
                               'color': '#808080'
                               },
                        ),
                dcc.Graph(id='profit-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                              'margin-right': '4px',
                          }),
                dcc.Graph(id='sales-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                              'margin-right': '4px',
                          }),
                dcc.Graph(id='orders-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                              'margin-right': '4px',
                          }),
                dcc.Graph(id='discount-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                              'margin-right': '4px',
                          }),
                dcc.Graph(id='clients-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                              'margin-right': '4px',

                          }),
                dcc.Graph(id='sales-per-client-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                          }),
            ],
            style={
                'height': card_height_s,
            },
        ),
    ],
)

top_provinces = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H2("Топ провинций по продажам или прибыли",
                            style={'font-size': 24,
                                   'text-align': 'left',
                                   },
                            ),
                    html.H6(
                        "Размер соответствует продажам или прибыли. Переключаться между продажами и прибылью можно с "
                        "помощью фильтра.",
                        style={'font-size': 14,
                               'text-align': 'left',
                               'color': '#808080'
                               },
                    ),
                ], width=8),
                dbc.Col([
                    sales_profit_filter,
                ], width=4)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="top-province-bubble-chart"))
            ])

        ])
    ])

sales_and_profit = dbc.Card([
    dbc.CardBody([
        html.H2("Динамика прибыли и продаж",
                style={'font-size': 24,
                       'text-align': 'left',
                       },
                ),
        html.H6("Тут динамика по прибыли и продажам",
                style={'font-size': 14,
                       'text-align': 'left',
                       'color': '#808080'
                       },
                ),
        dcc.Graph(id="sales-profit-bar-chart")
    ])
])

sales_by_category = dbc.Card([
    dbc.CardBody([
        html.H2("Прибыль и продажи по категориям",
                style={'font-size': 24,
                       'text-align': 'left',
                       },
                ),
        html.H6("Прибыль и продажи в категории. Можно изменять сортировку, нажимая на заголовки столбцов.",
                style={'font-size': 14,
                       'text-align': 'left',
                       'color': '#808080'
                       },
                ),
        dash_table.DataTable(
            id='category-sales',
            sort_action='native',
            columns=[{'name': i, 'id': i, 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed,
                                                                              symbol=Symbol.yes, symbol_prefix=u'$')}
                     for i in ["Product Category", "Product Sub-Category", "Sales", "Profit"]],
            style_data_conditional=(
                    data_bars(df, 'Sales') +
                    data_bars(df, 'Profit')
            ),
            style_cell={
                'width': '100px',
                'minWidth': '100px',
                'maxWidth': '100px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            page_size=20,
        )
    ])
])

sales_by_product = dbc.Card([
    dbc.CardBody([
        html.H2("Топ продуктов по прибыли",
                style={'font-size': 24,
                       'text-align': 'left',
                       },
                ),
        html.H6("Продукты, отсортированные по прибыли. Можно изменять сортировку, нажимая на заголовки столбцов.",
                style={'font-size': 14,
                       'text-align': 'left',
                       'color': '#808080'
                       },
                ),
        dash_table.DataTable(
            id='top-product-sales',
            sort_action='native',
            columns=[{'name': i, 'id': i, 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed,
                                                                              symbol=Symbol.yes, symbol_prefix=u'$')}
                     for i in ["Product Name", "Profit"]],
            style_data_conditional=(
                data_bars(df, 'Profit')
            ),
            style_cell={
                'width': '100px',
                'minWidth': '100px',
                'maxWidth': '100px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            page_size=15,
        )

    ])
])

clients_profit = dbc.Card([
    dbc.CardBody([
        dash_table.DataTable(
            id='top-clients',
            sort_action='native',
            columns=[{'name': i, 'id': i, 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed,
                                                                              symbol=Symbol.yes, symbol_prefix=u'$')}
                     for i in ["Customer Segment", "Customer Name", "Profit"]],
            style_data_conditional=(
                data_bars(df, 'Profit')
            ),
            style_cell={
                'width': '100px',
                'minWidth': '100px',
                'maxWidth': '100px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            page_size=15,
        )
    ])
])
# --------------------------------------
# LAYOUT
app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col([
            html.H2(
                config_file['themeSettings'][0]['title'],
                style={
                    "text-align": "left",
                    "font-size": 24,
                }
            ),
            html.H4(
                config_file['themeSettings'][0]['description'],
                style={
                    "text-align": "left",
                    'font-size': 16,
                    "color": "#808080",
                }
            ),
        ], width=10, style={'margin-top': '8px'}),
        dbc.Col([
            date_filter,
        ], width=2)
    ], style={'margin-top': '8px',
              'margin-bottom': '16px'}
    ),
    dbc.Row([
        dbc.Col([
            kpis_indicators,
        ]),
    ], style={'margin-bottom': '16px'}),
    dbc.Row([
        dbc.Col([
            top_provinces,
        ], width=6),
        dbc.Col([
            sales_and_profit,
        ], width=6)
    ], style={'margin-bottom': '16px'}),
    dbc.Row([
        dbc.Col([
            html.H2("Анализ продуктов и клиентов",
                    style={'font-size': 24,
                           'text-align': 'left',
                           },
                    ),
            html.H6("Обзор наиболее эффективных продуктов и клиентов по продажам и прибыли с группировкой по "
                    "товарным категориям и клиентским сегментам.",
                    style={'font-size': 14,
                           'text-align': 'left',
                           'color': '#808080'
                           },
                    ),
        ], width=8),
        dbc.Col([
            dbc.Row([
                category_filter,
                sub_category_filter,
            ])
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            sales_by_category,
        ], width=6),
        dbc.Col([
            sales_by_product,
        ], width=6),
    ], style={'margin-bottom': '16px'}),
    dbc.Row([
        dbc.Col([
            html.H2("Топ клиентов по прибыли",
                    style={'font-size': 24,
                           'text-align': 'left',
                           },
                    ),
            html.H6("Имена клиентов, отсортированные по прибыли. Выберите из списка определенный сегмент, "
                    "чтобы увидеть клиентов только по нему.",
                    style={'font-size': 14,
                           'text-align': 'left',
                           'color': '#808080'
                           },
                    ),
        ], width=10),
        dbc.Col([
            segment_filter,
        ], width=2)
    ]),
    dbc.Row(
        dbc.Col(
            clients_profit
        ), style={'margin-bottom': '16px'}
    )
],
    style={'margin-left': '16px',
           'margin-right': '16px'}
)


# ---------------------------------------------------------
# CALLBACKS

@app.callback(
    Output('profit-indicator', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_profit_indicator(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_indicator_plot(df, start_date, end_date, "Profit", segment, category, sub_category)


@app.callback(
    Output('sales-indicator', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_sales_indicator(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_indicator_plot(df, start_date, end_date, "Sales", segment, category, sub_category)


@app.callback(
    Output('orders-indicator', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_profit_indicator(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_indicator_plot(df, start_date, end_date, "Order ID", segment, category, sub_category)


@app.callback(
    Output('discount-indicator', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_profit_indicator(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_indicator_plot(df, start_date, end_date, "Discount", segment, category, sub_category)


@app.callback(
    Output('clients-indicator', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_profit_indicator(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_indicator_plot(df, start_date, end_date, "Customer Name", segment, category, sub_category)


@app.callback(
    Output('sales-per-client-indicator', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_profit_indicator(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_indicator_plot(df, start_date, end_date, "Sales Per Customer", segment, category, sub_category)


@app.callback(
    Output('top-province-bubble-chart', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date'),
        Input('sales_profit_dropdown', 'value')
    ]
)
def update_province_graph(category, sub_category, segment, start_date, end_date, type):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_top_province_graph(df, start_date, end_date, segment, category, sub_category, type)


@app.callback(
    Output('sales-profit-bar-chart', 'figure'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_sales_profit_graph(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    return get_sales_profit_graph(df, start_date, end_date, segment, category, sub_category)


@app.callback(
    Output('category-sales', 'data'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_sales_profit_graph(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    filtered_data = filter_data(category, sub_category, segment, start_date, end_date, df)
    filtered_data = filtered_data.groupby(["Product Category", "Product Sub-Category"]).agg(
        {"Sales": 'sum', "Profit": 'sum'}).reset_index()
    return filtered_data.to_dict('records')


@app.callback(
    Output('top-product-sales', 'data'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_sales_profit_graph(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    filtered_data = filter_data(category, sub_category, segment, start_date, end_date, df)
    filtered_data = filtered_data.groupby("Product Name").agg({"Profit": 'sum'}).reset_index()
    filtered_data = filtered_data.sort_values("Profit", ascending=False)
    return filtered_data.to_dict('records')


@app.callback(
    Output('top-clients', 'data'),
    [
        Input('category_dropdown', 'value'),
        Input('sub_category_dropdown', 'value'),
        Input('segment_dropdown', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date')
    ]
)
def update_sales_profit_graph(category, sub_category, segment, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    start_date = start_date.date()

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    filtered_data = filter_data(category, sub_category, segment, start_date, end_date, df)
    filtered_data = filtered_data.groupby(["Customer Segment", "Customer Name"]).agg({"Profit": 'sum'}).reset_index()
    filtered_data = filtered_data.sort_values("Profit", ascending=False)
    return filtered_data.to_dict('records')


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
