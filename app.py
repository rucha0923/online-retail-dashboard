import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Online Retail Dashboard", layout="wide")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("retail_dashboard_data.csv")


df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# ------------------ HEADER ------------------
st.title("Online Retail Business Insights Dashboard")

# ------------------ KPI METRICS ------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${df['Revenue'].sum():,.0f}")
col2.metric("Unique Customers", df["CustomerID"].nunique())
col3.metric("Total Orders", df["InvoiceNo"].nunique())

st.markdown("""
This is a transactional data set which contains all the transactions occurring between 01/12/2010 and 09/12/2011 for a UK-based and registered non-store online retail.The company mainly sells unique all-occasion gifts. Many customers of the company are wholesalers.
""")

st.markdown("---")

# ------------------ MONTHLY REVENUE TREND ------------------
monthly = df.groupby(df["InvoiceDate"].dt.to_period("M"))["Revenue"].sum().reset_index()
monthly["InvoiceDate"] = monthly["InvoiceDate"].astype(str)

fig1 = px.line(monthly, x="InvoiceDate", y="Revenue",
               title="Monthly Revenue Trend")
st.plotly_chart(fig1, use_container_width=True)

# ------------------ PRODUCT PERFORMANCE ------------------
st.subheader("Product Performance")

top_products = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10).reset_index()

least_products = df.groupby("Description")["Quantity"].sum().sort_values().head(10).reset_index()
least_products.columns = ["Product", "Total Quantity"]

col1, col2 = st.columns(2)

with col1:
    fig2 = px.bar(top_products, x="Quantity", y="Description",
                  orientation="h", title="Top 10 Products")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(""" 
    This bar chart highlights the top 10 best-selling products. These products generate the most revenue and are key contributors to overall sales.
    """)

with col2:
    st.markdown("#### 10 Least Ordered Products")
    st.dataframe(least_products, use_container_width=True, height=350)
    st.markdown("""  
    This table shows the 10 least ordered products. These items have the lowest demand and could be considered for inventory optimization or discontinuation.
    """)

# ------------------ CUSTOMER ANALYSIS ------------------
st.subheader("Customer Behavior")

cust_rev = df.groupby("CustomerID")["Revenue"].sum().reset_index()
orders = df.groupby("CustomerID")["InvoiceNo"].nunique().reset_index(name="Orders")
cust = cust_rev.merge(orders, on="CustomerID")
cust["Type"] = cust["Orders"].apply(lambda x: "Repeat" if x > 1 else "One-Time")

fig3 = px.box(cust, x="Type", y="Revenue", log_y=True,
              title="Customer Spend: Repeat vs One-Time")

fig3.update_yaxes(tickvals=[10,100,1000,10000,100000,1000000])
st.plotly_chart(fig3, use_container_width=True)
st.markdown(""" 
This box plot compares revenue from one-time vs repeat customers. Repeat customers tend to contribute more to total revenue, showing the value of customer retention.
""")


# ------------------ CUSTOMER PERCENTAGE PIES ------------------
cust_count = cust["Type"].value_counts().reset_index()
cust_count.columns = ["Type","Count"]

cust_rev_type = cust.groupby("Type")["Revenue"].sum().reset_index()

col1, col2 = st.columns(2)

with col1:
    fig4 = px.pie(cust_count, values="Count", names="Type",
                  title="Customer Breakdown (%)")
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(""" 
    This pie chart shows the proportion of one-time vs repeat customers. Most revenue comes from repeat customers even if their number is smaller.
    """)

with col2:
    fig5 = px.pie(cust_rev_type, values="Revenue", names="Type",
                  title="Revenue Contribution by Customer Type (%)")
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("""  
    This pie chart shows revenue contribution by customer type. Repeat customers dominate revenue, reinforcing the importance of loyalty programs.
    """)

# ------------------ GLOBAL MAP ------------------
import numpy as np
import plotly.express as px
import streamlit as st

# --- Revenue by country ---
country_rev = (
    df.groupby("Country", as_index=False)
      .agg(Revenue=("Revenue", "sum"))
)

# Log-transform for color scaling
country_rev["log_revenue"] = np.log10(country_rev["Revenue"])

# Title above the chart
st.subheader("Global Revenue by Country")

fig_map = px.choropleth(
    country_rev,
    locations="Country",
    locationmode="country names",
    color="log_revenue",
    hover_name="Country",
    hover_data={
        "Revenue": ":$,.0f",
        "log_revenue": False
    },
    color_continuous_scale="viridis"
)

# Optional: colorbar shows real dollar values
fig_map.update_coloraxes(
    colorbar=dict(
        title="Revenue ($)",
        tickvals=[1, 2, 3, 4, 5, 6],
        ticktext=["$10", "$100", "$1K", "$10K", "$100K", "$1M"]
    )
)

st.plotly_chart(fig_map, use_container_width=True)
st.markdown("""
This map displays revenue by country (log-scaled). Countries with lighter colors generate higher revenue, highlighting key geographic markets for the business.
""")

# ------------------ INSIGHTS ------------------
st.markdown("---")
st.subheader("Key Insights & Recommendations")

st.markdown("""
• Revenue is highly seasonal, peaking toward the end of the year  
• Repeat customers contribute disproportionately to total revenue  
• A small number of products drive the majority of sales  
• Several low-demand products could be reconsidered for inventory optimization  
• Revenue is geographically concentrated in a small number of countries
""")
