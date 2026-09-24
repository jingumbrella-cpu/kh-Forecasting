import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_tab_eda(df_current):
    st.header("១. ការវិភាគ EDA និងក្រាហ្វសំខាន់ៗ")
    
    m1, m2, m3, m4 = st.columns(4)
    latest_year = int(df_current['fiscal_year'].max())
    latest_amount = df_current[df_current['fiscal_year'] == latest_year]['implement_amount'].values[0]
    avg_growth = df_current['yoy_growth_percent'].mean()
    covid_2020_drop = df_current[df_current['fiscal_year'] == 2020]['yoy_growth_percent'].values[0]
    
    m1.metric("ចំណូលឆ្នាំចុងក្រោយ (2024)", f"{latest_amount:,.0f} លានរៀល")
    m2.metric("កំណើនមធ្យម (YoY Avg)", f"{avg_growth:.2f}%")
    m3.metric("ការធ្លាក់ចុះឆ្នាំកូវីដ (2020)", f"{covid_2020_drop:.2f}%", delta_color="inverse")
    m4.metric("ចំនួនឆ្នាំទិន្នន័យ", f"{len(df_current)} ឆ្នាំ")

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. 📈 Actual Current Revenue (2005–2024)")
        fig1 = px.line(df_current, x='fiscal_year', y='implement_amount', markers=True)
        fig1.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("2. 📊 Budget vs Actual Revenue")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_current['fiscal_year'], y=df_current['budget_law_amount'], name='ច្បាប់ថវិកា', marker_color='#abc9e9'))
        fig2.add_trace(go.Bar(x=df_current['fiscal_year'], y=df_current['implement_amount'], name='អនុវត្តជាក់ស្តែង', marker_color='#005b96'))
        fig2.update_layout(barmode='group')
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("3. 📉 Year-over-Year Growth (%)")
        colors = ['red' if x < 0 else 'green' for x in df_current['yoy_growth_percent'].fillna(0)]
        fig3 = go.Figure(go.Bar(x=df_current['fiscal_year'], y=df_current['yoy_growth_percent'], marker_color=colors))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("4. 🔍 Trend + 2020 Anomaly")
        fig4 = px.line(df_current, x='fiscal_year', y='implement_amount', markers=True)
        val_2020 = df_current[df_current['fiscal_year'] == 2020]['implement_amount'].values[0]
        fig4.add_annotation(x=2020, y=val_2020, text="⚠️ COVID-19 Drop (-15.65%)", showarrow=True, arrowhead=2, arrowcolor="red")
        st.plotly_chart(fig4, use_container_width=True)