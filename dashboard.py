import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("all_df.csv")  # Sesuaikan dengan nama file yang benar
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['year'] = df['order_purchase_timestamp'].dt.year
    df['month'] = df['order_purchase_timestamp'].dt.strftime('%Y-%m')
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", ['All'] + sorted(df['year'].unique()), index=0)
if selected_year == 'All':
    filtered_df = df.copy()
    available_months = ['All'] + sorted(df['month'].unique())
else:
    filtered_df = df[df['year'] == selected_year]
    available_months = ['All'] + sorted(filtered_df['month'].unique())
selected_month = st.sidebar.selectbox("Select Month", available_months)
selected_category = st.sidebar.multiselect("Select Product Categories", df['product_category_name_english'].unique(), default=df['product_category_name_english'].unique())

# Apply filters
filtered_df = filtered_df[filtered_df['product_category_name_english'].isin(selected_category)]
if selected_month != 'All':
    filtered_df = filtered_df[filtered_df['month'] == selected_month]

# KPI Metrics
st.title("📊 E-Commerce Sales Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${filtered_df['total_order_value'].sum():,.2f}")
col2.metric("Total Orders", f"{filtered_df['order_id'].nunique()}")
col3.metric("Unique Customers", f"{filtered_df['customer_unique_id'].nunique()}")

# Sales Trends
st.subheader("📈 Monthly Sales Trends")
monthly_sales = filtered_df.groupby('month')['total_order_value'].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x='month', y='total_order_value', data=monthly_sales, marker='o', ax=ax)
ax.set_xticklabels(monthly_sales['month'], rotation=45)
st.pyplot(fig)

# Best & Least Sold Products
st.subheader("🛍️ Top & Bottom Product Categories")
category_sales = filtered_df.groupby('product_category_name_english')['product_id'].nunique().reset_index().sort_values(by='product_id', ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=category_sales['product_category_name_english'].head(5), x=category_sales['product_id'].head(5), ax=ax, palette='Greens')
ax.set_title("Top 5 Best Selling Categories")
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=category_sales['product_category_name_english'].tail(5), x=category_sales['product_id'].tail(5), ax=ax, palette='Reds')
ax.set_title("Bottom 5 Least Selling Categories")
st.pyplot(fig)

# RFM Analysis (Top Customers)
st.subheader("🏆 Top Customers Based on RFM")
top_customers = filtered_df.groupby('customer_unique_id').agg(
    recency=('order_purchase_timestamp', lambda x: (filtered_df['order_purchase_timestamp'].max() - x.max()).days),
    frequency=('order_id', 'count'),
    monetary=('total_order_value', 'sum')
).reset_index()
top_customers = top_customers.sort_values(by=['monetary', 'frequency', 'recency'], ascending=[False, False, False])

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=top_customers['customer_unique_id'].head(5), x=top_customers['recency'].head(5), ax=ax, palette='Blues', orient='h')
ax.set_title("Top Customers - Recency")
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=top_customers['customer_unique_id'].head(5), x=top_customers['frequency'].head(5), ax=ax, palette='Oranges', orient='h')
ax.set_title("Top Customers - Frequency")
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=top_customers['customer_unique_id'].head(5), x=top_customers['monetary'].head(5), ax=ax, palette='Purples', orient='h')
ax.set_title("Top Customers - Monetary")
st.pyplot(fig)

# Order Status Distribution
st.subheader("📦 Order Status Distribution")
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(y='order_status', data=filtered_df, order=filtered_df['order_status'].value_counts().index, palette='Blues')
st.pyplot(fig)

st.markdown("---")
st.write("Dashboard by **Andhika**")
