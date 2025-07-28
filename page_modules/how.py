import pandas as pd
import streamlit as st

# Hardcoded data
data = {
    "Component": [
        "Cloud",
        "Infrastructure as Code",
        "Data Pipeline",
        "Data Storage",
        "OLAP Processing",
        "Query Engine",
        "Chicago Car Crashes - Business Intelligence Dashboard",
    ],
    "Detail": [
        "Digital Ocean",
        "Pulumi (Daily setup/teardown)",
        "Airflow",
        "🧊Apache Iceberg on blob storage",
        "⚡Spark on k8s / Apache Thetha Sketches",
        "🦆Duckdb",
        "Configuration json files using 🐙StreamLana",
    ],
}

# Create DataFrame
df = pd.DataFrame(data)


# Function to highlight the last row
def highlight_last_row(row):
    if row.name == len(df) - 1:
        return ["background-color: yellow"] * len(row)
    else:
        return [""] * len(row)


# Apply style
styled_df = df.style.apply(highlight_last_row, axis=1)

# Title and styled table
st.title("📍 Tech Stack details")
st.write("How this demo was built?")
st.dataframe(styled_df)