import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Dummy Components for Demo
class DummySQLQueryGenerator:
    """Simulates SQL query generation for the demo."""
    def generate_query(self, system_prompt, schema, query, current_time, language):
        return {
            "stepwise_sql": [
                {"reason": "Get sales orders per city.", "query": "SELECT City, COUNT(SaleID) FROM Sales GROUP BY City"},
                {"reason": "Find top 3 cities with highest sales.", "query": "SELECT City, COUNT(SaleID) FROM Sales GROUP BY City ORDER BY COUNT(SaleID) DESC LIMIT 3"}
            ]
        }

class DummySQLQueryExecutor:
    """Simulates SQL query execution for the demo."""
    def execute_queries(self, sql_query_steps):
        return {
            "sql_query_steps": [
                {
                    "reason": "Get sales orders per city.",
                    "query": "SELECT City, COUNT(SaleID) FROM Sales GROUP BY City",
                    "result": [
                        ["New York", 10], ["Los Angeles", 8], ["Chicago", 6],
                        ["Houston", 5], ["San Francisco", 4], ["Seattle", 3]
                    ]
                },
                {
                    "reason": "Find top 3 cities with highest sales.",
                    "query": "SELECT City, COUNT(SaleID) FROM Sales GROUP BY City ORDER BY COUNT(SaleID) DESC LIMIT 3",
                    "result": [["New York", 10], ["Los Angeles", 8], ["Chicago", 6]]
                }
            ]
        }

class DummyBIAnalyzer:
    """Simulates Business Intelligence Analysis for the demo."""
    def analyze_results(self, system_prompt, sql_query_steps_result):
        return {
            "sql_query_steps": sql_query_steps_result["sql_query_steps"],
            "business_analysis": {
                "summary": "New York, Los Angeles, and Chicago are the top-performing cities in sales. Houston and San Francisco have potential for growth.",
                "recommendations": [
                    "Increase inventory in New York, Los Angeles, and Chicago.",
                    "Run marketing campaigns in Houston and San Francisco to boost sales.",
                    "Optimize logistics to support high-demand areas efficiently."
                ],
                "chart-python-code": """
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Dummy Data
data = {"City": ["New York", "Los Angeles", "Chicago"], "Sales Orders": [10, 8, 6]}
df = pd.DataFrame(data)

# Plot
plt.figure(figsize=(8, 5))
sns.barplot(x="Sales Orders", y="City", data=df, palette="Blues_r")

# Labels
plt.xlabel("Number of Sales Orders")
plt.ylabel("City")
plt.title("Top 3 Cities by Sales Orders")

# Display the chart
plt.show()
"""
            }
        }

# Initialize Dummy Components
sql_generator = DummySQLQueryGenerator()
sql_executor = DummySQLQueryExecutor()
bi_analyzer = DummyBIAnalyzer()

# Streamlit UI
st.set_page_config(page_title="CannyBI", layout="wide")
st.title("💬 CannyBI - Stay Informed, Stay Ahead")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_question = st.chat_input("Ask a business intelligence question (e.g., 'Which cities have the most sales?')...")
if user_question:
    # Display User Query
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Generate SQL Queries (Dummy)
    sql_queries = sql_generator.generate_query("", "", user_question, "", "")

    # Execute SQL Queries (Dummy)
    sql_results = sql_executor.execute_queries(sql_queries["stepwise_sql"])

    # Analyze Results (Dummy)
    bi_analysis = bi_analyzer.analyze_results("", sql_results)

    # Format Response
    assistant_response = f"""
    **📊 Business Insights:**  
    {bi_analysis['business_analysis']['summary']}

    **💡 Recommendations:**  
    - {bi_analysis['business_analysis']['recommendations'][0]}
    - {bi_analysis['business_analysis']['recommendations'][1]}
    - {bi_analysis['business_analysis']['recommendations'][2]}
    """

    # Display Assistant Response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Append response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    # Display Chart Code
    chart_code = bi_analysis["business_analysis"]["chart-python-code"]
    with st.expander("📈 View Data Visualization Code"):
        st.code(chart_code, language="python")

    # Generate and Display Chart in Streamlit
    st.subheader("📊 Sales Performance Chart")
    sales_data = {
        "City": ["New York", "Los Angeles", "Chicago"],
        "Sales Orders": [10, 8, 6]
    }
    df = pd.DataFrame(sales_data)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x="Sales Orders", y="City", data=df, palette="Blues_r", ax=ax)
    st.pyplot(fig)
