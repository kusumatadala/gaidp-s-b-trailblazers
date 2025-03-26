import streamlit as st
import PyPDF2
from docx import Document
from io import BytesIO
import pandas as pd
import time
import json
import os
import requests
import random

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

def generate_rules(file):
    """Send file to DeepSeek API with prompt from rules_prompt.txt"""
    # Read the prompt template
    try:
        with open("rules_prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read().strip()
    except FileNotFoundError:
        prompt = "Please analyze this document and extract all relevant rules and regulations."
        st.warning("Using default prompt (rules_prompt.txt not found)")

    # Extract text from file
    file_content = extract_text(file)
    if not file_content:
        st.error(f"Failed to extract text from {file.name}")
        return None

    # Prepare API request using secrets
    headers = {
        "Authorization": f"Bearer {st.secrets['API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": st.secrets['MODEL'],
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "file_name": file.name,
                "file_content": file_content
            }
        ],
        "temperature": 0.7,
        "max_tokens": 8000
    }

    try:
        with st.spinner(f"Sending {file.name} to API..."):
            response = requests.post(
                st.secrets['API_URL'],
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            print(response.json())
            return {
                "filename": file.name,
                "content": result['choices'][0]['message']['content'],
                "usage": result['usage'],
                "status": "success"
            }
            
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            st.error(f"API response: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Error processing {file.name}: {str(e)}")
        return None

def mock_analysis(selected_files):
    """Mock analysis function that generates random results"""
    # Generate some random findings based on the number of files
    num_files = len(selected_files)
    
    findings = [
        f"Found {random.randint(1, 5)} compliance issues across documents",
        f"Identified {random.randint(2, 8)} key regulations",
        f"Detected {random.randint(0, 3)} potential violations"
    ]
    
    # Generate some random recommendations
    recommendations = [
        "Review transaction thresholds for compliance",
        "Verify customer identification procedures",
        "Update internal policies to reflect recent regulatory changes",
        "Conduct additional employee training on AML regulations",
        "Implement enhanced due diligence for high-risk clients"
    ]
    
    # Select a random subset of recommendations
    num_recs = min(random.randint(1, 3), len(recommendations))
    selected_recommendations = random.sample(recommendations, num_recs)
    
    return {
        "files_analyzed": selected_files,
        "findings": findings,
        "recommendations": selected_recommendations,
        "compliance_score": f"{random.randint(60, 95)}%",
        "risk_level": random.choice(["Low", "Medium", "High"])
    }

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
                # Only show view button if file has been processed
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
        result = st.session_state.generated_results[st.session_state.viewing_file]
        st.markdown(f"### {st.session_state.viewing_file}")
        st.markdown(result['content'])
        
        # Download button
        st.download_button(
            label="⬇️ Download Results",
            data=result['content'],
            file_name=f"rules_{st.session_state.viewing_file}.txt",
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
        else:
            with st.spinner("Analyzing files..."):
                # Call the mock analysis function
                analysis_result = mock_analysis(st.session_state.selected_files)
                
                st.session_state.analysis_result = analysis_result
                st.success("Analysis complete!")
                
                # Display results in a nicer format
                st.subheader("Analysis Results")
                st.write(f"**Files Analyzed:** {', '.join(analysis_result['files_analyzed'])}")
                st.write(f"**Compliance Score:** {analysis_result['compliance_score']}")
                st.write(f"**Risk Level:** {analysis_result['risk_level']}")
                
                st.subheader("Key Findings")
                for finding in analysis_result['findings']:
                    st.write(f"- {finding}")
                
                st.subheader("Recommendations")
                for rec in analysis_result['recommendations']:
                    st.write(f"- {rec}")

# Run the app
if __name__ == "__main__":
    home_page()