from ollama import chat
from src import prompts
sql_query_results = """'result': [{'City': 'North Melissaport',
                                  'NumberOfSales': 213},
                                 {'City': 'North Gregoryland',
                                  'NumberOfSales': 200},
                                 {'City': 'New Shaunville',
                                  'NumberOfSales': 193}]"""
user_prompt = (
            f"### SQL QUERY RESULTS ###\n{sql_query_results}\n\n"
            "Analyze the results as a Business Intelligence (BI) expert.\n"
            "- Provide key business insights.\n"
            "- Summarize findings across all SQL queries.\n"
            "- Suggest strategic recommendations for business improvement.\n"
            "- Generate Python visualization code using seaborn & matplotlib, and save inside chart folder with name chart.png.\n"
            "Return output as structured JSON in the format:\n"
            "{\n"
            '    "business_analysis": {\n'
            '        "summary": "<Overall BI interpretation>",\n'
            '        "recommendations": ["<Recommendation 1>", "<Recommendation 2>", "<Recommendation 3>"],\n'
            '        "chart-python-code": "<Seaborn & Matplotlib Python Code>"\n'
            "    }\n"
            "}"
        )

stream = chat(
    model="deepscaler:latest",
    messages=[
        {"role": "system", "content": prompts.SYSTEM_PROMPT_BI_ANALYSIS},
        {"role": "user", "content": user_prompt}
        ],
    stream=True,
)
for chunk in stream:
    print(chunk["message"]["content"], end="", flush=True)