from ollama import chat
from ollama import ChatResponse
from src.agents import prompts
sql_query_results = """[{"reason":"Calculate the average payment processing time for each payment method in the order_payments table for the last quarter (Q1 2025).","query":"SELECT payment_type_id, AVG(TIMESTAMPDIFF(SECOND, created_at, updated_at)) AS avg_processing_time_seconds FROM order_payments WHERE created_at >= '2025-01-01' AND created_at < '2025-04-01' GROUP BY payment_type_id ORDER BY avg_processing_time_seconds;","result":[{"payment_type_id":5,"avg_processing_time_seconds":"Decimal('7.6250')"},{"payment_type_id":3,"avg_processing_time_seconds":"Decimal('17036.7895')"},{"payment_type_id":2,"avg_processing_time_seconds":"Decimal('59615.5000')"},{"payment_type_id":1,"avg_processing_time_seconds":"Decimal('275194.8421')"}]}]"""
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

stream: ChatResponse = chat(
    model="gemma3",
    messages=[
        {"role": "system", "content": prompts.SYSTEM_PROMPT_BI_ANALYSIS},
        {"role": "user", "content": user_prompt}
        ],
    stream=True,
)
for chunk in stream:
    print(chunk.message.content, end="", flush=True)