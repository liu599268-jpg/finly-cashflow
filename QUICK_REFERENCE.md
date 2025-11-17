# Finly Hybrid Forecasting - Quick Reference

**Fast reference for using the hybrid forecasting engine**

---

## 🚀 Quick Commands

### Run the Demo
```bash
cd /Users/lhr/Desktop/Finly-prototype
python hybrid_forecasting_demo.py
```

### Run Validation Tests
```bash
python test_hybrid_realistic.py
```

### Generate Sample Data
```bash
python generate_sample_data.py
```

---

## 💻 Code Examples

### Basic Usage - Single Category
```python
from src.forecasting.ml_models import HybridEnsembleForecaster
import pandas as pd

# Load data
df = pd.read_csv('data/transactions.csv')

# Initialize
ensemble = HybridEnsembleForecaster()

# Fit and forecast
ensemble.fit_category(df, 'revenue', frequency='W')
forecast = ensemble.forecast_category('revenue', steps=13)

# Results
print(f"Week 1: ${forecast['forecast'][0]:,.2f}")
print(f"Week 13: ${forecast['forecast'][12]:,.2f}")
print(f"Models: {forecast['models_used']}")
print(f"Weights: {forecast['weights']}")
```

### Multi-Category Forecasting
```python
ensemble = HybridEnsembleForecaster()

# Fit all categories
categories = ['revenue', 'payroll', 'cogs', 'marketing']
ensemble.fit_all_categories(df, categories, frequency='W')

# Forecast all
forecasts = ensemble.forecast_all_categories(steps=13)

for category, result in forecasts.items():
    print(f"{category}: ${result['forecast'][0]:,.2f}")
```

### Custom Model Configuration
```python
# Enable only specific models
ensemble = HybridEnsembleForecaster(
    enable_arima=True,
    enable_regression=True,
    enable_xgboost=False  # Disable XGBoost
)

# Custom weights
ensemble = HybridEnsembleForecaster(
    weights={
        'arima': 0.5,      # 50%
        'regression': 0.3, # 30%
        'xgboost': 0.2     # 20%
    }
)
```

### Individual Models
```python
# ARIMA only
from src.forecasting.ml_models import CategoryARIMAForecaster

arima = CategoryARIMAForecaster()
arima.fit_category(df, 'revenue')
forecast = arima.forecast_category('revenue', steps=13)

# Regression only
from src.forecasting.ml_models import MultiCategoryRegressionForecaster

regression = MultiCategoryRegressionForecaster(model_type='ridge')
regression.fit_category(df, 'revenue')
forecast = regression.forecast_category('revenue', steps=13)

# XGBoost only
from src.forecasting.ml_models import MultiCategoryXGBoostForecaster

xgboost = MultiCategoryXGBoostForecaster()
xgboost.fit_category(df, 'revenue')
forecast = xgboost.forecast_category('revenue', steps=13)
```

---

## 📊 Understanding Results

### Forecast Dictionary Structure
```python
forecast = {
    'forecast': [1000, 1050, 1100, ...],      # 13 predictions
    'lower_bound': [900, 940, 980, ...],      # Lower confidence
    'upper_bound': [1100, 1160, 1220, ...],   # Upper confidence
    'category': 'revenue',
    'model_type': 'Hybrid Ensemble',
    'weights': {                               # Model weights
        'arima': 0.615,
        'regression': 0.202,
        'xgboost': 0.183
    },
    'individual_forecasts': {                  # Each model's prediction
        'arima': [980, 1030, ...],
        'regression': [1020, 1070, ...],
        'xgboost': [995, 1045, ...]
    },
    'models_used': ['arima', 'regression', 'xgboost']
}
```

### Accuracy Metrics
```python
# MAE (Mean Absolute Error)
# Average dollar difference
# Lower is better
# Example: MAE of $5,000 = off by $5K on average

# MAPE (Mean Absolute Percentage Error)
# Average percentage error
# Lower is better
# < 15% = Excellent
# 15-25% = Good
# 25-35% = Acceptable
# > 35% = Poor

# RMSE (Root Mean Square Error)
# Penalizes large errors
# Lower is better
# RMSE > MAE indicates some large errors
```

---

## 🎯 Model Selection Guide

| Business Pattern | Best Model | Reason |
|-----------------|-----------|--------|
| Regular subscriptions | ARIMA | Handles periodic patterns |
| Seasonal sales | Hybrid | Combines seasonality + trends |
| Growing startup | Regression | Captures growth |
| Project-based | ARIMA | Handles irregular revenue |
| E-commerce | Hybrid | Seasonal + marketing effects |
| Consulting | ARIMA | Lumpy, irregular patterns |

---

## 🔧 Troubleshooting

### "Input contains infinity"
**Problem:** Sparse data causes inf/NaN in features

**Solution:** Use ARIMA only
```python
ensemble = HybridEnsembleForecaster(
    enable_arima=True,
    enable_regression=False,
    enable_xgboost=False
)
```

### "Model must be fitted"
**Problem:** Forgot to fit before forecasting

**Solution:** Always fit first
```python
ensemble.fit_category(df, 'revenue')  # Fit first
forecast = ensemble.forecast_category('revenue', 13)  # Then forecast
```

### Poor Accuracy
**Possible Causes:**
- Not enough data (< 26 weeks)
- Irregular patterns
- Data quality issues

**Solutions:**
- Collect more historical data
- Use ARIMA for irregular patterns
- Clean and validate data first

---

## 📁 File Locations

### Implementation
```
src/forecasting/ml_models/
├── arima_model.py           # ARIMA forecaster
├── regression_model.py      # Regression forecaster
├── xgboost_model.py         # XGBoost forecaster
└── hybrid_ensemble.py       # Hybrid ensemble
```

### Tests & Demos
```
test_hybrid_realistic.py          # Validation tests
hybrid_forecasting_demo.py        # Interactive demo
generate_sample_data.py           # Sample data generator
```

### Documentation
```
docs/HYBRID_FORECASTING.md        # Complete guide
HYBRID_FORECASTING_SUMMARY.md     # Implementation summary
QUICK_REFERENCE.md                # This file
```

### Data
```
data/
├── transactions.csv              # Sample data (52 weeks)
├── ecommerce_test_data.csv       # E-commerce test
└── consulting_test_data.csv      # Consulting test
```

---

## 📚 More Information

- **Complete Guide:** `docs/HYBRID_FORECASTING.md`
- **Project Setup:** `QUICKSTART.md`
- **QuickBooks Integration:** `docs/QUICKBOOKS_INTEGRATION.md`
- **Testing Report:** `TEST_REPORT.md`

---

## 🎓 Key Concepts

### ARIMA
- Time series analysis
- Captures seasonality
- Best for regular patterns
- Requires 10+ data points

### Regression
- Feature-based modeling
- Linear trends
- 40+ engineered features
- Best for predictable growth

### XGBoost
- Machine learning
- Non-linear patterns
- Feature importance
- Best with large datasets

### Hybrid Ensemble
- Combines all three models
- Weighted averaging
- Adaptive weights (performance-based)
- Best overall accuracy

---

**Last Updated:** November 17, 2025
**Version:** 1.0
