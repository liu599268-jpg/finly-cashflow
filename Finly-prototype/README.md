# Finly - AI-Powered Cash Flow Forecasting for SMBs

**Finly** is an intelligent cash flow forecasting application designed specifically for small and medium-sized businesses. It connects to QuickBooks, analyzes historical transaction data, and generates accurate 13-week cash flow forecasts using AI/ML models.

---

## 🎯 Core Features

### 1. 📊 QuickBooks Integration
- Automatic connection to QuickBooks Online
- Real-time transaction sync
- Historical data import
- Category mapping and normalization

### 2. 🤖 AI/ML Forecasting Engine
- 13-week cash flow predictions
- Multiple forecasting models (ARIMA, Prophet, XGBoost)
- Category-level granular forecasting
- Confidence intervals and accuracy metrics

### 3. 📈 Web Dashboard
- Interactive cash flow visualizations
- Real-time alerts and insights
- Scenario planning tools
- Executive summaries and reports

### 4. 💡 Smart Analytics
- Burn rate analysis
- Cash runway predictions
- Anomaly detection
- Trend analysis and insights

---

## 📁 Project Structure

```
Finly-prototype/
├── src/
│   ├── quickbooks/           # QuickBooks integration
│   │   ├── auth.py          # OAuth authentication
│   │   ├── client.py        # API client
│   │   └── transformer.py   # Data transformation
│   │
│   ├── forecasting/          # ML forecasting engine
│   │   ├── models/          # ML models
│   │   ├── engine.py        # Main forecast engine
│   │   └── predictor.py     # Category predictors
│   │
│   ├── dashboard/            # Web dashboard
│   │   ├── app.py           # Main dashboard app
│   │   ├── components/      # UI components
│   │   └── utils/           # Dashboard utilities
│   │
│   └── database/             # Data persistence
│       ├── models.py        # Database models
│       └── repository.py    # Data access layer
│
├── config/                   # Configuration files
│   ├── quickbooks.yaml      # QuickBooks settings
│   └── models.yaml          # ML model config
│
├── tests/                    # Unit and integration tests
├── docs/                     # Documentation
├── outputs/                  # Generated forecasts
├── data/                     # Sample/cache data
└── requirements.txt          # Python dependencies
```

---

## 🚀 Quick Start

### 1. Installation

```bash
cd Finly-prototype
pip install -r requirements.txt
```

### 2. Configure QuickBooks

```bash
# Set up your QuickBooks credentials
cp config/quickbooks.example.yaml config/quickbooks.yaml
# Edit config/quickbooks.yaml with your credentials
```

### 3. Run the Dashboard

```bash
streamlit run src/dashboard/app.py
```

### 4. Generate Forecast

```python
from src.forecasting.engine import ForecastEngine
from src.quickbooks.client import QuickBooksClient

# Connect to QuickBooks
qb = QuickBooksClient()
transactions = qb.get_transactions(days=365)

# Generate forecast
engine = ForecastEngine()
forecast = engine.generate_forecast(transactions, weeks=13)

print(f"13-Week Projection: ${forecast.final_balance:,.2f}")
```

---

## 🔧 System Requirements

- Python 3.9+
- QuickBooks Online account
- 365+ days of transaction history (recommended)

---

## 📊 Forecast Accuracy

Finly uses a hybrid ML approach combining:
- **ARIMA** for time series patterns
- **Prophet** for seasonality
- **XGBoost** for category-specific predictions
- **Ensemble methods** for improved accuracy

**Typical Accuracy**: 85-95% for 13-week forecasts

---

## 🔐 Security

- OAuth 2.0 for QuickBooks authentication
- Encrypted credential storage
- No sensitive data in logs
- Local data processing option

---

## 📈 Roadmap

- [ ] QuickBooks Desktop support
- [ ] Multi-currency support
- [ ] Mobile app
- [ ] Slack/Email notifications
- [ ] Advanced scenario planning
- [ ] Industry benchmarking

---

## 📝 License

Proprietary - All rights reserved

---

## 🤝 Support

For issues or questions, please contact: support@finly.app

---

**Built for SMBs, powered by AI**
