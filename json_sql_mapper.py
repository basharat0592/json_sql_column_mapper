import streamlit as st

# Set Streamlit page config
st.set_page_config(page_title="JSON to SQL Column Mapper", layout="centered")

import json
import re
import sqlparse
import pandas as pd
from rapidfuzz import process
from sentence_transformers import SentenceTransformer, util

# Load model
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# Utility functions
def normalize(name):
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    return name.replace('-', '_').replace(' ', '_')

def semantic_match(norm_key, norm_columns, original_columns, threshold=0.6):
    key_vec = model.encode([norm_key], convert_to_tensor=True)
    col_vecs = model.encode(norm_columns, convert_to_tensor=True)
    scores = util.cos_sim(key_vec, col_vecs)[0]
    best_idx = scores.argmax().item()
    best_score = scores[best_idx].item()
    if best_score >= threshold:
        return original_columns[best_idx]
    else:
        return "❓ No Match"

def map_json_to_columns(json_keys, table_columns, use_semantic=False, threshold=0.6):
    normalized_columns = [normalize(col) for col in table_columns]
    mapping = {}
    for key in json_keys:
        norm_key = normalize(key)
        match, score, _ = process.extractOne(norm_key, normalized_columns)
        if score > 85:
            matched_col = table_columns[normalized_columns.index(match)]
        elif use_semantic:
            matched_col = semantic_match(norm_key, normalized_columns, table_columns, threshold)
        else:
            matched_col = "❓ No Match"
        mapping[key] = matched_col
    return mapping

def extract_columns_from_sql(sql_text):
    parsed = sqlparse.parse(sql_text)[0]
    columns = []
    for token in parsed.tokens:
        if token.ttype is None and isinstance(token, sqlparse.sql.Parenthesis):
            content = token.value.strip("()")
            for line in content.split(","):
                parts = line.strip().split()
                if parts:
                    col = parts[0].strip("`[]\"")
                    columns.append(col)
    return columns

# --- Sidebar: Sample Data ---
st.sidebar.markdown("### 📋 Sample SQL DDL")
st.sidebar.code("""CREATE TABLE Customers (
    customer_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email_address VARCHAR(100),
    signup_date DATE,
    is_active BIT,
    loyalty_points INT,
    referrer_code VARCHAR(50),
    profile_picture_url TEXT,
    marketing_opt_in BOOLEAN,
    birth_date DATE
);""", language="sql")

st.sidebar.markdown("### 📦 Sample JSON")
st.sidebar.code("""{
  "CustomerId": 789,                  
  "FirstName": "Alice",                 
  "LastName": "Smith",                  
  "Email": "alice.smith@example.com",   
  "JoinDate": "2022-11-11",            
  "enabled": false,                    
  "Points": 1200,                       
  "Referral": "ABC123",                
  "Avatar": "https://example.com/img",  
  "AgreeToMarketing": true,            
  "DOB": "1995-05-15",                  
  "Region": "North America"            
}
""", language="json")

# --- Main App ---
st.title("🔄 JSON → SQL Column Mapper")

# Step 1: Schema Input
st.markdown("### 1. Define Your Table Schema")
ddl_input = st.text_area("Paste SQL CREATE TABLE statement", height=200)

columns = []
if ddl_input:
    try:
        columns = extract_columns_from_sql(ddl_input)
        st.success(f"Extracted {len(columns)} columns from SQL.")
    except Exception as e:
        st.error(f"Failed to parse SQL: {e}")

# Step 2: JSON Input
st.markdown("### 2. Paste JSON Payload")
json_text = st.text_area("Paste JSON here", height=200)

if json_text:
    try:
        json_data = json.loads(json_text)
    except:
        st.error("❌ Invalid JSON!")
        json_data = None
else:
    json_data = None

# Step 3: Mapping Controls
if columns and json_data:
    st.markdown("### 3. Mapping Controls")
    use_semantic = st.checkbox("Use Semantic Matching", value=True)
    threshold = st.slider("Semantic Match Threshold", 0.0, 1.0, 0.6, 0.01, help="Increase for stricter matching.")

    # Support array of objects
    if isinstance(json_data, list):
        json_keys = list(json_data[0].keys())
        json_data = json_data[0]
    else:
        json_keys = list(json_data.keys())

    # Perform mapping
    mapping = map_json_to_columns(json_keys, columns, use_semantic=use_semantic, threshold=threshold)

    # Display result
    st.markdown("### 4. Mapping Results")
    st.dataframe([{"JSON Property": k, "Matched Column": v} for k, v in mapping.items()])
