import streamlit as st
import PyPDF2
from docx import Document
from io import BytesIO
import pandas as pd
import time
import json
import os

content='```json\n{\n  "transaction_analysis": {\n    "headers": ["UserId", "TransactionId", "TransactionTime", "ItemCode", "ItemDescription", "NumberOfItemsPurchased", "CostPerItem", "Country"],\n    "inferred_data_types": {\n      "UserId": "integer",\n      "TransactionId": "integer",\n      "TransactionTime": "datetime",\n      "ItemCode": "integer",\n      "ItemDescription": "string",\n      "NumberOfItemsPurchased": "integer",\n      "CostPerItem": "float",\n      "Country": "string"\n    },\n    "validated_rules": [\n      {\n        "rule_id": "GEN001",\n        "category": "General Data Integrity",\n        "description": "UserId cannot be negative except for special cases.",\n        "condition": "UserId >= 0 or UserId == -1",\n        "severity": "High",\n        "origin": "Generic rule",\n        "action": "Flag transactions with invalid UserId for manual review.",\n        "flagged_transactions": ["-1,6143225,Mon Sep 10 11:58:00 IST 2018,1733592,WASHROOM METAL SIGN,3,3.4,United Kingdom", "-1,6143225,Mon Sep 10 11:58:00 IST 2018,447867,SKULLS WRITING SET ,120,1.15,United Kingdom", "-1,6058140,Mon Jul 02 07:33:00 IST 2018,435225,LUNCH BAG RED RETROSPOT,60,6.85,United Kingdom"]\n      },\n      {\n        "rule_id": "GEN002",\n        "category": "General Data Integrity",\n        "description": "TransactionTime must not be in the future.",\n        "condition": "TransactionTime <= current_date",\n        "severity": "High",\n        "origin": "🚀 Comprehensive Rules for Transaction Data Audit in the USA 🇺🇸.docx, General Da ata Integrity Rules",\n        "action": "No future dated transactions found.",\n        "flagged_transactions": []\n      },\n      {\n        "rule_id": "GEN003",\n        "category": "General Data Integrity",\n        "description": "TransactionId must be unique.",\n        "condition": "TransactionId must be unique",\n        "severity": "High",\n        "origin": "🚀 Comprehensive Rules for Transaction Data Audit in the USA 🇺🇸.docx, General Data Integrity y Rules",\n        "action": "Flag duplicates for review.",\n        "flagged_transactions": ["-1,6143225,Mon Sep 10 11:58:00 IST 2018,1733592,WASHROOM METAL SIGN,3,3.4,United Kingdom", "-1,6143225,Mon Sep 10 11:58:00 IST 2018,447867,SKULLS WRITING SET ,120,1.15,United Kingdom"]\n      },\n      {\n        "rule_id": "AML001",\n        "category": "AML & Fraud Detection",\n        "description": "Transactions above $10,000 must be reported to FinCEN.",\n        "condition": "NumberOfItemsPurchased * CostPerItem > 10000",\n        "severity": "High",\n        "origin": "🚀 Comprehensive Rules for Transaction Data Audit in the USA 🇺🇸.docx, AML & Fraud Detection Rules",\n        "action": "No transactions above $10,000 found.",\n        "flagged_transactions": []\n        },\n      {\n        "rule_id": "AML002",\n        "category": "AML & Fraud Detection",\n        "description": "Multiple transactions under $10,000 by the same user within 24 hours should be flagged for structuring (AML).",\n        "condition": "SUM(NumberOfItemsPurchased * CostPerItem by UserId) < 10000 in 24 hours",\n        "severity": "High",\n        "origin": "🚀 Comprehensive Rules for Transaction Data Audit in the USA 🇺🇸.docx, AML & Fraud Detect tion Rules",\n        "action": "No structuring detected.",\n        "flagged_transactions": []\n      },\n      {\n        "rule_id": "AML003",\n        "category": "AML & Fraud Detection",\n        "description": "Transactions originating from high-risk countries must be flagged.",\n        "condition": "Country in high-risk list",\n        "severity": "High",\n        "origin": "🚀 Comprehensive Rules for Transaction Data Audit in the USA 🇺🇸.docx, AML & Fra aud Detection Rules",\n        "action": "No high-risk country transactions found.",\n        "flagged_transactions": []\n      },\n      {\n        "rule_id": "GEN004",\n        "category": "General Data Integrity",\n        "description": "ItemDescription cannot be numerical.",\n        "condition": "ItemDescription is not numerical",\n        "severity": "Medium",\n        "origin": "Generic rule",\n        "action": "No numerical ItemDescription found.",\n        "flagged_transactions": []\n      },\n      {\n        "rule_id": "GEN005",\n        "category": "General Data Integrity",\n        "description": "Transactions older than 365 days should trigger a data validation alert.",\n        "condition": "TransactionTime < current_date - 365 days",\n        "severity": "Medium",\n        "origin": "Generic rule",\n        "action": "Flag transactions older than 365 days.",\n        "flagged_transactions": ["278166,6355745,Sat Feb 02 12:50:00 IST 2019,465549,FAMILY ALBUM WHITE PICTURE FRAME,6,11.73,United Kingdom", "337701,6283376,Wed Dec 26 09:06:00 IST 2018,482370,LONDON BUS COFFEE MUG,3,3.52,United Kingdom", "267099,6385599,Fri Feb 15 09:45:00 IST 2019,490728,SET 12 COLOUR PENCILS DOLLY GIRL ,72,0.9,France", "380478,6044973,Fri Jun 22 07:14:00 IST 2018,459186,UNION JACK FLAG LUGGAGE TAG,3,1.73,United Kingdom", "-1,6143225,Mon Sep 10 11:58:00 IST 2018,1733592,WASHROOM METAL SIGN,3,3.4,United Kingdom", "285957,6307136,Fri Jan 11 09:50:00 IST 2019,1787247,CUT GLASS T-LIGHT HOLDER OCTAGON,12,3.52,United Kingdom", "345954,6162981,Fri Sep 28 10:51:00 IST 2018,471576,NATURAL SLATE CHALKBOARD LARGE ,9,6.84,United Kingdom", "-1,6143225,Mon Sep 10 11:58:00 IST 2018,447867,SKULLS WRITING SET ,120,1.15,United Kingdom", "339822,6255403,Mon Dec 10 09:23:00 IST 2018,1783845,MULTI COLOUR SILVER T-LIGHT HOLDER,36,1.18,United Kingdom", "328440,6387425,Sat Feb 16 10:35:00 IST 2019,494802,SET OF 6 RIBBONS PERFECTLY PRETTY  ,36,3.99,United Kingdom", "316848,6262696,Sat Dec 15 10:05:00 IST 2018,460215,RED  HARMONICA IN BOX ,36,1.73,United Kingdom", "372897,6199061,Mon Oct 29 09:04:00 IST 2018,459669,WOODEN BOX OF DOMINOES,3,1.73,United Kingdom", "364791,6358242,Sun Feb 03 09:25:00 IST 2019,486276,SET OF 5 MINI GROCERY MAGNETS,3,2.88,United Kingdom", "-1,6058140,Mon Jul 02 07:33:00 IST 2018,435225,LUNCH BAG RED RETROSPOT,60,6.85,United Kingdom"]\n      }\n    ],\n    "risk_scoring": {\n      "definition": "Risk scoring is a dynamic mechanism that assigns a risk value to each transaction based on the severity and number of rules violated. The score is adjusted based on transaction patterns and historical violations.",\n      "segments": {\n        "credit_risk": {\n          "score": 0,\n          "definition": "Risk of loss due to a borrower\'s failure to make payments as agreed."\n        },\n        "transaction_risk": {\n          "score": 20,\n          "definition": "Risk associated with the transaction itself, including fraud and AML risks."\n        },\n        "market_risk": {\n          "score": 0,\n          "definition": "Risk of losses due to changes in market conditions."\n        },\n        "operational_risk": {\n          "score": 10,\n          "definition": "Risk of loss resulting from inadequate or failed internal processes, people, or systems."\n        },\n        "overall_risk_score": 30,\n        "scale": "0-100, where 0-30 is Low, 31-60 is Medium, 61-100 is High"\n      }\n    },\n    "suggestions": [\n      {\n        "transaction": "-1,6143225,Mon Sep 10 11:58:00 IST 2018,1733592,WASHROOM METAL SIGN,3,3.4,United Kingdom",\n        "suggestion": "Review UserId -1 for validity. Check for duplicate TransactionId 6143225."\n      },\n      {\n      L SIGN,3,3.4,United Kingdom",\n        "suggestion": "Review UserId -1 for validity. Check for duplicate TransactionId 6143225."\n      },\n      {\n      L SIGN,3,3.4,United Kingdom",\n        "suggestion": "Review UserId -1 for validity. Check for duplicate TransactionId 6143225."\n      },\n      {\n        "transaction": "-1,6143225,Mon Sep 10 11:58:00 IST 2018,447867,SKULLS WRITING SET ,120,1.15,United Kingdom",\n        "suggestion": "Review UserId -1 for validity. Check for duplicate TransactionId 6143225."\n      },\n      {\n        "transaction": "-1,6058140,Mon Jul 02 07:33:00 IST 2018,435225,LUNCH BAG RED RETROSPOT,60,6.85,United Kingdom",\n        "suggestion": "Review UserId -1 for validity."\n      }\n    ],\n    "notes": "The risk score is dynamic and may change with additional data. High-risk transactions should be manually reviewed for further action."\n  }\n}\n```'
# Helper functions
def extract_text(file):
    """Extract text from PDF or DOCX files"""
    content = file.read()
    
    try:
        if file.name.endswith('.pdf'):
            pdf = PyPDF2.PdfReader(BytesIO(content))
            return "\n".join([page.extract_text() for page in pdf.pages])
        elif file.name.endswith('.docx'):
            doc = Document(BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return content.decode('utf-8')
    except Exception as e:
        st.error(f"Error reading {file.name}: {str(e)}")
        return None
def extract_json_from_string(input_str):
    # Find the start and end of the JSON content
    start_index = input_str.find('```json\n') + len('```json\n')
    end_index = input_str.find('\n```', start_index)
    
    if start_index == -1 or end_index == -1:
        raise ValueError("Could not find JSON content in the string")
    
    # Extract the JSON content
    json_content = input_str[start_index:end_index].strip().replace("\n", "")
    
    # Parse the JSON content into a Python dictionary
    try:
        json_obj = json.loads(json_content)
        print(json_obj)
        return json_obj
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")