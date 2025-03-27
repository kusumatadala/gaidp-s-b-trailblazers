"""
COMPLIANCE DASHBOARD RENDERER
Streamlit application that visualizes transaction compliance analysis results
from JSON data in the specified format.
"""

# --------------------------
# IMPORTS & CONFIGURATION
# --------------------------
import streamlit as st
import json
import pandas as pd
from datetime import datetime

def calculate_risk_level(risk_score):
    """Calculate risk level based on risk score"""
    if risk_score >= 70:
        return "High"
    elif risk_score >= 30:
        return "Medium"
    else:
        return "Low"

def show_dashboard():
    """
    Main function to render the compliance dashboard
    """
    
    # --------------------------
    # DATA LOADING & VALIDATION
    # --------------------------
    data = st.session_state.analysis_result.get('analysis_data', {})

    # --------------------------
    # PAGE CONFIGURATION
    # --------------------------
    st.set_page_config(layout="wide", page_title="Dashboard")
    
    # --------------------------
    # CSS STYLING
    # --------------------------
    st.markdown("""
    <style>
        /* Header styling */
        .header { font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }
        .subheader { font-size: 14px; color: #7f8c8d; margin-bottom: 20px; }
        
        /* Section styling */
        .section-title { 
            font-size: 18px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-top: 20px; 
            margin-bottom: 10px; 
        }
        
        /* Risk level indicators */
        .risk-item { font-size: 14px; margin-left: 15px; margin-bottom: 5px; }
        .risk-high { color: #e74c3c; font-weight: bold; }
        .risk-medium { color: #f39c12; font-weight: bold; }
        .risk-low { color: #27ae60; font-weight: bold; }
        
        /* Table styling */
        .transaction-table { width: 100%; margin-top: 10px; margin-bottom: 20px; }
        
        /* Footer styling */
        .footer { 
            font-size: 12px; 
            color: #7f8c8d; 
            margin-top: 40px; 
            border-top: 1px solid #eee; 
            padding-top: 10px; 
        }
    </style>
    """, unsafe_allow_html=True)

    # --------------------------
    # HEADER SECTION
    # --------------------------
    st.markdown('<div class="header">Analysis Results</div>', unsafe_allow_html=True)
    
    # Create two columns for header content
    col1, col2 = st.columns([3, 2])
    with col1:
        # Show analyzed documents
        st.markdown(f"""
        <div class="subheader">
        <strong>Analysed</strong><br>
        {data.get('rules_list', [{}])[0].get('origin', 'sample_regulation.txt').split(',')[0]}<br>
        against<br>
        Transaction Data
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Show analysis timestamp (right-aligned)
        st.markdown(f"""
        <div class="subheader" style="text-align: right;">
        {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --------------------------
    # RISK SUMMARY SECTION
    # --------------------------
    st.markdown('<div class="section-title">Risk Summary</div>', unsafe_allow_html=True)
    
    # Calculate risk counts from transactions
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    
    for tx in data.get('transactions_list', []):
        risk_level = calculate_risk_level(tx.get('risk_score', 0))
        if risk_level == "High":
            high_risk += 1
        elif risk_level == "Medium":
            medium_risk += 1
        else:
            low_risk += 1
    
    total_transactions = len(data.get('transactions_list', []))
    flagged_count = len(data.get('flagged_list', []))
    
    # Display risk metrics in columns
    risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
    with risk_col1:
        st.markdown(f'<div class="risk-item risk-high">• High Risk: {high_risk}</div>', 
                   unsafe_allow_html=True)
    with risk_col2:
        st.markdown(f'<div class="risk-item risk-medium">• Medium Risk: {medium_risk}</div>', 
                   unsafe_allow_html=True)
    with risk_col3:
        st.markdown(f'<div class="risk-item risk-low">• Low Risk: {low_risk}</div>', 
                   unsafe_allow_html=True)
    with risk_col4:
        st.markdown(f'<div class="risk-item">• Total Transactions: {total_transactions}</div>', 
                   unsafe_allow_html=True)
    
    st.markdown("---")

    # --------------------------
    # TRANSACTION ANALYSIS SECTION
    # --------------------------
    st.markdown('<div class="section-title">Transaction Analysis</div>', unsafe_allow_html=True)
    
    # Prepare transaction data for display
    transaction_display = []
    for tx in data.get('transactions_list', []):
        # Note: Corrected field name from 'voilated_rules_list' to 'violated_rules_list'
        violated_rules = ", ".join(tx.get('voilated_rules_list', []))
        risk_level = calculate_risk_level(tx.get('risk_score', 0))
        
        transaction_display.append({
            "Transaction ID": tx.get('transaction_id', ''),
            "Risk Level": risk_level,
            "Violated Rules": violated_rules,
            "Explanation": tx.get('explanation', ''),
            "Risk Score": tx.get('risk_score', 0),
            "Flagged": "Yes" if tx.get('flag', False) else "No"
        })
    
    # Display transaction table if data exists
    if transaction_display:
        df = pd.DataFrame(transaction_display)
        
        # Color coding for risk levels
        def color_risk(val):
            if isinstance(val, str):
                if val.lower() == "high": 
                    return 'color: #e74c3c; font-weight: bold;'
                elif val.lower() == "medium": 
                    return 'color: #f39c12; font-weight: bold;'
                elif val.lower() == "low": 
                    return 'color: #27ae60; font-weight: bold;'
            return 'color: #7f8c8d;'
        
        # Apply styling and display table
        styled_df = df.style.applymap(color_risk, subset=['Risk Level'])
        st.table(styled_df)
    else:
        st.warning("No transaction data available")
    
    # Show entries count
    st.markdown(f"*Showing 1 to {min(10, total_transactions)} of {total_transactions} entries*")
    
    # Calculate and display median risk
    risk_scores = [tx.get('risk_score', 0) for tx in data.get('transactions_list', [])]
    median_risk = pd.Series(risk_scores).median() if risk_scores else 0
    st.markdown(f"**Median Risk Score:** {median_risk:.2f}")
    
    st.markdown("---")

    # --------------------------
    # FAILURE TRANSACTIONS SECTION
    # --------------------------
    st.markdown('<div class="section-title">Flagged Transactions</div>', unsafe_allow_html=True)
    
    # Create tabs for different failure details
    tab1, tab2, tab3 = st.tabs(["Review Status", "Actions", "Results"])
    
    with tab1:  # Review Status
        for tx_id in data.get('flagged_list', []):
            st.markdown(f"• **{tx_id}**: Needs Review")
    
    with tab2:  # Actions
        for tx_id in data.get('flagged_list', []):
            tx = next((t for t in data.get('transactions_list', []) 
                      if t.get('transaction_id') == tx_id), None)
            if tx:
                st.markdown(f"• **{tx_id}**:")
                remediation = tx.get('remediation', 'None')
                if isinstance(remediation, list):
                    for action in remediation:
                        st.markdown(f"  - {action}")
                else:
                    st.markdown(f"  - {remediation}")
    
    with tab3:  # Results
        for tx_id in data.get('flagged_list', []):
            tx = next((t for t in data.get('transactions_list', []) 
                      if t.get('transaction_id') == tx_id), None)
            if tx:
                st.markdown(f"• **{tx_id}**: Found {len(tx.get('voilated_rules_list', []))} violations")
    
    st.markdown("---")

    # --------------------------
    # RULES SECTION
    # --------------------------
    st.markdown('<div class="section-title">Applied Rules</div>', unsafe_allow_html=True)
    
    rules_df = pd.DataFrame(data.get('rules_list', []))
    if not rules_df.empty:
        st.table(rules_df[['ruleid', 'description', 'severity']])
    else:
        st.warning("No rules data available")
    
    st.markdown("---")

    # --------------------------
    # EXPORT OPTIONS SECTION
    # --------------------------
    st.markdown('<div class="section-title">Export Options</div>', unsafe_allow_html=True)
    
    # Export buttons in columns
    col1, col2 = st.columns(2)
    with col1:
        st.button("EXPORT CSV", key="csv_export")
    with col2:
        st.button("EXPORT PDF", key="pdf_export")
    
    st.markdown("---")

    # --------------------------
    # FOOTER SECTION
    # --------------------------
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("**Auditor Assist 2.0**")
    st.markdown("Federal Reserve Compliance Test | Regulatory Analysis | Compliance Auditing | Elema Assessment")
    st.markdown("© 2025 Auditor Assist Technology Powered by Gawick L.S.P.R.")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# EXAMPLE USAGE
# --------------------------
# if __name__ == "__main__":
#     # Sample data matching the required JSON structure
#     sample_data = {
#         'analysis_data': {
#             'rules_list': [
#                 {'ruleid': 'GEN001', 'description': 'Transaction date must not be in the future.', 'origin': 'Comprehensive Rules for Transaction Data Audit in the USA, General Data Integrity Rules', 'severity': 'High', 'remarks': 'Reject transactions with future dates.'},
#                 # ... (other rules)
#             ],
#             'transactions_list': [
#                 {'transaction_id': '6355745', 'voilated_rules_list': [], 'flag': False, 'risk_score': 0, 'explanation': 'No rules violated.', 'remediation': 'do something', 'remarks': 'Valid transaction.', 'risk_segments': {'credit_risk': 0, 'transaction_risk': 0, 'market_risk': 0, 'operational_risk': 0}, 'sugggestions': 'arey something man'},
#                 # ... (other transactions)
#             ],
#             'flagged_list': ['6143225', '6058140'],
#             'risk_scoring_definition': 'Risk scoring is based on the severity of violated rules and the potential impact on financial integrity. Scores range from 0 (no risk) to 100 (critical risk). Each risk segment (credit, transaction, market, operational) is scored individually, and an overall score is calculated as the average of these segments.'
#         }
#     }
    
#     st.session_state.analysis_result = sample_data
#     show_dashboard()