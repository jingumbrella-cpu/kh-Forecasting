import streamlit as st

def render_tab_dataset(df_current):
    st.header("៣. ទិន្នន័យដែលបានសម្អាតរួច")
    st.dataframe(df_current[['fiscal_year', 'implement_amount', 'yoy_growth_percent']], use_container_width=True)