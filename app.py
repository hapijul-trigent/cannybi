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
from src.request_handler import GPTRequestHandler
from src.sql_query_generator import SQLQueryGenerator
from src.sql_query_executor import SQLQueryExecutor
from src.business_intelligence_analyzer import BusinessIntelligenceAnalyzer
from src.sql_query_reasoning_generation import SQLQueryReasoningGenerator
from src.query_intent_classifier import QueryIntentClassifier
from src.misleading_query_handler import MisleadingQueryHandler
from src.prompts import (
    SYSTEM_PROMPT_INTENTCLASSIFIER,
    CONTEXT_SCHEMA,
    SYSTEM_PROMPT_SQL_REASONING,
    SYSTEM_PROMPT_SQG,
    SYSTEM_PROMPT_BI_ANALYSIS,
    LANGUAGE,
    SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION
)
from src.utils import display_refrence_table, display_and_pin_charts, display_pinned_charts
from src import styles
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

CHART_DIR = 'chart'
PINNED_CHART_DIR = 'pinned_chart'

# Load credentials from config
def load_credentials(config_file="config.json"):
    with open(config_file, "r") as file:
        data = json.load(file)
    return data

# Streamlit UI
st.set_page_config(page_title="CannyBI", layout="wide", page_icon="💬")
styles.apply_styles()


title, username, logout = st.columns([4, 3, 1])
with title:
    # st.title("💬 CannyBI")
    st.markdown('<h1 class="custom-title">💬 CannyBI v0.1</h1>', unsafe_allow_html=True)


# Authentication Logic
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Load credentials from config
    credentials = load_credentials()

    # Login Form
    _,  login_col, _ = st.columns([1, 1, 1])
    with login_col:
        st.image("static/CanPrev_4D-logo.jpg", width=400)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if username in credentials["users"] and authenticate(username, password, credentials["users"]):
                    st.session_state.authenticated = True
                    st.session_state.username = username  # Store username
                    st.rerun()
                else:
                    st.error("Invalid username or password")

# **Only show chatbot if authenticated**
if st.session_state.authenticated:

    with username:
        st.markdown(f'<div class="user-info">{st.session_state.username.title()}</div>', unsafe_allow_html=True)
    
    with logout:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button(f"Logout", use_container_width=True):
            st.session_state.update({"authenticated": False})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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
        # Clean up the charts folder
        for chart in os.listdir(CHART_DIR):
            os.remove(os.path.join(CHART_DIR, chart))

        # Display User Query
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Run Resolver Pipeline
        with st.spinner("Understanding Intent..."):
            intent_analysis = query_intent_classifier.classify(
                system_prompt=SYSTEM_PROMPT_INTENTCLASSIFIER,
                context=CONTEXT_SCHEMA,
                user_input=user_question
            )

        if intent_analysis['intent'].lower() == 'MISLEADING_QUERY'.lower():
            assistant_response = misleading_query_handler.suggest_better_questions(
                reasoning=intent_analysis['reasoning'],
                user_question=intent_analysis["rephrased_question"]
            )
        elif intent_analysis['intent'].lower() == 'GENERAL'.lower():
            pass
        else:
            chart_code = None
            query_results = {}
            try:
                with st.spinner("Reasoning Optimal Query Plan..."):
                    reasoning = sql_reasoning_generator.generate_reasoning(
                        system_prompt=SYSTEM_PROMPT_SQL_REASONING,
                        schema=CONTEXT_SCHEMA,
                        query=intent_analysis['rephrased_question'],
                        language=LANGUAGE
                    )

                with st.spinner("Writing Query..."):
                    sql_query = sql_generator.generate_queries(
                        system_prompt=SYSTEM_PROMPT_SQG,
                        schema=CONTEXT_SCHEMA,
                        query=intent_analysis['rephrased_question'],
                        reasoning_steps=reasoning,
                        current_time=time.time(),
                        language=LANGUAGE
                    )

                with st.spinner("Executing Queries..."):
                    query_results = sql_executor.execute_queries(sql_query["sql_query_steps"])
                    sql_executor.close_connection()
                    # st.success("SQL queries executed!")

                with st.spinner("Analyzing ..."):
                    bi_analysis_result = bi_analyzer.analyze_results(
                        SYSTEM_PROMPT_BI_ANALYSIS, 
                        sql_query_steps_result=query_results
                    )

                chart_code = bi_analysis_result["business_analysis"].get("chart-python-code", 'None')
            except Exception as e:
                st.toast("Please refresh and retry")

            try:
                if chart_code:
                    exec_globals = {}
                    exec(chart_code.replace("```python", '').replace('```', ''), {
                        "plt": plt, "sns": sns, "pd": pd, "st": st, 'np': np
                    }, exec_globals)

            except Exception as e:
                st.error(f"Error executing chart code: {e}")

        # Response Section
        with st.chat_message("assistant"):
            if intent_analysis['intent'].lower() == 'MISLEADING_QUERY'.lower():
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            elif intent_analysis['intent'].lower() == 'GENERAL'.lower():
                pass
            elif intent_analysis['intent'].lower() == 'TRIGGER'.lower():
                assistant_response = "**Created a Trigger for the above question**"
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                try:
                    st.markdown(bi_analysis_result['business_analysis']['summary'])
                    with st.expander("📊 Reference Queries"):
                        for rs in query_results['sql_query_steps']:
                            st.markdown(f"**🔍 Reason :: {rs['reason']}**")
                            st.code(rs['query'], language='sql')
                            display_refrence_table(rs['result'])

                    display_and_pin_charts(chart_dir=CHART_DIR, pinned_dir=PINNED_CHART_DIR)
                    st.session_state.messages.append({"role": "assistant", "content": bi_analysis_result['business_analysis']['summary']})
                except Exception as e:
                    st.toast("Please refresh and try again")
                    st.session_state.messages.append({"role": "assistant", "content": "Please refresh and try again"})
