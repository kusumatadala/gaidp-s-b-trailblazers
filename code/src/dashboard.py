import streamlit as st
import PyPDF2
from docx import Document
from io import BytesIO
import pandas as pd
import time
import json
import os
import requests
from util import *
from profiliing import profile
from rulesgeneration import generate_rules
import time

def show_dashboard(analysis_json):
    """Displays a compliance dashboard matching the provided design style."""
    
    # Load JSON if input is string
    if isinstance(analysis_json, str):
        data = json.loads(analysis_json)
    else:
        data = analysis_json
    
    analysis = data['transaction_analysis']
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate risk distribution
    risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    for tx in analysis['risk_scoring']['transaction_scores']:
        if tx['risk_score'] >= 40:
            risk_counts['High'] += 1
        elif tx['risk_score'] >= 20:
            risk_counts['Medium'] += 1
        elif tx['risk_score'] > 0:
            risk_counts['Low'] += 1
    
    # Print dashboard header
    print("\n" + "#"*60)
    print("# Analysis Results".ljust(59) + "#")
    print("#"*60)
    print(f"\n{'**Analysed**':<20}")
    print("sample_regulation.txt")
    print("against")
    print("sample_transactions.json\n")
    print(f"{'2025-03-26 13:25':>60}\n")
    print("-"*60)
    
    # Risk Summary section
    print("\n## Risk Summary\n")
    print(f"- **High Risk** {risk_counts['High']}")
    print(f"  Medium Risk {risk_counts['Medium']}")
    print(f"- **Low Risk** {risk_counts['Low']}")
    print(f"- **Total Transactions** {len(analysis['risk_scoring']['transaction_scores'])}\n")
    print("-"*60)
    
    # Transaction Analysis table
    print("\n## Transaction Analysis\n")
    print("| Show ID | entries    |")
    print("|---|---|")
    print("| Transaction ID | Risk Level | Explanation    |")
    
    # Display top 5 transactions by risk
    sorted_tx = sorted(analysis['risk_scoring']['transaction_scores'], 
                      key=lambda x: x['risk_score'], reverse=True)[:5]
    
    for tx in sorted_tx:
        risk_level = ("High" if tx['risk_score'] >= 40 else 
                     "Medium" if tx['risk_score'] >= 20 else "Low")
        first_flag = tx['flags'][0] if tx['flags'] else "No flags"
        print(f"| {tx['TransactionId']} | {risk_level} | {first_flag[:30]}... |")
    
    print("\n**Median**\n")
    
    # Failure transactions section
    print("**Failure transactions:**")
    print("- **Review Status:**")
    print("  - Actions")
    print("  - **Results**")
    print("  - **Q, VIEW DETAILS**\n")
    
    # Threshold visualization
    print("**TX/OCI:**")
    print("Logo with transfer exceeding threshold\n")
    
    # Pagination
    print("**Showing 1 to 2 of 2 entries:**\n")
    
    # Prediction section
    print("**Predicts:**")
    print("**Need**\n")
    print("-"*60)
    
    # Export options
    print("\n## EXPORT CSV")
    print("**EXPORT PDF**\n")
    print("-"*60)
    
    # Footer
    print("\n## Auditor Assist 2.0")
    print("Federal Reserve Compliance Test\n")
    print("Regulatory Analysis")
    print("Compliance Auditing")
    print("Elema Assessment\n")
    print("© 2025 Auditor Assist Technology")
    print("Powered by Gawick L.S.P.R.")

# Example usage:
# show_dashboard(json_output)