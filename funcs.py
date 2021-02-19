from datetime import datetime
from dateutil.relativedelta import relativedelta

kpi_rus = {
    "Sales": "Продажи",
    "Profit": "Прибыль",
    "Customer Name": "Клиенты",
    "Discount": "Скидка",
    "Order ID": "Заказы",
    "Sales Per Customer": "Продажи на клиента",
    "Product Name": "Название товара",
    "Customer Segment": "Сегмент клиента",
    "Product Category": "Категория товара",
    "Product Sub-Category": "Подкатегория товара",
}


def filter_data(category, sub_category, segment, start_date, end_date, df, province):
    filtered_df = df.copy()
    if category is not None:
        filtered_df = filtered_df[filtered_df["Product Category"] == category]
    if sub_category is not None:
        filtered_df = filtered_df[filtered_df["Product Sub-Category"] == sub_category]
    if segment is not None:
        filtered_df = filtered_df[filtered_df["Customer Segment"] == segment]
    if province is not None:
        if "entry" in province["points"][0].keys():
            if province["points"][0]["entry"] == '':
                filtered_df = filtered_df[filtered_df["Province"] == province["points"][0]["customdata"][0]]
    if start_date is not None:
        if type(start_date) == str:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        filtered_df = filtered_df[filtered_df["Order Date"] >= start_date]
    if end_date is not None:
        if type(end_date) == str:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        filtered_df = filtered_df[filtered_df["Order Date"] <= end_date]
    return filtered_df


def get_previous_dates(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    prev_start_date = start_date - relativedelta(years=1)
    prev_end_date = end_date - relativedelta(years=1)
    return prev_start_date, prev_end_date
