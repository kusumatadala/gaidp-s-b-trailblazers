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

# Initialize session state
if 'uploaded_rules' not in st.session_state:
    st.session_state.uploaded_rules = {}
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []
if 'generated_results' not in st.session_state:
    st.session_state.generated_results = {}
if 'viewing_file' not in st.session_state:
    st.session_state.viewing_file = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None



# Main app
def home_page():
    st.title("Financial Rules Analyzer")
    st.write("Upload rules documents and transaction files for analysis")
    
    # Section 1: Upload Rules Files
    st.header("📁 Upload Rules Documents (PDF/DOCX)")
    new_files = st.file_uploader(
        "Select files",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="rules_uploader",
        label_visibility="collapsed"
    )
    
    if new_files:
        for file in new_files:
            if file.name not in st.session_state.uploaded_rules:
                st.session_state.uploaded_rules[file.name] = {
                    "file": file,
                    "processed": False,
                    "selected": False
                }
        st.success(f"Added {len(new_files)} new file(s)")
    
    # Section 2: Manage Uploaded Files
    st.header("📋 Uploaded Rules Documents")
    if not st.session_state.uploaded_rules:
        st.info("No documents uploaded yet")
    else:
        # Create a table-like display with 4 columns
        col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
        with col1:
            st.write("**Document Name**")
        with col2:
            st.write("**Actions**")
        with col3:
            st.write("**View**")
        with col4:
            st.write("**Select**")
        
        for filename, data in st.session_state.uploaded_rules.items():
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            
            with col1:
                st.write(filename)
            
            with col2:
                if st.button("Generate Rules", key=f"gen_{filename}"):
                    with st.spinner(f"Processing {filename}..."):
                        result = generate_rules(data['file'])
                        if result:
                            st.session_state.generated_results[filename] = result
                            st.session_state.uploaded_rules[filename]['processed'] = True
                            st.rerun()
            
            with col3:
                if data['processed']:
                    if st.button("👁️ View", key=f"view_{filename}"):
                        st.session_state.viewing_file = filename
                        st.session_state.show_results = True
                        st.rerun()
            
            with col4:
                selected = st.checkbox(
                    "Select", 
                    value=data['selected'],
                    key=f"select_{filename}",
                    label_visibility="collapsed"
                )
                if selected != data['selected']:
                    st.session_state.uploaded_rules[filename]['selected'] = selected
                    if selected:
                        st.session_state.selected_files.append(filename)
                    else:
                        st.session_state.selected_files.remove(filename)
        
        # Save selection button
        if st.button("💾 Save Selection"):
            selected_count = len(st.session_state.selected_files)
            st.success(f"Saved selection of {selected_count} file(s)")
    
    # Section 3: Generated Results (only shown when viewing a file)
    if st.session_state.show_results and st.session_state.viewing_file:
        st.header("📊 Generated Rules")
        
        # Display close button at top right
        close_col1, close_col2 = st.columns([4, 1])
        with close_col2:
            if st.button("❌ Close Results"):
                st.session_state.show_results = False
                st.session_state.viewing_file = None
                st.rerun()
        
        # Display the content
        result = st.session_state.generated_results.get(st.session_state.viewing_file, {})
        st.markdown(f"### {st.session_state.viewing_file}")
        
        if 'content' in result:
            st.markdown(result['content'])
            
            # Show usage stats if available
            if 'usage' in result:
                st.write("**API Usage Statistics:**")
                st.json(result['usage'])
        else:
            st.warning("No analysis content available")
        
        # Download button
        if 'content' in result:
            st.download_button(
                label="⬇️ Download Results",
                data=result['content'],
                file_name=f"analysis_{st.session_state.viewing_file}.md",
                key=f"dl_{st.session_state.viewing_file}"
            )
    
    # Section 4: Transaction Data
    st.header("💳 Upload Transaction Data (CSV)")
    transaction_file = st.file_uploader(
        "Select CSV file",
        type=["csv"],
        key="txn_uploader",
        label_visibility="collapsed"
    )
    
    if transaction_file:
        try:
            df = pd.read_csv(transaction_file)
            st.success("CSV file loaded successfully")
            with st.expander("View Transaction Data"):
                st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")
    
    # Analyze Button
    if st.button("🔍 Analyze Selected Files", type="primary", use_container_width=True):
        if not st.session_state.selected_files:
            st.warning("Please select at least one rules file")
        elif not transaction_file:
            st.warning("Please upload transaction data CSV")
        else:
            with st.spinner("Analyzing files..."):
                # Call the profile function with selected files and transaction data
                api_response = profile(
                    selected_files=st.session_state.selected_files,
                    transaction_file=transaction_file
                )
                
                if api_response is None:
                    st.error("Analysis failed - please check the logs")
                else:
                    try:
                        # Process the API response
                        content = api_response.get('choices', [{}])[0].get('message', {}).get('content', '')
                        
                        # Store results
                        st.session_state.analysis_result = {
                            "files_analyzed": st.session_state.selected_files,
                            "findings": [],
                            "recommendations": [],
                            "content": content,
                            "usage": api_response.get('usage', {}),
                            "compliance_score": "N/A",
                            "risk_level": "To be determined"
                        }
                        
                        # Try to parse structured data from response
                        try:
                            parsed_content = json.loads(content)
                            if isinstance(parsed_content, dict):
                                if 'analysis_summary' in parsed_content:
                                    summary = parsed_content['analysis_summary']
                                    st.session_state.analysis_result.update({
                                        "compliance_score": summary.get("overall_risk_score", "N/A"),
                                        "risk_level": summary.get("overall_risk_level", "To be determined")
                                    })
                                if 'recommendations' in parsed_content:
                                    st.session_state.analysis_result['recommendations'] = parsed_content['recommendations']
                        except json.JSONDecodeError:
                            # Content is not JSON, treat as plain text
                            st.session_state.analysis_result['content'] = content
                        
                        st.success("Analysis complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error processing API response: {str(e)}")
    
    # Display analysis results if available
    if st.session_state.analysis_result:
        st.subheader("Analysis Results")
        st.write(f"**Files Analyzed:** {', '.join(st.session_state.analysis_result['files_analyzed'])}")
        st.write(f"**Compliance Score:** {st.session_state.analysis_result['compliance_score']}")
        st.write(f"**Risk Level:** {st.session_state.analysis_result['risk_level']}")
        
        if st.session_state.analysis_result['content']:
            st.subheader("Detailed Analysis")
            st.markdown(st.session_state.analysis_result['content'])
        
        if st.session_state.analysis_result['recommendations']:
            st.subheader("Recommendations")
            for rec in st.session_state.analysis_result['recommendations']:
                st.write(f"- {rec}")
        
        if 'usage' in st.session_state.analysis_result:
            st.write("**API Usage Statistics:**")
            st.json(st.session_state.analysis_result['usage'])

# Run the app
if __name__ == "__main__":
    home_page()