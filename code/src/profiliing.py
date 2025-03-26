import streamlit as st
import requests
import json
from io import BytesIO
import PyPDF2
from docx import Document
from typing import Optional, Dict, Any

def extract_text(file_obj):
    """Extract text from PDF, DOCX, or plain text files"""
    try:
        content = file_obj.read()
        
        if file_obj.name.lower().endswith('.pdf'):
            pdf = PyPDF2.PdfReader(BytesIO(content))
            return "\n".join([page.extract_text() for page in pdf.pages])
        elif file_obj.name.lower().endswith('.docx'):
            doc = Document(BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            # Try UTF-8 first, then fallback to latin-1
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('latin-1')
    except Exception as e:
        st.error(f"Error reading {file_obj.name}: {str(e)}")
        return None

def profile(
    selected_files: list,
    transaction_file
) -> Optional[Dict[str, Any]]:
    """
    Send transaction data and selected rules to DeepSeek API
    
    Args:
        selected_files: List of selected document names
        transaction_file: Uploaded CSV file object
        
    Returns:
        dict: API response JSON or None if failed
    """
    try:
        # 1. Read the prompt
        with open("profiling_prompt.txt", "r", encoding='utf-8') as f:
            prompt = f.read().strip()
        with open("system_prompt.txt", "r", encoding='utf-8') as f:
            systemPrompt = f.read().strip()
        
        # 2. Process transaction data
        transaction_file.seek(0)
        transaction_content = extract_text(transaction_file)
        if not transaction_content:
            raise ValueError("Failed to read transaction file")
        
        # 3. Process selected rules documents
        rules_content = []
        for filename in selected_files:
            if filename in st.session_state.uploaded_rules:
                file_obj = st.session_state.uploaded_rules[filename]['file']
                file_obj.seek(0)
                content = extract_text(file_obj)
                if content:
                    rules_content.append(f"=== {filename} ===\n{content}")
        
        # 4. Prepare API request
        payload = {
            "model": st.secrets["MODEL"],
            "messages": [{
                "role":"system",
                "content":systemPrompt
            },
                {
                "role": "user",
                "content": f"{prompt}\n\nTRANSACTION DATA:\n{transaction_content}\n\nRULES DOCUMENTS:\n" + 
                          "\n\n".join(rules_content),
                "file_name": transaction_file.name,
                "file_content": transaction_content
            }],
            "temperature": 0.7,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"}
        }
        
        # 5. Send request
        response = requests.post(
            st.secrets["API_URL"],
            headers={
                "Authorization": f"Bearer {st.secrets['API_KEY']}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        api_response=response.json()
        print(api_response)
        return api_response
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None