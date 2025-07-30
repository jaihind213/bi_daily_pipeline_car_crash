import streamlit as st

st.title("📍 Tech Stack details")
st.write("How this demo was built?")

# Table rows with HTML formatting
rows = [
    ["Cloud", "Digital Ocean"],
    ["Infrastructure as Code", "Pulumi (Daily setup/teardown)"],
    ["Data Pipeline", "Airflow"],
    ["Data Storage", "🧊Apache Iceberg on blob storage"],
    [
        "OLAP Processing",
        "⚡Spark on k8s / Apache Thetha Sketches (<a href='https://github.com/jaihind213/daily_pipeline_car_crash' target='_blank'>GitHub</a>)",  # noqa: E501
    ],
    ["Query Engine", "🦆Duckdb"],
    [
        "Chicago Car Crashes - Business Intelligence Dashboard",
        "Configuration json files using 🐙StreamLana (<a href='https://github.com/jaihind213/bi_daily_pipeline_car_crash' target='_blank'>GitHub</a>)",  # noqa: E501
    ],
]

# Build HTML table
table_html = """
<table>
    <thead>
        <tr>
            <th>Component</th>
            <th>Detail</th>
        </tr>
    </thead>
    <tbody>
"""

for _, (comp, detail) in enumerate(rows):
    highlight = ""
    table_html += f"<tr{highlight}><td>{comp}</td><td>{detail}</td></tr>"

table_html += """
    </tbody>
</table>
"""

with st.container():
    # Render table with hyperlinks
    st.markdown(table_html, unsafe_allow_html=True)

    st.image("arch.jpg", use_container_width=False, width=800)
