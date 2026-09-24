import numpy as np
import pandas as pd
from statsmodels.tsa.api import Holt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

def calc_metrics(y_true, y_pred):
    """គណនា MAPE និង RMSE"""
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return round(mape, 2), round(rmse, 2)

def create_covid_exog(years_index):
    """បង្កើត Dummy Variable សម្រាប់ឆ្នាំ 2020 (COVID-19 Intervention)"""
    return np.where(pd.Series(years_index) == 2020, 1, 0)

def evaluate_models(train_data, test_data):
    """វាយតម្លៃសមត្ថភាព Models ទាំងអស់លើ Test Period (2021-2024)"""
    train_years = train_data.index
    test_years = test_data.index
    
    # 1. Naive Drift
    drift_slope = (train_data.iloc[-1] - train_data.iloc[0]) / (len(train_data) - 1)
    naive_pred = [train_data.iloc[-1] + drift_slope * i for i in range(1, len(test_data) + 1)]
    
    # 2. Holt's Linear
    holt_fit = Holt(train_data.values, initialization_method="estimated").fit()
    holt_pred = holt_fit.forecast(len(test_data))
    
    # 3. ARIMA (1,1,0)
    arima_fit = ARIMA(train_data.values, order=(1, 1, 0)).fit()
    arima_pred = arima_fit.forecast(len(test_data))
    
    # 4. ARIMAX (1,1,0) - ជាមួយ COVID Dummy Variable
    exog_train = create_covid_exog(train_years)
    exog_test = create_covid_exog(test_years)
    arimax_fit = ARIMA(train_data.values, exog=exog_train, order=(1, 1, 0)).fit()
    arimax_pred = arimax_fit.forecast(len(test_data), exog=exog_test.reshape(-1, 1))

    # គណនា Metrics
    naive_mape, naive_rmse = calc_metrics(test_data, naive_pred)
    holt_mape, holt_rmse = calc_metrics(test_data, holt_pred)
    arima_mape, arima_rmse = calc_metrics(test_data, arima_pred)
    arimax_mape, arimax_rmse = calc_metrics(test_data, arimax_pred)
    
    metrics_df = pd.DataFrame({
        "Model Name": ["ARIMAX (1,1,0) + COVID Dummy", "ARIMA (1,1,0)", "Holt's Linear Smoothing", "Naive Drift (Baseline)"],
        "MAPE (%)": [arimax_mape, arima_mape, holt_mape, naive_mape],
        "RMSE (លានរៀល)": [arimax_rmse, arima_rmse, holt_rmse, naive_rmse]
    }).sort_values(by="MAPE (%)").reset_index(drop=True)
    
    # រក Best Model (MAPE ទាបជាងគេ)
    best_model_name = metrics_df.iloc[0]["Model Name"]
    
    preds_dict = {
        "ARIMAX (1,1,0) + COVID Dummy": arimax_pred,
        "ARIMA (1,1,0)": arima_pred,
        "Holt's Linear Smoothing": holt_pred,
        "Naive Drift (Baseline)": naive_pred
    }
    
    return metrics_df, best_model_name, preds_dict

def run_future_forecast(full_data, selected_model, horizon, preds_dict, growth_adjustment=0.0):
    """គណនា Forecast ទៅអនាគត + What-If Scenario Growth Adjustment"""
    last_year = int(full_data.index.max())
    future_years = list(range(last_year + 1, last_year + horizon + 1))
    
    exog_full = create_covid_exog(full_data.index)
    exog_future = np.zeros(horizon) # ឆ្នាំទៅអនាគតគ្មាន COVID ទេ (0)
    
    if selected_model == "ARIMAX (1,1,0) + COVID Dummy":
        model_full = ARIMA(full_data.values, exog=exog_full, order=(1, 1, 0)).fit()
        forecast_res = model_full.get_forecast(steps=horizon, exog=exog_future.reshape(-1, 1))
        future_pred_base = forecast_res.predicted_mean
        conf_int = forecast_res.conf_int(alpha=0.20)
        lower_bounds = conf_int[:, 0]
        upper_bounds = conf_int[:, 1]

    elif selected_model == "ARIMA (1,1,0)":
        model_full = ARIMA(full_data.values, order=(1, 1, 0)).fit()
        forecast_res = model_full.get_forecast(steps=horizon)
        future_pred_base = forecast_res.predicted_mean
        conf_int = forecast_res.conf_int(alpha=0.20)
        lower_bounds = conf_int[:, 0]
        upper_bounds = conf_int[:, 1]

    elif selected_model == "Holt's Linear Smoothing":
        model_full = Holt(full_data.values, initialization_method="estimated").fit()
        future_pred_base = model_full.forecast(horizon)
        residual_std = np.std(model_full.resid)
        lower_bounds = future_pred_base - (1.28 * residual_std)
        upper_bounds = future_pred_base + (1.28 * residual_std)

    else: # Naive Drift
        drift_full = (full_data.iloc[-1] - full_data.iloc[0]) / (len(full_data) - 1)
        future_pred_base = np.array([full_data.iloc[-1] + drift_full * i for i in range(1, horizon + 1)])
        std_diff = np.std(np.diff(full_data.values))
        lower_bounds = np.array([future_pred_base[i-1] - 1.28 * std_diff * np.sqrt(i) for i in range(1, horizon + 1)])
        upper_bounds = np.array([future_pred_base[i-1] + 1.28 * std_diff * np.sqrt(i) for i in range(1, horizon + 1)])

    # អនុវត្ត What-If Scenario Growth Adjustment (% Slider)
    adj_factor = np.array([(1 + growth_adjustment / 100) ** i for i in range(1, horizon + 1)])
    future_pred = pd.Series(future_pred_base * adj_factor, index=future_years)
    lower_bounds = pd.Series(lower_bounds * adj_factor, index=future_years)
    upper_bounds = pd.Series(upper_bounds * adj_factor, index=future_years)
    
    test_model_pred = preds_dict[selected_model]

    return future_years, future_pred, lower_bounds, upper_bounds, test_model_pred

def run_stress_test(base_forecast, inflation_shock=0.0, gdp_impact=0.0, exchange_rate_impact=0.0):
    """
    គណនាផលប៉ះពាល់នៃ Macroeconomic Shocks លើ Forecast Baseline
    - inflation_shock (%): ផលប៉ះពាល់ពីអតិផរណា
    - gdp_impact (%): កំណើន/ថយចុះនៃ GDP 
    - exchange_rate_impact (%): ការប្រែប្រួលអត្រាប្តូរប្រាក់
    """
    # គណនា Net Macro Impact (%) 
    net_shock_percent = (gdp_impact * 0.8) - (inflation_shock * 0.3) + (exchange_rate_impact * 0.2)
    
    # បង្កើត Shock Factor
    horizon = len(base_forecast)
    shock_factors = np.array([(1 + net_shock_percent / 100) ** i for i in range(1, horizon + 1)])
    
    stressed_forecast = base_forecast * shock_factors
    return stressed_forecast, net_shock_percent
