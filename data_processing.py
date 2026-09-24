import pandas as pd

def clean_and_prepare_data(uploaded_file):
    """សម្អាត និងរៀបចំទិន្នន័យពី CSV Upload"""
    raw_df = pd.read_csv(uploaded_file)
    df = raw_df.copy()
    
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
        
    df['fiscal_year'] = pd.to_numeric(df['fiscal_year'], errors='coerce').astype('Int64')
    numeric_cols = ['budget_law_amount', 'implement_amount', 'deficit_surplus']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.drop_duplicates()
    
    # Filter Current Revenue
    df_current = df[df['main_revenue_indicator_en'] == 'Current Revenue'].sort_values('fiscal_year').reset_index(drop=True)
    df_current['yoy_growth_percent'] = (df_current['implement_amount'].pct_change() * 100).round(2)
    
    return df_current