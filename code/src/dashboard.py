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

def show_dashboard(analysis_data):
    """
    Main function to render the compliance dashboard
    
    Args:
        analysis_data: JSON string containing analysis results with:
            - rules_list: List of rule objects
            - transactions_list: List of analyzed transactions
            - flagged_list: IDs of non-compliant transactions
            - risk_scoring_definition: Risk calculation parameters
    """
    
    # --------------------------
    # DATA LOADING & VALIDATION
    # --------------------------
    try:
        # Parse JSON input
        data = json.loads(analysis_data)
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON data provided")
        return

    # --------------------------
    # PAGE CONFIGURATION
    # --------------------------
    st.set_page_config(layout="wide", page_title="Auditor Assist 2.0")
    
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
    high_risk = sum(1 for tx in data.get('transactions_list', []) 
                 if tx.get('risk_level', '').lower() == 'high')
    medium_risk = sum(1 for tx in data.get('transactions_list', []) 
                  if tx.get('risk_level', '').lower() == 'medium')
    low_risk = sum(1 for tx in data.get('transactions_list', []) 
                 if tx.get('risk_level', '').lower() == 'low')
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
        # Concatenate violated rule IDs
        violated_rules = ", ".join([vr.get('ruleid', '') 
                                  for vr in tx.get('violated_rules_list', [])])
        
        transaction_display.append({
            "Transaction ID": tx.get('transaction_id', ''),
            "Risk Level": tx.get('risk_level', '').capitalize(),
            "Violated Rules": violated_rules,
            "Explanation": "; ".join(tx.get('explanation', [])),
            "Risk Score": tx.get('risk_score', 0)
        })
    
    # Display transaction table if data exists
    if transaction_display:
        df = pd.DataFrame(transaction_display)
        
        # Color coding for risk levels
        def color_risk(val):
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
    st.markdown('<div class="section-title">Failure transactions</div>', unsafe_allow_html=True)
    
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
                for action in tx.get('remediation', []):
                    st.markdown(f"  - {action}")
    
    with tab3:  # Results
        for tx_id in data.get('flagged_list', []):
            tx = next((t for t in data.get('transactions_list', []) 
                      if t.get('transaction_id') == tx_id), None)
            if tx:
                st.markdown(f"• **{tx_id}**: Found {len(tx.get('violated_rules_list', []))} violations")
    
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
#         "rules_list": [
#             {
#                 "ruleid": "AML-001",
#                 "description": "Transactions over $10,000 require additional verification",
#                 "origin": "sample_regulation.txt, Section 5.2",
#                 "severity": "high",
#                 "remarks": "Applies to all cross-border transactions"
#             }
#         ],
#         "transactions_list": [
#             {
#                 "transaction_id": "TX1001",
#                 "violated_rules_list": [{"ruleid": "AML-001", "origin": "sample_regulation.txt, Section 5.2"}],
#                 "flag": True,
#                 "risk_score": 0.85,
#                 "risk_level": "high",
#                 "explanation": ["Amount exceeds threshold"],
#                 "remediation": ["Freeze transaction"],
#                 "remarks": "International transfer",
#                 "risk_segments": ["cross-border"],
#                 "suggestions": ["Enhanced due diligence"]
#             }
#         ],
#         "flagged_list": ["TX1001"],
#         "risk_scoring_definition": {
#             "high_risk_threshold": 0.7,
#             "medium_risk_threshold": 0.4,
#             "low_risk_threshold": 0.1,
#             "calculation_method": "weighted_violation_score"
#         }
#     }
    
#     # Convert to JSON and render
#     render_dashboard(json.dumps(sample_data))