import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

kpi_rus = {
    "Sales": "Продажи",
    "Profit": "Прибыль",
    "Customer Name": "Клиенты",
    "Discount": "Скидка",
    "Order ID": "Заказы",
    "Sales Per Customer": "Продажи на клиента",
}


def filter_data(category, sub_category, segment, start_date, end_date, df):
    filtered_df = df.copy()
    if category is not None:
        filtered_df = filtered_df[filtered_df["Product Category"] == category]
    if sub_category is not None:
        filtered_df = filtered_df[filtered_df["Product Sub-Category"] == sub_category]
    if segment is not None:
        filtered_df = filtered_df[filtered_df["Customer Segment"] == segment]
    if start_date is not None:
        filtered_df = filtered_df[filtered_df["Order Date"] >= start_date]
    if end_date is not None:
        filtered_df = filtered_df[filtered_df["Order Date"] <= end_date]
    filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"])
    filtered_df["month-year"] = filtered_df["Order Date"].dt.strftime('%Y-%b')
    return filtered_df


def get_previous_dates(start_date, end_date):
    prev_start_date = start_date - relativedelta(years=1)
    prev_end_date = end_date - relativedelta(years=1)
    return prev_start_date, prev_end_date
