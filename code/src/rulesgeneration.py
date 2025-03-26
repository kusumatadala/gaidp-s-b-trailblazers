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
from util  import *

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
