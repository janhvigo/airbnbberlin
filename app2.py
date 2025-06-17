import streamlit as st
import pandas as pd

df = pd.read_csv("listings.csv")

# Title and Introduction
st.title("Berlin Airbnb Market Advisor")
st.write("""
Welcome! This tool is built for:
- New investors evaluating property potential
- Airbnb hosts setting competitive nightly rates
- Market analysts looking for key trends

Select your preferences below to get tailored insights.
""")

st.sidebar.header("Your Listing")
neighborhood = st.sidebar.selectbox("Select a Neighborhood", sorted(df['neighbourhood'].dropna().unique()))
room_type = st.sidebar.selectbox("Room Type", df['room_type'].dropna().unique())

bedrooms = st.sidebar.slider("Estimated Bedrooms", 1, 10, 1)

filtered = df[(df['neighbourhood'] == neighborhood) & (df['room_type'] == room_type)]

# Price insights
if not filtered.empty:
    avg_price = filtered['price'].mean()
    min_price = filtered['price'].min()
    max_price = filtered['price'].max()

    st.subheader("💰 Suggested Nightly Price")
    price_suggestion = avg_price + (bedrooms - 1) * 10
    st.metric("Recommended Price (€)", f"{price_suggestion:.2f}")

    st.write(f"(Based on {len(filtered)} similar listings in {neighborhood})")

    st.subheader("Market Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Price", f"€{avg_price:.2f}")
    col2.metric("Min Price", f"€{min_price:.2f}")
    col3.metric("Max Price", f"€{max_price:.2f}")

    st.write("### Sample Listings")
    st.dataframe(filtered[['name', 'price', 'minimum_nights', 'number_of_reviews', 'availability_365']].head(10))

    st.write("### Reviews vs Availability")
    st.bar_chart(filtered[['availability_365', 'number_of_reviews']].head(20))
    
    st.write("### Top Hosts per Neighbourhood by Estimated Revenue")

    revenue_df = df.dropna(subset=['price', 'reviews_per_month'])

    revenue_df['estimated_annual_revenue'] = revenue_df['price'] * revenue_df['reviews_per_month'] * 12

    # Group by host and neighbourhood, sum revenues
    top_hosts = (
        revenue_df.groupby(['neighbourhood', 'host_id'])
        .agg(host_name=('host_name', 'first'),
             total_listings=('id', 'count'),
             total_revenue=('estimated_annual_revenue', 'sum'))
        .reset_index()
    )

    top_hosts_per_nbh = top_hosts.sort_values(['neighbourhood', 'total_revenue'], ascending=[True, False])
    top_hosts_per_nbh = top_hosts_per_nbh.groupby('neighbourhood').head(1)


    st.dataframe(top_hosts_per_nbh[['neighbourhood', 'host_name', 'host_id', 'total_listings', 'total_revenue']].sort_values(by='total_revenue', ascending=False).reset_index(drop=True))

else:
    st.warning("No listings match your selected criteria. Try another combination.")


st.sidebar.header("Market Trends")
if st.sidebar.checkbox("Show city-wide analytics"):
    st.subheader("City-wide Market Trends")

    city_group = df.groupby('neighbourhood')[['price', 'availability_365', 'number_of_reviews']].mean().sort_values(by='price', ascending=False)
    st.write("#### Average Price by Neighborhood")
    st.bar_chart(city_group['price'])

    st.write("#### Listings Count by Neighborhood")
    st.bar_chart(df['neighbourhood'].value_counts())

    st.write("#### Grouped Reviews (Last 12 Months)")
    review_group = st.selectbox("Group reviews by:", ['room_type', 'neighbourhood', 'neighbourhood_group'])
    review_means = df.groupby(review_group)['number_of_reviews_ltm'].mean()
    st.bar_chart(review_means)

st.sidebar.download_button(
    label="Download Dataset (Credits - Airbnb Insider)",
    data=df.to_csv(index=False),
    file_name='berlin_airbnb_listings.csv',
    mime='text/csv')
