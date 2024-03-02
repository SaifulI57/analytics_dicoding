import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import re
import urllib
import os
import glob

sns.set_style('dark')
st.set_option('deprecation.showPyplotGlobalUse',False)

pt = ''.join([os.path.dirname(__file__),'/../data/all_data.csv'])
geo = ''.join([os.path.dirname(__file__),'/../data/geo.csv'])

# dataset
all_data = pd.read_csv(pt)
all_data.sort_values(by='order_approved_at',ascending=False)
all_data.reset_index(inplace=True)
for key in all_data.keys():
    reg =  re.search(r'.*_timestamp|.*_date|.*_at',key)
    if reg:
        all_data[reg.group(0)] = pd.to_datetime(all_data[reg.group(0)])

# Geolocation
geo = pd.read_csv(geo)



date_mi = all_data['order_approved_at'].min()
date_ma = all_data['order_approved_at'].max()

with st.sidebar:
    st.title('Saiful Islam')

    
    start_d, end_d = st.date_input(
        label='Select Date Range',
        value=[date_mi, date_ma],
        min_value=date_mi,
        max_value=date_ma
    )
n_df = all_data[((all_data['order_approved_at'] >= str(start_d)) & (all_data['order_approved_at'] <= str(end_d)))]

def get_rev(data):
    res = data.resample(rule='D',on='order_approved_at').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()
    
    res.rename(columns={
        'order_id':'order_count',
        'payment_value':'revenue'
    },inplace=True)
    return res
def get_oi(data):
    sum_order_df = all_data.groupby(by='product_category_name_english')['payment_value'].sum().reset_index()
    sum_order_df = sum_order_df.sort_values(by='payment_value',ascending=False)
    return sum_order_df
def get_m(data):
    monthly = all_data.resample(rule='ME', on='order_approved_at').agg({
        "order_id": 'nunique',
    })
    monthly.index = monthly.index.strftime('%B')
    monthly = monthly.reset_index()
    monthly.rename(columns={
        "order_id": "order_count",
    }, inplace=True)
    monthly_sum = monthly.groupby(by='order_approved_at')['order_count'].sum().reset_index()
    month_order = [
    'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
    ]
    monthly_sum['order_approved_at'] = pd.Categorical(monthly_sum['order_approved_at'], categories=month_order, ordered=True)
    monthly_sum = monthly_sum.sort_values(by='order_approved_at')
    return monthly_sum
    
st.header('E-Commerce Olist Brazil.')

st.subheader('Daily Order')

col1, col2 = st.columns(2)

dtd = get_rev(n_df)
with col1:
    total_o = dtd['order_count'].sum()
    st.markdown(f'Total Order Count: {total_o}')
    
with col2:
    total_r = dtd['revenue'].sum()
    st.markdown(f'Total Revenue: R${total_r:,.2f}')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    dtd["order_approved_at"],
    dtd["order_count"],
    marker="o",
    linewidth=2,
    color="#BA4D32"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)


st.subheader('Product Income')

col1, col2 = st.columns(2)

doi = get_oi(all_data)

with col1:
    total_oi = round(doi['payment_value'].sum())
    st.markdown(f'Total Income: {total_oi}')

with col2:
    total_oi = round(doi['payment_value'].mean())
    st.markdown(f'Avarage income: {total_oi}')
    
fix, ax = plt.subplots(nrows=1, ncols=2, figsize=(24,6))
color = ['#C14112', '#CCD3D38F','#D7C9D694','#BFE2B683','#A0969B9D']
sns.barplot(x="payment_value",hue='product_category_name_english', y="product_category_name_english",data=doi.head(5),ax=ax[0],palette=color)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title('Product dengan penghasilan terbesar',loc="center",fontsize=16)
ax[0].tick_params(axis='y',labelsize=14)

sns.barplot(x="payment_value",hue='product_category_name_english', y="product_category_name_english",data=doi.sort_values(by='payment_value',ascending=True).head(5),palette=color)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk dengan penghasilan terkecil", loc="center", fontsize=16)
ax[1].tick_params(axis='y', labelsize=14)

st.pyplot(fix)


st.subheader('Review Score')


col1, col2 = st.columns(2)

d_s = all_data['review_score'].value_counts().sort_values(ascending=False)
with col1:
    total_s = d_s.mean()
    st.markdown(f'Average Score: {total_s}')

with col2:
    total_s = d_s.sum()
    st.markdown(f'Total Review: {total_s}')

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=d_s.index,
            y=d_s.values,
            order=d_s.index,
            palette=color[::-1],
            hue=d_s.values
)

plt.title('Rating Score by customer for service')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.xticks(fontsize=14)
st.pyplot(fig)


st.subheader('Performance E-Commerce')

col1, col2 = st.columns(2)

d_m = get_m(all_data)

with col1:
    total_m = d_m['order_count'].mean()
    st.markdown(f'Average order per month: {round(total_m)}')
    
with col2:
    total_m = d_m['order_count'].sum()
    st.markdown(f'Total order: {total_m}')
    
fig, ax = plt.subplots(figsize=(10, 5))
plt.plot(
    d_m["order_approved_at"],
    d_m["order_count"],
    marker='o',
    linewidth=2,
    color='#C76A13'
)
plt.title("Number of Orders per Month", loc="center", fontsize=20)
plt.xticks(fontsize=10, rotation=25)
plt.yticks(fontsize=10)

st.pyplot(fig)



st.subheader('Customer Demographic')

tab1, tab2 = st.tabs(["State",'Geolocation'])

with tab1:
    state_sum = all_data.groupby(by='customer_state').customer_id.nunique().reset_index()
    state_sum.rename(columns={
        "customer_id":"count"
    },inplace=True)
    state_sum = state_sum.sort_values(by='count',ascending=False)
    fig, ax = plt.subplots(figsize=(12,6))
    state_common = state_sum.loc[state_sum['count'].idxmax(),'customer_state']
    sns.barplot(x='customer_state',y='count',hue='customer_state', data=state_sum, palette=["#DB1A2D" if state == state_common else "#9C7070" for state in state_sum['customer_state']])
    plt.title("Number of Customers from Each State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=10)
    st.pyplot(fig)
    
with tab2:
    geo = geo.drop_duplicates(subset='customer_unique_id')
    bz = mpimg.imread(urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
    ax = geo.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10,10), alpha=0.3,s=0.3,c='maroon')
    plt.axis('off')
    plt.imshow(bz, extent=[-73.98283055, -33.8,-33.75116944,5.4])
    st.pyplot()