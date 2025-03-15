from textwrap import dedent



SYSTEM_PROMPT_INTENTCLASSIFIER = """### TASK ###
Classify user intent into MISLEADING_QUERY, TEXT_TO_SQL, TRIGGER, or GENERAL after rephrasing the question for clarity and relevance to the database schema.

### INSTRUCTIONS ###
1. Rephrase the question:
   - Adjust adjectives for specificity and schema relevance.
   - Include time formats (YYYY-MM-DD) if needed.
   - Consider previous SQL queries if provided.
2. Classify intent:
   - TEXT_TO_SQL: Requires SQL query, references schema elements.
   - MISLEADING_QUERY: Irrelevant, vague, or contains SQL code.
   - GENERAL: Asks about the schema or guidance.
   
3. Reasoning must be ≤20 words.

### OUTPUT FORMAT ###
```json
{
    "rephrased_question": "<REPHRASED_USER_QUESTION_IN_STRING_FORMAT>",
    "reasoning": "<CHAIN_OF_THOUGHT_REASONING_BASED_ON_REPHRASED_USER_QUESTION_IN_STRING_FORMAT>",
    "intent": "MISLEADING_QUERY" | "TEXT_TO_SQL" | "GENERAL"
}```
"""

CONTEXT_SCHEMA = """
SALES DATABASE SCHEMA
### Table: sales_report
#### Purpose:
Tracks sales transactions with order, product, account, pricing, tax, and shipment details.

#### Columns:
- **id** (Primary Key)
- **order_id** (Foreign Key to orders)
- **order_item_id**
- **account_id** (Foreign Key to accounts)
- **currency_id**, **currency_abbreviation**, **currency_rate**
- **country_id**
- **account_name**, **account_type**, **account_type_id**
- **invoice**, **invoice_dt**
- **product_sku**, **product_name**, **product_description**, **product_brand**, **product_brand_id**
- **product_lot**, **product_expiry**
- **promotion_id** (Foreign Key to promotions), **promotion_name**
- **cogs**, **price**, **quantity**, **scanned_quantity**
- **discount_type**, **unit_discount**
- **line_amount**, **line_tax**
- **payterm**, **payterm_id**
- **billing_id**, **shipping_id**
- **billing_address**, **billing_city**, **billing_province**, **billing_province_id**
- **billing_lat**, **billing_log**
- **shipping_address**, **shipping_city**, **shipping_province**, **shipping_province_id**
- **shipping_lat**, **shipping_log**
- **source**, **source_id**
- **order_date**, **ship_date**
- **order_type_id**, **order_type**
- **credit_type_id**, **credit_type**
- **print_queue_date**, **completed_date**
- **purity_Id**, **new_fullscript_id**, **fullscript_id**, **fullscript_account_id**
- **iv_id**, **iv_sale_type**
- **picked_lot_codes**, **picked_date_of_expiry**
- **sample** (0-No, 1-Yes)

### Table: orders
#### Purpose:
Stores order details including payment, discounts, status, and fulfillment.

#### Columns:
- **id** (Primary Key)
- **kn_warehouse_id**
- **currency_id**, **currency_rate**
- **pod_printed**
- **account_id** (Foreign Key to accounts)
- **qb_entity_id**, **godirect_id**
- **pay_term_id** (Foreign Key to pay_terms)
- **invoice_number**
- **order_type_id** (Foreign Key to order_types)
- **order_source_id** (Foreign Key to order_sources)
- **source_value**
- **account_contact_id**
- **po_number**
- **billing_id**, **shipping_id**
- **subtotal_amount**, **coupon_discount**, **shipping_amount**
- **shipping_fee_option**, **tax_percent**, **tax_amount**, **tax_exempt**
- **total_amount**, **paid_amount**, **refund_amount**
- **total_items**, **total_lines**
- **order_status_id** (Foreign Key to order_statuses)
- **dn_sync_status**, **qb_sync_status**
- **invoice_date**, **warehouse_note**, **invoice_note**, **shipment_note**
- **claimed_by**
- **order_held**, **held_reason**, **reject_reason**
- **put_away**, **packed_percentage**, **packed_updated_at**
- **completed_date**
- **skid**, **order_split_claimed**, **order_split**, **claim_source**
- **created_by**, **updated_by**
- **created_at**, **updated_at**

### Table: accounts
#### Purpose:
Stores customer account details including contact, billing, and payment preferences.

#### Columns:
- **id** (Primary Key)
- **name**, **company_flag**
- **main_contact_name**, **country_code**
- **phone**, **extension**, **fax**, **email**, **accounting_email**
- **website**, **account_type_id** (Foreign Key to account_types)
- **tax_exempt**, **pricing_model_id**
- **school_name**, **school_id**, **graduation_year**, **graduation_month**
- **pay_term_id** (Foreign Key to pay_terms)
- **red_flag**, **stop_shipment**, **call_collect**
- **facebook_url**, **twitter_url**, **instagram_url**, **linkedin_url**
- **site_id**, **account_status_id**, **account_approval_status_id**
- **approved_date**, **created_by**, **updated_by**
- **created_at**, **updated_at**
- **last_order_date**
- **account_id**, **currency_id**, **country_id**
- **account_license**, **score**, **school_email**

### Table: products
#### Purpose:
Stores product inventory, pricing, branding, and stock.

#### Columns:
- **id** (Primary Key)
- **kn_part_id**, **kn_part_type_id**
- **name**, **pricelist_name**
- **upc**, **sku**, **erp_key**, **casecode**
- **uom**, **cogs**, **msrp**
- **line**, **brand_id** (Foreign Key to brands)
- **product_website_url**, **product_doc_url**
- **photo**, **unit_weight**, **case_length**, **case_width**, **case_height**, **case_weight**
- **case_volume**, **case_density**
- **eta_stock_from_date**, **eta_stock_to_date**
- **out_of_stock**, **safe_stock**, **instruction**
- **out_of_stock_date**, **dn_available_qty**
- **inventory_qty**, **reserved_qty**, **outbound_reserved_qty**
- **inter_wh_reserved_qty**, **kit_reserved_qty**, **account_reserved_qty**
- **hold_qty**, **expired_qty**, **ordered_qty**
- **assigned_ordered_qty**, **available_qty**, **inventory_linked**
- **size**, **serving_size**, **flavour**, **flavor**
- **codex_status**, **best_seller**, **status**, **npn**
- **include_in_portal**, **lang**, **storage_conditions**, **webinar_product**
- **canprev_used_in_flag**, **pricelist_used_in_flag**
- **created_by**, **updated_by**, **created_at**, **updated_at**
- **portal_used_in_flag**, **canprev_codex_id**, **codex_config_module_id**
### Table: promotions
#### Purpose:
Defines active promotions with discounts and eligibility.

#### Columns:
- **id** (Primary Key)
- **name**, **description**
- **from_date**, **to_date**
- **promotion_for** (0-All accounts, 1-Associations/Accounts)
- **promotion_to** (0-All products, 1-Brands/Products)
- **promotion_rule_id** (Foreign Key to promotion_rules)
- **value1**, **value2**
- **promotion_status_id** (Foreign Key to promotion_statuses)
- **approved_by**
- **priority** (0-Default, 1-High, 2-None)
- **portal** (0-No, 1-Yes)
- **rejection_reason**, **percentage_value**
- **country_id**
- **created_by**, **updated_by**
- **created_at**, **updated_at**

### Table: order_payments
#### Purpose:
Tracks order payment transactions.

#### Columns:
- **id** (Primary Key)
- **payment_type_id** (Foreign Key to payment_types)
- **transaction_type** (0-Purchase, 1-Preauth)
- **moneris_order_id** (Moneris transaction reference)
- **order_id** (Foreign Key to orders)
- **key_id**
- **transaction_number**
- **amount_paid**, **others**
- **status** (0-Failed, 1-Success, 2-Void)
- **qb_entity_id**
- **qb_sync_status** (0-No, 1-Yes)
- **qb_txn_date**
- **parent_id**
- **created_by**, **updated_by**
- **created_at**, **updated_at**

payment_types:
### Table: payment_types
#### Purpose:
Stores different types of payment methods used in transactions.

#### Columns:
- **id** (Primary Key) - Unique identifier for the payment type.
- **title** - Name of the payment type.
- **qb_entity_id** - Reference ID for QuickBooks integration.
- **created_by** - ID of the user who created the record.
- **updated_by** - ID of the user who last updated the record.
- **created_at** - Timestamp when the record was created.
- **updated_at** - Timestamp when the record was last updated.


### Table: order_shipments
#### Purpose:
Manages order shipments including carriers, tracking, and costs.

#### Columns:
- **id** (Primary Key)
- **order_id** (Foreign Key to orders)
- **scheduled_date**
- **weight**, **uom** (0-Kg, 1-Lbs)
- **cost**
- **package_count**
- **courier_id** (Foreign Key to couriers)
- **tracking_number**
- **courier_response_id**
- **pickup_id**
- **status** (0-Deleted, 1-Active)
- **warehouse_id** (Foreign Key to warehouses)
- **bol_file_name**
- **created_by**, **updated_by**
- **created_at**, **updated_at**
- **manifest_id**
"""

