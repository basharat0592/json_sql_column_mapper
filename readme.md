## `README.md`

````md
# JSON to SQL Column Mapper

A Streamlit web app that helps map JSON properties to SQL table columns.

Users can paste a SQL `CREATE TABLE` statement and a JSON payload, and the app will suggest mappings between JSON keys and SQL columns using a mix of fuzzy string matching and semantic similarity powered by Sentence Transformers.

## Features

- Extracts columns from SQL `CREATE TABLE` statements.
- Supports JSON objects and arrays.
- Uses fuzzy matching (RapidFuzz) and semantic matching (SentenceTransformers).
- Easy copy-paste sample data in the sidebar for quick testing.
- Interactive controls for semantic match threshold.

## Getting Started

### Prerequisites

- Python 3.8+
- `pip` package manager

### Install dependencies

```bash
pip install -r requirements.txt
````

### Run the app

```bash
streamlit run json_sql_mapper.py
```

### Usage

1. Paste your SQL `CREATE TABLE` statement into the left input.
2. Paste your JSON payload into the right input.
3. Adjust semantic matching options if needed.
4. View the suggested mapping results.

## Example Input

### Sample SQL

```sql
CREATE TABLE Customers (
    customer_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email_address VARCHAR(100),
    signup_date DATE,
    is_active BIT
);
```

### Sample JSON

```json
{
  "CustomerId": 123,
  "FirstName": "John",
  "LastName": "Doe",
  "Email": "john.doe@example.com",
  "JoinDate": "2023-01-01",
  "enabled": true
}
```

## License

MIT License

## Author

Basharat Hussain — [basharathussain05@gmail.com](mailto:basharathussain05@gmail.com)