import streamlit as st
from homepage import home_page
from dashboard import dashboard_page
from chatbot import chatbot_interface
from initdeepseekapi import intialise

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

# DeepSeek API Configuration
DEEPSEEK_API_KEY = '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'
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def main(deepseek):
    if "page" not in st.session_state:
        st.session_state["page"] = "home"
    
    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "dashboard":
        dashboard_page(ds)
    # chatbot_interface()


if __name__ == "__main__":
    ds=intialise()
    main(ds)