SYSTEM_PROMPT_SQL_REASONING = """### TASK ###
You are a skilled data analyst who deeply reasons about the user's question and the database schema to provide a step-by-step reasoning plan.

### INSTRUCTIONS ###
1. Analyze the user’s question and database schema thoroughly.
2. Provide a structured, numbered reasoning plan.
3. Use the same language as the user’s input.
4. Consider the provided current time if the question involves date/time.
5. Do NOT include SQL in the reasoning plan.

**Important Note**:
Last quarter refers to the previous three-month period based on the calendar year: Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec). Example: If today is in Q2 (Apr-Jun), the last quarter was Q1 (Jan-Mar).

### OUTPUT FORMAT ###
```json
{
    "reasoning_plan": "<STEP-BY-STEP_REASONING_PLAN>"
}```
"""

SYSTEM_PROMPT_SQL_REASONING = """### TASK ###
You are a skilled data analyst who deeply reasons about the user's question and the database schema to provide a structured reasoning plan.

### INSTRUCTIONS ###
1. Analyze the user’s question and database schema carefully.
2. Provide a clear, numbered reasoning plan.
3. Use the same language as the user’s input.
4. Consider the current date if the question involves time.
5. Do NOT include SQL in the reasoning plan.

**Note**:
"Last quarter" refers to the previous three-month period based on the calendar year:  
Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec).  
Example: If today is in Q2, the last quarter was Q1.

### OUTPUT FORMAT ###
```json
{
    "reasoning_plan": "<STEP-BY-STEP_REASONING_PLAN>"
}
"""

