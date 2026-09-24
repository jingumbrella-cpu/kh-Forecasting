import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.stattools import adfuller

def render_tab_timeseries(df_current):
    st.header("២. Time-Series Analysis")
    
    train_df = df_current[df_current['fiscal_year'] <= 2020]
    test_df = df_current[df_current['fiscal_year'] > 2020]
    
    col1, col2 = st.columns(2)
    col1.info(f"**Train Set (2005-2020):** {len(train_df)} ឆ្នាំ")
    col2.warning(f"**Test Set (2021-2024):** {len(test_df)} ឆ្នាំ")

    fig_split = go.Figure()
    fig_split.add_trace(go.Scatter(x=train_df['fiscal_year'], y=train_df['implement_amount'], mode='lines+markers', name='Train Set'))
    fig_split.add_trace(go.Scatter(x=test_df['fiscal_year'], y=test_df['implement_amount'], mode='lines+markers', name='Test Set'))
    fig_split.update_layout(title="Train/Test Split Visualization (80% / 20%)")
    st.plotly_chart(fig_split, use_container_width=True)

    st.subheader("Stationarity Test (ADF Test)")
    ts_data = df_current['implement_amount'].dropna()
    adf_res = adfuller(ts_data)
    st.write(f"**ADF Statistic:** `{adf_res[0]:.4f}` | **p-value:** `{adf_res[1]:.4f}`")