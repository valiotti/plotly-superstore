import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from datetime import date
import json

card_height_s = '18rem'

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
with open('config.json', 'r') as f:
    config_file = json.load(f)

tablename = config_file['tablename']

df = pd.read_csv("superstore.csv", sep=';')
df = df.dropna()
df["Order Date"] = pd.to_datetime(df["Order Date"])

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
                html.H6("Изменение ключевых показателей YoY по отношению к аналогичному месяцу прошлого года.",
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
                          }),
                dcc.Graph(id='sales-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                          }),
                dcc.Graph(id='orders-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                          }),
                dcc.Graph(id='discount-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',
                          }),
                dcc.Graph(id='clients-indicator',
                          style={
                              'height': '80%',
                              'width': '16%',
                              'float': 'left',

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
            html.H2("Топ провинций по продажам",
                    style={'font-size': 24,
                           'text-align': 'left',
                           },
                    ),
            html.H6("Размер пузырика - это продажи",
                    style={'font-size': 14,
                           'text-align': 'left',
                           'color': '#808080'
                           },
                    ),
            dcc.Graph(id="top-province-bubble-chart")
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
        html.H6("Прибыль и продажи в категории",
                style={'font-size': 14,
                       'text-align': 'left',
                       'color': '#808080'
                       },
                ),
        dcc.Graph(id="sales-category-bar-chart")
    ])
])

sales_by_product = dbc.Card([
    dbc.CardBody([
        html.H2("Топ продуктов по прибыли",
                style={'font-size': 24,
                       'text-align': 'left',
                       },
                ),
        html.H6("Продукты, отсортированные по прибыли.",
                style={'font-size': 14,
                       'text-align': 'left',
                       'color': '#808080'
                       },
                ),
        dcc.Graph(id="sales-product-bar-chart")
    ])
])

clients_profit = dbc.Card([
    dbc.CardBody([
        dcc.Graph(id="top-clients-bar-chart")
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
        ), style={'margin-bottom':'16px'}
    )
],
    style={'margin-left': '16px',
           'margin-right': '16px'}
)
# ---------------------------------------------------------


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
