import streamlit as st
import streamlit_authenticator as stauth

from data_processing import clean_and_prepare_data
from components.sidebar import render_sidebar
from components.tab_eda import render_tab_eda
from components.tab_timeseries import render_tab_timeseries
from components.tab_dataset import render_tab_dataset
from components.tab_forecasting import render_tab_forecasting
from components.tab_stresstest import render_tab_stresstest

st.set_page_config(page_title="Revenue Forecasting Dashboard", layout="wide")

# ==========================================
# AUTHENTICATION SETUP (Fixed for New Version)
# ==========================================
import streamlit as st
import streamlit_authenticator as stauth

# ==========================================
# AUTHENTICATION SETUP (Fixed for v0.3.x)
# ==========================================
credentials = {
    "usernames": {
        "admin": {
            "name": "Executive User",
            "password": stauth.Hasher.hash("admin123")  # ប្រើ .hash() ជំនួស .hash_password()
        },
        "analyst": {
            "name": "Data Analyst",
            "password": stauth.Hasher.hash("analyst123") # ប្រើ .hash() ជំនួស .hash_password()
        }
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="revenue_dashboard_cookie",
    key="auth_signature_key",
    cookie_expiry_days=30
)
# Render Login Widget
try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state.get("authentication_status") == False:
    st.error("❌ Username ឬ Password មិនត្រឹមត្រូវទេ!")
elif st.session_state.get("authentication_status") == None:
    st.warning("🔒 សូមបញ្ចូល Username និង Password ដើម្បីចូលប្រព័ន្ធ")
elif st.session_state.get("authentication_status"):

    # ------------------------------------------
    # MAIN APPLICATION (RUN WHEN LOGGED IN)
    # ------------------------------------------
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f"👋 ស្វាគមន៍, **{st.session_state.get('name')}**")

    st.title("📊 National Revenue EDA & Forecasting Dashboard")
    st.markdown("ប្រព័ន្ធសម្អាតទិន្នន័យ វិភាគ Time Series និងព្យាករណ៍ចំណូលចរន្តថវិការដ្ឋ")

    uploaded_file = render_sidebar()

    if uploaded_file is not None:
        df_current = clean_and_prepare_data(uploaded_file)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 EDA & Visualizations", 
            "📈 Time-Series Analysis", 
            "🎯 Clean Dataset", 
            "🎯 Model Forecasting & Prediction",
            "📊 Stress Testing & Risk Analysis"
        ])
        # 2. រៀបចំ Variables ចាំបាច់សម្រាប់ Forecasting និង Stress Testing
        train_data = df_current[df_current['fiscal_year'] <= 2020].set_index('fiscal_year')['implement_amount']
        test_data = df_current[df_current['fiscal_year'] > 2020].set_index('fiscal_year')['implement_amount']
        full_data = df_current.set_index('fiscal_year')['implement_amount']

        # Evaluate Models ដើម្បីទទួលបាន preds_dict
        from models import evaluate_models
        metrics_df, best_model_name, preds_dict = evaluate_models(train_data, test_data)
        with tab1:
            render_tab_eda(df_current)

        with tab2:
            render_tab_timeseries(df_current)

        with tab3:
            render_tab_dataset(df_current)

        with tab4:
            render_tab_forecasting(df_current)
        with tab5:
            # ផ្ញើ Parameters ទាំង ៥ ឱ្យគ្រប់គ្រាន់
            selected_model = best_model_name  # ប្រើ Best Model ជា Default
            horizon = 5                       # ប្រើ Horizon 5 ឆ្នាំជា Default
            render_tab_stresstest(df_current, full_data, preds_dict, selected_model, horizon)
    else:
        st.info("👋 សូម Upload ឯកសារ CSV នៅ Sidebar ខាងឆ្វេង ដើម្បីចាប់ផ្តើមវិភាគ EDA និង Forecast!")