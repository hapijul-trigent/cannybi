import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
from dotenv import load_dotenv
from src.auth.hashing import authenticate  # Import authentication function
from src.agents.request_handler import GPTRequestHandler
from src.agents.sql_query_generator import SQLQueryGenerator
from src.agents.sql_query_executor import SQLQueryExecutor
from src.agents.business_intelligence_analyzer import BusinessIntelligenceAnalyzer
from src.agents.sql_query_reasoning_generation import SQLQueryReasoningGenerator
from src.agents.query_intent_classifier import QueryIntentClassifier
from src.agents.misleading_query_handler import MisleadingQueryHandler
from src.agents.sql_auto_fixer import SQLQueryAutoFixer
from src.agents.prompts import (
    SYSTEM_PROMPT_INTENTCLASSIFIER,
    CONTEXT_SCHEMA,
    SYSTEM_PROMPT_SQL_REASONING,
    SYSTEM_PROMPT_SQG,
    SYSTEM_PROMPT_BI_ANALYSIS,
    LANGUAGE,
    SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION
)
from src.agents.utils import display_refrence_table, display_and_pin_charts, display_pinned_charts
from src.agents import styles

load_dotenv()

# Initialize Components
GPT4V_KEY = os.getenv("GPT4V_KEY")
ENDPOINT = os.getenv("GPT_ENDPOINT")
request_handler = GPTRequestHandler(api_key=GPT4V_KEY, endpoint=ENDPOINT)
query_intent_classifier = QueryIntentClassifier(request_handler=request_handler)
sql_reasoning_generator = SQLQueryReasoningGenerator(request_handler=request_handler)
sql_generator = SQLQueryGenerator(request_handler=request_handler)
sql_executor = SQLQueryExecutor()
bi_analyzer = BusinessIntelligenceAnalyzer(request_handler=request_handler)
misleading_query_handler = MisleadingQueryHandler(request_handler=request_handler, system_prompt=SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION)
sql_query_fixer = SQLQueryAutoFixer(request_handler=request_handler, database_schema=CONTEXT_SCHEMA)

CHART_DIR = 'charts'
PINNED_CHART_DIR = 'pinned_charts'

# Load credentials from config
def load_credentials(config_file="config.json"):
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading credentials: {e}")
        return {"users": {}}

# Streamlit UI
st.set_page_config(page_title="CannyBI", layout="wide", page_icon="💬")
styles.apply_styles()

title, username, logout = st.columns([4, 3, 1])

# Authentication Logic
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    credentials = load_credentials()

    _, login_col, _ = st.columns([1, 1, 1])
    with login_col:
        st.image("static/CanPrev_4D-logo.jpg", width=400)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if username in credentials["users"] and authenticate(username, password, credentials["users"]):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.toast("Invalid username or password")

# **Only show chatbot if authenticated**
if st.session_state.authenticated:
    with title:
        st.markdown('<h1 class="custom-title">💬 CannyBI v0.1</h1>', unsafe_allow_html=True)
    with username:
        st.markdown(f'<div class="user-info">👤: {st.session_state.username.title()}</div>', unsafe_allow_html=True)
    with logout:
        if st.button("Logout", use_container_width=True):
            st.session_state.update({"authenticated": False})
            st.rerun()

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    user_question = st.chat_input("Ask a business intelligence question...")

    if user_question:
        for chart in os.listdir(CHART_DIR):
            os.remove(os.path.join(CHART_DIR, chart))

        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        try:
            query_results = {}
            bi_analysis_result = {"business_analysis": {"summary": "Analysis not available. Try again", "chart-python-code": None}}

            with st.spinner("Understanding Intent..."):
                intent_analysis = query_intent_classifier.classify(
                    system_prompt=SYSTEM_PROMPT_INTENTCLASSIFIER,
                    context=CONTEXT_SCHEMA,
                    user_input=user_question
                )

            if intent_analysis['intent'].lower() == 'misleading_query':
                assistant_response = misleading_query_handler.suggest_better_questions(
                    reasoning=intent_analysis['reasoning'],
                    user_question=intent_analysis["rephrased_question"]
                )
            elif intent_analysis['intent'].lower() == 'general':
                assistant_response = (
                    "I can only answer database-related queries.\n\n"
                    "**Example Questions:**\n"
                    "- *'What were the total sales in the last quarter?'*\n"
                    "- *'How many customers placed an order last month?'*"
                )
            else:
                
                try:
                    with st.spinner("Reasoning Optimal Query Plan..."):
                        reasoning = sql_reasoning_generator.generate_reasoning(
                            SYSTEM_PROMPT_SQL_REASONING, CONTEXT_SCHEMA, intent_analysis['rephrased_question'], LANGUAGE
                        )

                    with st.spinner("Writing Query..."):
                        sql_query = sql_generator.generate_queries(
                            SYSTEM_PROMPT_SQG, CONTEXT_SCHEMA, intent_analysis['rephrased_question'], reasoning, time.time(), LANGUAGE
                        )

                    with st.spinner("Executing Queries..."):
                        query_results = sql_executor.execute_queries(sql_query["sql_query_steps"])
                        # st.write(query_results)
                        sql_executor.close_connection()
                except Exception as e:
                    st.toast("Auto-fixing query...")
                    with st.spinner("Fixing Queries..."):
                        fixed_queries = sql_query_fixer.fix_sql_errors(intent_analysis['rephrased_question'], query_results)
                        query_results = sql_executor.execute_queries(fixed_queries)
                        # st.write(query_results)

                try:
                    with st.spinner("Analyzing ..."):
                        bi_analysis_result = bi_analyzer.analyze_results(SYSTEM_PROMPT_BI_ANALYSIS, query_results, user_question=intent_analysis['rephrased_question'])
                except Exception as e:
                    st.toast(f"Analysis failed: {e}")

                chart_code = bi_analysis_result["business_analysis"].get("chart-python-code", None)
                
                if chart_code:
                    try:
                        exec_globals = {}
                        exec(chart_code.replace("```python", "").replace("```", ""), {"plt": plt, "sns": sns, "pd": pd, "st": st, "np": np, "os": os}, exec_globals)
                    except Exception as e:
                        pass

        except Exception as e:
            st.toast(f"Unexpected error: {e}")

        # Display Response
        with st.chat_message("assistant"):
            st.markdown(bi_analysis_result['business_analysis']['summary'])
            with st.expander("📊 Reference Queries"):
                for rs in query_results.get('sql_query_steps', None):
                    if rs['result'] is not None:
                        st.markdown(f"**🔍 Reason :: {rs['reason']}**")
                        st.code(rs['query'], language='sql')
                        display_refrence_table(rs['result'])

            display_and_pin_charts(chart_dir=CHART_DIR, pinned_dir=PINNED_CHART_DIR)
            st.session_state.messages.append({"role": "assistant", "content": bi_analysis_result['business_analysis']['summary']})
