import streamlit as st
import pandas as pd

def render_sidebar():
    st.sidebar.title("📌 ណែនាំអំពីការប្រើប្រាស់")
    with st.sidebar.expander("ℹ️ លក្ខខណ្ឌនៃ File ត្រូវ Upload", expanded=True):
        st.markdown("""
        **ទម្រង់ឯកសារ (Format):**
        * ត្រូវតែជា File **CSV (.csv)**
        
        **ជួរឈរចាំបាច់ (Required Columns):**
        1. `fiscal_year`: ឆ្នាំថវិកា
        2. `main_revenue_indicator_en`: ត្រូវមានតម្លៃ `Current Revenue`
        3. `budget_law_amount`: ច្បាប់ថវិកា
        4. `implement_amount`: អនុវត្តជាក់ស្តែង
        """)

    sample_data = pd.DataFrame({
        'fiscal_year': [2022, 2023, 2024],
        'main_revenue_indicator_en': ['Current Revenue', 'Current Revenue', 'Current Revenue'],
        'budget_law_amount': [23000000, 25000000, 28000000],
        'implement_amount': [24860865, 24641415, 25717812]
    })
    
    st.sidebar.download_button(
        label="📄 ទាញយកគំរូ CSV Template",
        data=sample_data.to_csv(index=False).encode('utf-8'),
        file_name="sample_revenue_template.csv",
        mime="text/csv"
    )

    st.sidebar.header("📁 Upload Dataset")
    return st.sidebar.file_uploader("ជ្រើសរើសឯកសារ CSV", type=["csv"])