LANGUAGE =  'english'

SYSTEM_PROMPT_SQG = """### TASK ###
Generate MySQL-compatible SQL queries based on the user’s question, database schema, and reasoning steps.

### INSTRUCTIONS ###
1. **Analyze the database schema and reasoning steps carefully.**
2. **Generate a valid SQL query** for each reasoning step if required; otherwise, return `null`.
3. **Ensure queries follow MySQL syntax** and retrieve accurate data.
4. **Optimize queries for performance** by:
   - Using indexed columns in `JOIN` and `WHERE` clauses.
   - Avoiding unnecessary subqueries.
   - Ensuring proper filtering and ordering.
   - If possible combine multiple reasons into single queries
   - **Limit result rows to prevent excessive token usage** (`LIMIT 10` by default, unless otherwise specified by the user).


### IMPORTANT SQL RULES ###
✅ **DO NOT use `LIMIT` inside `IN/ALL/ANY/SOME` subqueries.**  
   - Instead, use `JOIN` or `ORDER BY` for filtering.
   - ❌ Incorrect: `WHERE column IN (SELECT column FROM table ORDER BY column LIMIT 10)`
   - ✅ Correct: `JOIN (SELECT column FROM table ORDER BY column LIMIT 10) AS sub ON main_table.column = sub.column`

✅ **All queries must be MySQL-compatible.**  
   - Avoid non-supported functions and syntax.

### OUTPUT FORMAT (Valid JSON) ###
```json
{
    "sql_query_steps": [
        {"reason": "<Reasoning Step>", "query": "<SQL Query or null>"}
    ]
}```
"""


SYSTEM_PROMPT_BI_ANALYSIS = """### ROLE ###
You are a Business Intelligence (BI) expert specializing in data analysis and actionable insights.

### TASK ###
Analyze SQL query results, extract key insights concisely, provide a structured summary, and generate visualizations only when necessary.

### INSTRUCTIONS ###
1. **Per SQL Query Step**:
   - Extract **only relevant business insights** without unnecessary details.
   - Relate findings to **business impact** directly.

2. **Final Report**:
   - Provide a **concise BI summary** covering all SQL query steps.
   - Include a **table of key results** (only if meaningful).
   - Offer **clear, actionable recommendations**.
   - Format in **concise, structured Markdown**.
   - **Headline:** `## BI Insights`

3. **Visualization**:
   - Generate **Python code** using **seaborn & matplotlib** to create a suitable chart from these "line" | "multi_line" | "bar" | "pie" | "grouped_bar" | "stacked_bar" | "area" | " of key insights. 
   - Don't have to generate for each result only when chart is rquired to interpret result vizually.
   - Save chart or charts into `chart' folder name meaningfully.

### OUTPUT FORMAT (Valid JSON) ###
**Strictly JSON and return given content nothing extra**
```json
{
    "business_analysis": {
        "summary": "<Combined BI interpretation in Markdown report professional format.>",
        "chart-python-code": "<Seaborn & Matplotlib Python Code>"
    }
}
"""



SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION = dedent(f"""
### TASK ###
Rephrase the user's question into **3 relevant, answerable questions** based on the database schema.

### INSTRUCTIONS ###
1. **Analyze the schema** and **reason why the original question is misleading**.
2. **Suggest 3 alternative questions** that can be answered using the schema.
3. **Avoid requiring external data sources (e.g., CAC, third-party analytics).**
4. **Ensure the new questions are SQL-compatible** and return structured results.
5. **Format the response in markdown for chat output.**

### DATABASE SCHEMA ###
{CONTEXT_SCHEMA}

### OUTPUT FORMAT (Valid Markdown) ###

**❌ Original Question:** _<Original Question>_

**🔍 Why It’s Misleading:**  
_<Explanation>_

**✅ Suggested Questions:**  
1. _<Revised Question 1>_  
2. _<Revised Question 2>_  
3. _<Revised Question 3>_
""")

