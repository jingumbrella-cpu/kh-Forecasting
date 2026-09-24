import io
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt

def generate_pdf_report(df_current, metrics_df, selected_model, report_df, fig_plotly):
    """
    បង្កើត PDF Executive Summary Report
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    # Define Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#003366"),
        spaceAfter=12,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor("#005b96"),
        spaceBefore=10,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leading=14
    )

    # 1. Header & Title
    story.append(Paragraph("<b>EXECUTIVE SUMMARY: NATIONAL REVENUE FORECAST</b>", title_style))
    story.append(Paragraph("<b>National Level Revenue Collection & Time Series Forecasting Report</b>", body_style))
    story.append(Spacer(1, 10))

    # 2. Key Metrics Summary (KPI Table)
    story.append(Paragraph("1. Key Metrics & Historical Summary", subtitle_style))
    
    latest_year = int(df_current['fiscal_year'].max())
    latest_amount = df_current[df_current['fiscal_year'] == latest_year]['implement_amount'].values[0]
    avg_growth = df_current['yoy_growth_percent'].mean()
    covid_drop = df_current[df_current['fiscal_year'] == 2020]['yoy_growth_percent'].values[0]

    kpi_data = [
        ["Metric Name", "Value"],
        ["Latest Historical Year", f"{latest_year}"],
        ["Latest Actual Revenue (2024)", f"{latest_amount:,.2f} Million KHR"],
        ["Average Historical YoY Growth", f"{avg_growth:.2f}%"],
        ["2020 COVID-19 Anomaly Drop", f"{covid_drop:.2f}%"],
        ["Selected Forecasting Model", f"{selected_model}"]
    ]

    kpi_table = Table(kpi_data, colWidths=[240, 260])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # 3. Export Plotly Chart as Image for PDF
    story.append(Paragraph("2. History vs Forecast Plot", subtitle_style))
    
    # Render Matplotlib figure for PDF rendering
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(df_current['fiscal_year'], df_current['implement_amount'], label='Historical Actual', color='#1f77b4', marker='o')
    ax.plot(report_df['Fiscal Year'], report_df['Forecasted Amount (លានរៀល)'], label='Forecast', color='green', marker='s', linestyle='--')
    ax.fill_between(
        report_df['Fiscal Year'], 
        report_df['Lower Bound (80%)'], 
        report_df['Upper Bound (80%)'], 
        color='green', alpha=0.15, label='80% Confidence Interval'
    )
    ax.set_title("Current Revenue: Historical vs Forecast")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Million KHR")
    ax.legend(fontsize=8)
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=200)
    img_buf.seek(0)
    plt.close(fig)

    story.append(Image(img_buf, width=500, height=210))
    story.append(Spacer(1, 10))

    # 4. Forecast Data Table
    story.append(Paragraph("3. 5-Year Forecast Details", subtitle_style))
    
    table_data = [["Fiscal Year", "Forecast (Million KHR)", "Lower Bound (80%)", "Upper Bound (80%)"]]
    for _, row in report_df.iterrows():
        table_data.append([
            str(int(row['Fiscal Year'])),
            f"{row['Forecasted Amount (លានរៀល)']:,.2f}",
            f"{row['Lower Bound (80%)']:,.2f}",
            f"{row['Upper Bound (80%)']:,.2f}"
        ])

    forecast_table = Table(table_data, colWidths=[100, 140, 130, 130])
    forecast_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#005b96")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(forecast_table)
    story.append(Spacer(1, 12))

    # 5. Executive Insights & Recommendations
    story.append(Paragraph("4. Executive Insights & Recommendations", subtitle_style))
    insights_text = f"""
    • <b>Model Performance:</b> The selected model <i>{selected_model}</i> demonstrated superior historical accuracy during testing.<br/>
    • <b>Growth Trend:</b> Projected revenues show a stable positive trajectory over the next 5 years.<br/>
    • <b>Risk Management:</b> Fiscal policy makers should consider the 80% confidence lower boundary when setting conservative budget baselines to cushion against potential economic shocks.
    """
    story.append(Paragraph(insights_text, body_style))

    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()