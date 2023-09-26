import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

hour_df = pd.read_csv("hour_data.csv")
day_df = pd.read_csv("day_data.csv")

datetime_columns = ["dteday"]
for column in datetime_columns:
  day_df[column] = pd.to_datetime(day_df[column])

datetime_columns = ["dteday"]
for column in datetime_columns:
  hour_df[column] = pd.to_datetime(hour_df[column])

def create_sum_season_cnt_df(df):
    sum_season_cnt_df = day_df.groupby("season").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_season_cnt_df

def create_sum_mnth_cnt_df(df):
    sum_mnth_cnt_df = day_df.groupby("mnth").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_mnth_cnt_df

def create_sum_hr_cnt_df(df):
    sum_hr_cnt_df = hour_df.groupby("hr").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_hr_cnt_df


def create_sum_hr_casreg_df(df):
    sum_hr_casreg_df = df.groupby(["hr", "workingday"])[["casual", "registered"]].sum()
    sum_hr_casreg_df = sum_hr_casreg_df.reset_index()
    sum_hr_casreg_df = sum_hr_casreg_df.sort_values(by=["hr", "workingday"], ascending=[True, True])
    return sum_hr_casreg_df

def create_rfm_df(day_df):
    rfm_df = day_df.groupby("weekday").agg({
       "dteday": "max",
       "instant": "nunique",
       "cnt": "sum"
    })

    rfm_df.columns = ["max_order_timestamp", "monetary", "frequency"]
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"])
    recent_date = day_df["dteday"].max()
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

min_date = hour_df["dteday"].min()
max_date = hour_df["dteday"].max()
 
with st.sidebar:
   
    st.image("https://image.spreadshirtmedia.com/image-server/v1/mp/products/T1302A1PA2669PT24X0Y0D1028855787W20718H20718/views/1,width=800,height=800,appearanceId=1,backgroundColor=F2F2F2/road-bike-logo-black-poster.jpg")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main1_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                (hour_df["dteday"] <= str(end_date))]
main2_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

sum_season_cnt_df = create_sum_season_cnt_df(main2_df)
sum_mnth_cnt_df = create_sum_mnth_cnt_df(main2_df)
sum_hr_cnt_df = create_sum_hr_cnt_df(main1_df)
sum_hr_casreg_df = create_sum_hr_casreg_df(main1_df)
rfm_df = create_rfm_df(main2_df)

st.header('Bike-sharing Dashboard :sparkles:')

st.subheader("Count of Total Month & Season")
 
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_ = ["dodgerblue"] + ["lightgray"] * (len(sum_season_cnt_df) - 1)

    sns.barplot(
        y="cnt", 
        x="season",
    data=sum_season_cnt_df,
    order=sum_season_cnt_df.sort_values(by="cnt", ascending=False)["season"],
    palette=colors_,
    ax=ax
    )
    ax.set_title("Count of Total by Season", loc="center", fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_ = ["dodgerblue"] + ["lightgray"] * (11)
    
    sns.barplot(
        x="mnth", 
        y="cnt",
    data=sum_mnth_cnt_df,
    order=sum_mnth_cnt_df.sort_values(by="cnt", ascending=False)["mnth"],
    palette=colors_,
    ax=ax
    )
    ax.set_title("Count of Total by Month", loc="center", fontsize=15)
    ax.set_label(None)
    ax.set_label(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

st.subheader("Best & Worst Performing Hour")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="hr", y="cnt", data=sum_hr_cnt_df,
            order=sum_hr_cnt_df.sort_values(by="cnt", ascending=False)["hr"].head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total of Count", fontsize=30)
ax[0].set_title("Best Performing Hour", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="hr", y="cnt", data=sum_hr_cnt_df,
            order=sum_hr_cnt_df.sort_values(by="cnt", ascending=True)["hr"].head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total of Count", fontsize=30)
ax[1].set_title("Worst Performing Hour", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

st.subheader("Comparison of Casual and Registered per Hour (2011-2012)")

fig, ax = plt.subplots(figsize=(30, 15))
sns.lineplot(
    x=sum_hr_casreg_df["hr"],
    y=sum_hr_casreg_df["casual"],
    marker='o', 
    linewidth=2,
    color="#FFA500",
    label="Casual",
    ax=ax
)
sns.lineplot(
    x=sum_hr_casreg_df["hr"],
    y=sum_hr_casreg_df["registered"],
    marker='o', 
    linewidth=2,
    color="#008000",
    label="Registered",
    ax=ax
)
ax.set_title("Comparison of Casual and Registered per Hour (2011-2012)", loc="center", fontsize=30)
ax.tick_params(axis='x', labelsize=30) 
ax.tick_params(axis='y', labelsize=30)
ax.set_ylabel("Total", fontsize=30) 
ax.set_xlabel("Hour", fontsize=30)
ax.legend(fontsize=30)

st.pyplot(fig)

st.subheader("Best Weekday Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x=rfm_df.index[:5], data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("weekday", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x=rfm_df.index[:5], data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("weekday", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x=rfm_df.index[:5], data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("weekday", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Suryansyah Suciono')
