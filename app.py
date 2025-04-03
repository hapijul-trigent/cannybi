import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.request_handler import GPTRequestHandler
from src.sql_query_generator import SQLQueryGenerator
from src.sql_query_executor import SQLQueryExecutor
from src.business_intelligence_analyzer import BusinessIntelligenceAnalyzer
from src.sql_query_reasoning_generation import SQLQueryReasoningGenerator
from src.query_intent_classifier import QueryIntentClassifier
from src.misleading_query_handler import MisleadingQueryHandler
from dotenv import load_dotenv
import numpy as np

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
import time
from pprint import pprint, pformat
load_dotenv()


# Initialize Components
GPT4V_KEY=''
ENDPOINT = ""
request_handler = GPTRequestHandler(api_key=GPT4V_KEY, endpoint=ENDPOINT)
query_intent_classifier = QueryIntentClassifier(request_handler=request_handler)
sql_reasoning_generator = SQLQueryReasoningGenerator(request_handler=request_handler)
sql_generator = SQLQueryGenerator(request_handler=request_handler)
sql_executor = SQLQueryExecutor()
bi_analyzer = BusinessIntelligenceAnalyzer(request_handler=request_handler)
misleading_query_handler = MisleadingQueryHandler(request_handler=request_handler, system_prompt=SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION)
CHART_DIR = 'chart'
PINNED_CHART_DIR = 'pinned_chart'



# Streamlit UI
st.set_page_config(page_title="CannyBI", layout="wide")
st.title("💬 CannyBI")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Two columns
# chat_section, pinned_chart_section = st.columns([2.7, 1.3])

# with pinned_chart_section:
#     display_pinned_charts(directory=PINNED_CHART_DIR)

# # with chat_section:
# User Input
user_question = st.chat_input("Ask a business intelligence question (e.g., 'Which cities have the most sales?')...")
if user_question:
    # CLean up the charts folder
    for chart in os.listdir('chart'):
        os.remove(os.path.join('chart', chart))
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
        # st.success("Intent classification completed!")
        # st.code(pformat(intent_analysis), language='json')


    if intent_analysis['intent'].lower() == 'MISLEADING_QUERY'.lower():
        assitant_response = misleading_query_handler.suggest_better_questions(
            reasoning=intent_analysis['reasoning'],
            user_question=intent_analysis["rephrased_question"]
        )
    elif intent_analysis['intent'].lower() == 'GENERAL'.lower():
        pass
    else:
        chart_code = None
        query_results =  {}
        try:
            with st.spinner("Reasoning Optimal Query Plan..."):
                reasoning = sql_reasoning_generator.generate_reasoning(
                    system_prompt=SYSTEM_PROMPT_SQL_REASONING,
                    schema=CONTEXT_SCHEMA,
                    query=intent_analysis['rephrased_question'],
                    language=LANGUAGE
                )
                # st.success("SQL reasoning generated!")
                # st.code(pformat(reasoning), language='json')

            with st.spinner("Writing Query..."):
                sql_query = sql_generator.generate_queries(
                    system_prompt=SYSTEM_PROMPT_SQG,
                    schema=CONTEXT_SCHEMA,
                    query=intent_analysis['rephrased_question'],
                    reasoning_steps=reasoning,
                    current_time=time.time(),
                    language=LANGUAGE
                )
                # st.success("SQL queries generated!")
                # st.code(pformat(sql_query), language='json')

            with st.spinner("Executing Queries..."):
                query_results = sql_executor.execute_queries(sql_query["sql_query_steps"])
                sql_executor.close_connection()
                st.success("SQL queries executed!")
                # st.code(pformat(query_results), language='json')

            with st.spinner("Analyzing ..."):
                bi_analysis_result = bi_analyzer.analyze_results(
                    SYSTEM_PROMPT_BI_ANALYSIS, 
                    sql_query_steps_result=query_results
                )
                # st.success("BI analysis completed!")
                # st.code(pformat(bi_analysis_result), language='json')

            chart_code = bi_analysis_result["business_analysis"].get("chart-python-code", 'None')
        except Exception as e:
            st.toast(f"Please refresh and retry")
        try:
            # Define a local execution environment for running the AI-generated code
            if chart_code:
                exec_globals = {}
                exec(chart_code.replace("```python", '').replace('```', ''), {"plt": plt, "sns": sns, "pd": pd, "st": st, 'np': np}, exec_globals)

        except Exception as e:
            st.error(f"Error executing chart code: {e}")

    # ----------------------------
    # Response Section
    # ----------------------------

    # Display Assistant Response
    with st.chat_message("assistant"):
        if intent_analysis['intent'].lower() == 'MISLEADING_QUERY'.lower():
            st.markdown(assitant_response)
            st.session_state.messages.append({"role": "assistant", "content": assitant_response})
        elif intent_analysis['intent'].lower() == 'GENERAL'.lower():
            pass
        elif intent_analysis['intent'].lower() == 'TRIGGER'.lower():
            assitant_response = "**Created a Trigger for the above question**"
            st.markdown(assitant_response)
            st.session_state.messages.append({"role": "assistant", "content": assitant_response})
        else:
            try:
                st.markdown(bi_analysis_result['business_analysis']['summary'])
                with st.expander("📊 Reference Queries"):
                    # st.code(query_results)
                    for rs in query_results['sql_query_steps']:
                        st.markdown(f"**🔍 Reason :: {rs['reason']}**")
                        st.code(rs['query'], language='sql')
                        display_refrence_table(rs['result'])

                display_and_pin_charts(chart_dir=CHART_DIR, pinned_dir=PINNED_CHART_DIR)

                # Append response to chat history
                st.session_state.messages.append({"role": "assistant", "content": bi_analysis_result['business_analysis']['summary']})
            except Exception as e:
                st.toast(f"Please refresh and try again")
                st.session_state.messages.append({"role": "assistant", "content": "Please refresh and try again"})
            






