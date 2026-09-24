import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.graph_objects as go
from models import evaluate_models, run_future_forecast
from pdf_generator import generate_pdf_report
from telegram_bot import send_telegram_alert  # Import Telegram Module ថ្មី

def render_tab_forecasting(df_current):
    st.header("🎯 ៤. Model Forecasting & Scenario Analysis")
    
    train_data = df_current[df_current['fiscal_year'] <= 2020].set_index('fiscal_year')['implement_amount']
    test_data = df_current[df_current['fiscal_year'] > 2020].set_index('fiscal_year')['implement_amount']
    full_data = df_current.set_index('fiscal_year')['implement_amount']
    test_years = test_data.index.tolist()

    # 1. Auto Model Evaluation
    metrics_df, best_model_name, preds_dict = evaluate_models(train_data, test_data)

    st.success(f"🏆 **Recommended Model (Auto-Selected):** `{best_model_name}` (មានអត្រាកំហុស MAPE ទាបបំផុតត្រឹម **{metrics_df.iloc[0]['MAPE (%)']}%** លើ Test Period)")

    st.subheader("📊 តារាងប្រៀបធៀបសមត្ថភាព Models (Evaluation Period 2021-2024)")
    st.dataframe(metrics_df, use_container_width=True)
    st.markdown("---")

    # Interactive Controls
    st.subheader("🎛️ ការកំណត់ការព្យាករណ៍ និង What-If Scenario Analysis")
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
    
    model_list = metrics_df["Model Name"].tolist()
    default_idx = model_list.index(best_model_name)
    
    with ctrl_col1:
        selected_model = st.selectbox("1. ជ្រើសរើសម៉ូឌែល (Model Selector):", model_list, index=default_idx)
        
    with ctrl_col2:
        horizon = st.slider("2. ចំនួនឆ្នាំព្យាករណ៍ទៅមុខ (Horizon):", min_value=1, max_value=5, value=5)

    with ctrl_col3:
        growth_adj = st.slider("3. What-If Growth Adjustment (%):", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)

    # Forecast Logic Execution
    future_years, future_pred, lower_bounds, upper_bounds, test_model_pred = run_future_forecast(
        full_data, selected_model, horizon, preds_dict, growth_adjustment=growth_adj
    )

    # Interactive Plot
    st.subheader(f"📈 ក្រាហ្វព្យាករណ៍ចំណូលចរន្ត ({selected_model})")
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=full_data.index, y=full_data.values, mode='lines+markers', name='Past Actual Revenue (2005-2024)', line=dict(color='#1f77b4', width=3)))
    fig_forecast.add_trace(go.Scatter(x=test_years, y=test_model_pred, mode='lines+markers', name='Test Prediction (2021-2024)', line=dict(color='orange', width=2, dash='dash')))
    fig_forecast.add_trace(go.Scatter(x=future_years, y=future_pred.values, mode='lines+markers', name=f'Future Forecast ({future_years[0]}-{future_years[-1]})', line=dict(color='green', width=3)))
    fig_forecast.add_trace(go.Scatter(
        x=future_years + future_years[::-1],
        y=list(upper_bounds.values) + list(lower_bounds.values)[::-1],
        fill='toself', fillcolor='rgba(0, 128, 0, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        name='80% Confidence Interval'
    ))
    fig_forecast.update_layout(xaxis_title="ឆ្នាំ (Fiscal Year)", yaxis_title="ចំណូលចរន្ត (លានរៀល)")
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Executive Summary Report & Download
    st.subheader("📋 របាយការណ៍ព្យាករណ៍ និងទាញយកទិន្នន័យ (Executive Summary)")
    
    report_df = pd.DataFrame({
        "Fiscal Year": future_years,
        "Forecasted Amount (លានរៀល)": np.round(future_pred.values, 2),
        "Lower Bound (80%)": np.round(lower_bounds.values, 2),
        "Upper Bound (80%)": np.round(upper_bounds.values, 2)
    })
    st.dataframe(report_df, use_container_width=True)

    # 1. Download Excel & PDF Buttons
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            report_df.to_excel(writer, sheet_name='Future Forecast', index=False)
            metrics_df.to_excel(writer, sheet_name='Model Performance Evaluation', index=False)
        
        st.download_button(
            label="📥 Download Executive Report (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"executive_revenue_forecast_{selected_model.replace(' ', '_').lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # PDF Generation
    pdf_bytes = generate_pdf_report(df_current, metrics_df, selected_model, report_df, fig_forecast)
    
    with btn_col2:
        st.download_button(
            label="📄 Download Executive PDF Report",
            data=pdf_bytes,
            file_name=f"executive_revenue_forecast_{selected_model.replace(' ', '_').lower()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("---")

    # =========================================================
    # TELEGRAM TRIGGER NOTIFICATION SECTION
    # =========================================================
    st.subheader("🔔 2. Automated Telegram Notification & Alert")
    st.markdown("ផ្ញើលទ្ធផលព្យាករណ៍សង្ខេប និងឯកសារ PDF ទៅកាន់ Telegram Group របស់ថ្នាក់ដឹកនាំដោយស្វ័យប្រវត្តិ")

    tg_col1, tg_col2 = st.columns(2)
    with tg_col1:
        bot_token = st.text_input("Telegram Bot Token:", type="password", placeholder="ឧទាហរណ៍៖ 123456789:ABCdefGhIJK...", help="Bot Token ទទួលបានពី @BotFather")
    with tg_col2:
        chat_id = st.text_input("Telegram Chat ID / Group ID:", placeholder="ឧទាហរណ៍៖ -100123456789", help="ID របស់ Telegram Group ឬ User")

    if st.button("📤 ផ្ញើរបាយការណ៍ទៅកាន់ Telegram", type="primary"):
        if not bot_token or not chat_id:
            st.warning("⚠️ សូមបញ្ចូល Telegram Bot Token និង Chat ID ឱ្យបានត្រឹមត្រូវជាមុនសិន!")
        else:
            latest_amount = df_current[df_current['fiscal_year'] == int(df_current['fiscal_year'].max())]['implement_amount'].values[0]
            
            # បង្កើតអត្ថបទសារសង្ខេបជា HTML Format
            alert_msg = f"""
<b>📊 NATIONAL REVENUE FORECAST REPORT</b>
----------------------------------------
• <b> Selected Model:</b> {selected_model}
• <b> Latest Historical (2024):</b> {latest_amount:,.0f} លានរៀល
• <b> Forecast ({future_years[0]}):</b> {future_pred.iloc[0]:,.0f} លានរៀល
• <b> Forecast ({future_years[-1]}):</b> {future_pred.iloc[-1]:,.0f} លានរៀល
• <b> Status:</b> Successfully Generated via Dashboard.
----------------------------------------
<i>📄 ឯកសារ PDF លម្អិតត្រូវបានទាញទម្លាក់ក្នុង Group នេះស្រាប់។</i>
            """
            
            with st.spinner("កំពុងផ្ញើរបាយការណ៍ទៅកាន់ Telegram..."):
                success = send_telegram_alert(bot_token, chat_id, alert_msg, pdf_bytes)
                if success:
                    st.success("✅ បានផ្ញើរបាយការណ៍ និងឯកសារ PDF ទៅកាន់ Telegram រួចរាល់!")
                else:
                    st.error("❌ មិនអាចផ្ញើសារបានទេ! សូមពិនិត្យ Bot Token, Chat ID ឬការតភ្ជាប់ Internet។")