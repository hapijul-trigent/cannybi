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
<context>
<DataBase Schema>
-- Customers Table
CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20),
    Address TEXT,
    City VARCHAR(50),
    State VARCHAR(50),
    Country VARCHAR(50),
    ZipCode VARCHAR(20),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE Products (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    ProductName VARCHAR(100) NOT NULL,
    Description TEXT,
    Category VARCHAR(50),
    Price DECIMAL(10,2) NOT NULL,
    StockQuantity INT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales Table
CREATE TABLE Sales (
    SaleID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT,
    SaleDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(12,2) NOT NULL,
    PaymentMethod ENUM('Cash', 'Credit Card', 'Debit Card', 'Online Transfer') NOT NULL,
    Status ENUM('Completed', 'Pending', 'Cancelled') DEFAULT 'Completed',
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE SET NULL
);

--  SalesDetails Table (Many-to-Many Relationship)
CREATE TABLE SalesDetails (
    SaleDetailID INT AUTO_INCREMENT PRIMARY KEY,
    SaleID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    UnitPrice DECIMAL(10,2) NOT NULL,
    SubTotal DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (SaleID) REFERENCES Sales(SaleID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE
);

-- Payments Table
CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    SaleID INT NOT NULL,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Amount DECIMAL(12,2) NOT NULL,
    PaymentMethod ENUM('Cash', 'Credit Card', 'Debit Card', 'Online Transfer') NOT NULL,
    TransactionID VARCHAR(100) UNIQUE NULL,
    FOREIGN KEY (SaleID) REFERENCES Sales(SaleID) ON DELETE CASCADE
);"""

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

