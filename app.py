import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Luiss%402025@localhost:3306/airbnb")

def run_query(query):
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

st.set_page_config(page_title="Airbnb SQL Dashboard", layout="wide")
st.title("Airbnb SQL Dashboard – Berlin Listings")

# --- 1. Which neighborhoods generate the most revenue? ---
st.subheader("1. Top Revenue-Generating Neighborhoods")
query1 = """
SELECT 
    neighbourhood,
    SUM(price * number_of_reviews) AS total_revenue
FROM 
    listings
GROUP BY 
    neighbourhood
ORDER BY 
    total_revenue DESC;
"""
df1 = run_query(query1)
st.bar_chart(df1.set_index("neighbourhood"))

# --- 2. What are the cheapest listings with good review counts? ---
st.subheader("2. Cheapest Listings with >10 Reviews")
query2 = """
SELECT 
    name, 
    neighbourhood, 
    price
FROM 
    listings
WHERE 
    price < 50 AND number_of_reviews > 10
ORDER BY 
    price ASC;
"""
df2 = run_query(query2)
st.dataframe(df2)

# --- 3. What is the average price per room type? ---
st.subheader("3. Average Price by Room Type")
query3 = """
SELECT 
    room_type,
    MIN(price) AS min_price,
    AVG(price) AS avg_price,
    MAX(price) AS max_price
FROM 
    listings
GROUP BY 
    room_type;
"""
df3 = run_query(query3)
st.table(df3)

# --- 4. Which listings received the most reviews overall? ---
st.subheader("4. Listings with the Most Reviews")
query4 = """
SELECT 
    l.name, 
    COUNT(r.date) AS total_reviews
FROM 
    listings l
JOIN 
    reviews r ON l.id = r.listing_id
GROUP BY 
    l.id, l.name
ORDER BY 
    total_reviews DESC
LIMIT 10;
"""
df4 = run_query(query4)
st.dataframe(df4)

# --- 5. What is the cumulative number of reviews per listing by month? ---
st.subheader("5. Cumulative Reviews per Listing by Month")
query5 = """
SELECT 
    listing_id,
    date,
    DATE_FORMAT(date, '%%Y-%%m') AS month,
    COUNT(*) OVER (
        PARTITION BY listing_id 
        ORDER BY date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_reviews
FROM 
    reviews;
"""
df5 = run_query(query5)
listing_ids = df5["listing_id"].drop_duplicates().sample(10).tolist()
selected_listing = st.selectbox("Choose a Listing ID", listing_ids)
filtered_df5 = df5[df5["listing_id"] == selected_listing]
st.line_chart(filtered_df5.set_index("date")["cumulative_reviews"])

# --- 6. Classify listings into value categories using CASE ---
st.subheader("6. Listing Categories by Price and Popularity")
query6 = """
SELECT 
    name, 
    neighbourhood, 
    price, 
    number_of_reviews,
    CASE
        WHEN price < 50 AND number_of_reviews > 100 THEN 'Top Budget Pick'
        WHEN price BETWEEN 50 AND 100 AND number_of_reviews > 50 THEN 'Best Mid-Range'
        ELSE 'Niche or Premium'
    END AS category
FROM 
    listings;
"""
df6 = run_query(query6)
st.dataframe(df6)

# --- 7. Which neighborhoods had the most reviews in 2025? ---
st.subheader("7. Most Reviewed Neighborhoods in 2025")
query7 = """
WITH last_year_reviews AS (
    SELECT 
        listing_id, 
        date
    FROM 
        reviews
    WHERE 
        date >= '2025-01-01'
)
SELECT 
    l.neighbourhood, 
    COUNT(*) AS review_count
FROM 
    last_year_reviews r
JOIN 
    listings l ON r.listing_id = l.id
GROUP BY 
    l.neighbourhood
ORDER BY 
    review_count DESC
LIMIT 10;
"""
df7 = run_query(query7)
st.bar_chart(df7.set_index("neighbourhood"))
