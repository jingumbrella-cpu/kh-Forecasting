import streamlit as st
import plotly.graph_objects as go
from models import run_future_forecast, run_stress_test

def render_tab_stresstest(df_current, full_data, preds_dict, selected_model, horizon):
    st.header("📊 Macroeconomic Stress Testing & Risk Analysis")
    st.markdown("ធ្វើការតេស្តល្បងមើលផលប៉ះពាល់នៃកត្តាសេដ្ឋកិច្ចម៉ាក្រូទៅលើការព្យាករណ៍ចំណូលចរន្ត")

    # 1. Stress Testing Controls
    st.subheader("🎛️ កំណត់ Macroeconomic Shock Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        gdp_shock = st.slider("📈 កំណើន/ថយចុះ GDP Shock (%)", min_value=-5.0, max_value=5.0, value=0.0, step=0.5)
    with col2:
        inflation_shock = st.slider("💸 កើនឡើងនៃអតិផរណា Inflation (%)", min_value=0.0, max_value=10.0, value=0.0, step=0.5)
    with col3:
        fx_shock = st.slider("🔱 ការប្រែប្រួលអត្រាប្តូរប្រាក់ FX Rate (%)", min_value=-10.0, max_value=10.0, value=0.0, step=1.0)

    # 2. Compute Baseline & Stressed Forecast
    future_years, future_pred, lower_bounds, upper_bounds, _ = run_future_forecast(
        full_data, selected_model, horizon, preds_dict
    )
    
    stressed_pred, net_impact = run_stress_test(future_pred.values, inflation_shock, gdp_shock, fx_shock)

    # Status Banner
    if net_impact < 0:
        st.error(f"⚠️ **Pessimistic Stress Level:** ផលប៉ះពាល់សរុបធ្វើឱ្យចំណូលធ្លាក់ចុះមធ្យម **{abs(net_impact):.2f}%** ធៀបនឹង Baseline")
    elif net_impact > 0:
        st.success(f"🚀 **Optimistic Stress Level:** ផលប៉ះពាល់សរុបធ្វើឱ្យចំណូលកើនឡើងមធ្យម **{net_impact:.2f}%** ធៀបនឹង Baseline")
    else:
        st.info("ℹ️ **Baseline Level:** គ្មានការផ្លាស់ប្តូរកត្តាសេដ្ឋកិច្ចម៉ាក្រូទេ")

    # 3. Interactive Plot (Baseline vs Stressed)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=future_years, y=future_pred.values, mode='lines+markers', name='Baseline Forecast', line=dict(color='green', width=3)))
    fig.add_trace(go.Scatter(x=future_years, y=stressed_pred, mode='lines+markers', name='Stressed Forecast Scenario', line=dict(color='red', width=3, dash='dash')))
    fig.update_layout(title="ការប្រៀបធៀប Baseline Forecast និង Stressed Scenario", xaxis_title="ឆ្នាំ", yaxis_title="ចំណូលចរន្ត (លានរៀល)")
    st.plotly_chart(fig, use_container_width=True)