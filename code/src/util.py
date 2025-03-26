import streamlit as st
import PyPDF2
from docx import Document
from io import BytesIO
import pandas as pd
import time
import json
import os

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