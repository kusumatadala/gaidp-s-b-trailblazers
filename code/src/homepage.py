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
from dashboard import show_dashboard

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
    
    # Then modify the Analyze Button section in home_page():
    if st.button("🔍 Analyze Selected Files", type="primary", use_container_width=True):
        if not st.session_state.selected_files:
            st.warning("Please select at least one rules file")
        elif not transaction_file:
            st.warning("Please upload transaction data CSV")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            with st.spinner("est:3mins,please don't refresh..."):
                status_text.text("Preparing files...")
                time.sleep(0.5)
                progress_bar.progress(10)

                status_text.text("Extracting rules content...")
                time.sleep(0.5)
                progress_bar.progress(30)

                status_text.text("Processing transaction data...")
                time.sleep(0.5)
                progress_bar.progress(50)

                status_text.text("Hang on,Sending to DeepSeek API.....")
                api_response = profile(
                    selected_files=st.session_state.selected_files,
                    transaction_file=transaction_file
                )
                progress_bar.progress(80)

                status_text.text("Processing results...")
                time.sleep(0.5)
                progress_bar.progress(90)

                if api_response is None:
                    progress_bar.progress(100)
                    status_text.error("Analysis failed - please check the logs")
                    time.sleep(2)
                    status_text.empty()
                    progress_bar.empty()
                else:
                    try:
                        content=api_response['choices'][0]['message']['content']
                        analysis_data =extract_json_from_string(content) 
                        try:
                            st.session_state.analysis_result = analysis_data

                            if 'flagged_list' in analysis_data:
                                total = len(analysis_data['transactions_list'])
                                flagged = len(analysis_data['flagged_list'])
                                analysis_data['transaction_stats'] = {
                                    'total_transactions': total,
                                    'flagged_count': flagged,
                                    'failure_rate': round((flagged/total)*100, 2) if total > 0 else 0
                                }

                            analysis_data['transaction_file'] = transaction_file
                            analysis_data['rules_documents']=st.session_state.selected_files

                            progress_bar.progress(100)
                            status_text.success("Analysis complete!")
                            time.sleep(1)
                            status_text.empty()
                            progress_bar.empty()

                            st.session_state["page"] = "dashboard"
                            st.session_state.analysis_result=analysis_data
                            st.rerun()

                        except json.JSONDecodeError:
                            progress_bar.progress(100)
                            status_text.error("Invalid analysis response format")
                            st.text_area("Raw API Response", value=content, height=300)
                            time.sleep(2)
                            status_text.empty()
                            progress_bar.empty()

                    except Exception as e:
                        progress_bar.progress(100)
                        status_text.error(f"Error processing API response: {str(e)}")
                        st.text_area("Raw API Response", value=content, height=300)
                        time.sleep(2)
                        status_text.empty()
                        progress_bar.empty()