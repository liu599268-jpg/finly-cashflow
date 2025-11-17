# Finly - Quick Start Guide

Get your cash flow forecasting application up and running in minutes!

---

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd /Users/lhr/Desktop/Finly-prototype
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### 2. Configure QuickBooks (Optional)

```bash
# Copy QuickBooks config template
cp config/quickbooks.example.yaml config/quickbooks.yaml

# Edit with your QuickBooks credentials
nano config/quickbooks.yaml
```

**To get QuickBooks credentials:**
1. Go to [QuickBooks Developer Portal](https://developer.intuit.com/)
2. Create an app
3. Get your Client ID and Client Secret
4. Set redirect URI to `http://localhost:8000/callback`

---

## 🎯 Running the Application

### Option 1: Run Dashboard (Recommended)

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Option 2: Use Python API

```python
from src.forecasting import ForecastEngine, HistoricalData
from src.quickbooks import QuickBooksClient, QuickBooksTransformer

# 1. Connect to QuickBooks
qb_client = QuickBooksClient()
qb_transactions = qb_client.get_transactions(days=365)

# 2. Transform data
transformer = QuickBooksTransformer()
finly_transactions = transformer.transform_transactions(qb_transactions)

# 3. Generate forecast
engine = ForecastEngine()
forecast = engine.generate_forecast(
    historical_data=finly_transactions,
    company_name="My Company",
    weeks_ahead=13
)

# 4. View results
print(f"Current Balance: ${forecast.current_balance:,.2f}")
print(f"13-Week Projection: ${forecast.get_final_balance():,.2f}")
```

---

## 📊 Demo Mode

If you don't have QuickBooks set up yet, you can run in demo mode with sample data:

```python
from utils.sample_data import SampleDataGenerator
from src.forecasting import ForecastEngine

# Generate sample data
generator = SampleDataGenerator()
historical = generator.generate_transactions(num_weeks=52)

# Create forecast
engine = ForecastEngine()
forecast = engine.generate_forecast(
    historical_data=historical,
    company_name="Demo Company",
    weeks_ahead=13
)

print(f"Demo Forecast Generated!")
print(f"Ending Balance: ${forecast.get_final_balance():,.2f}")
```

---

## 📁 Project Structure

```
Finly-prototype/
├── src/
│   ├── quickbooks/          # QuickBooks integration
│   │   ├── auth.py         # OAuth authentication
│   │   ├── client.py       # API client
│   │   └── transformer.py  # Data transformation
│   │
│   ├── forecasting/         # ML forecasting engine
│   │   ├── models.py       # Data models
│   │   ├── engine.py       # Forecast engine
│   │   ├── predictor.py    # ML predictors
│   │   └── processor.py    # Data processing
│   │
│   └── dashboard/           # Web dashboard
│       └── app.py          # Streamlit app
│
├── config/                  # Configuration files
├── utils/                   # Utilities
├── outputs/                 # Generated forecasts
└── requirements.txt         # Dependencies
```

---

## 🔍 Common Tasks

### Generate a Forecast

```bash
# Using the dashboard
streamlit run src/dashboard/app.py
# Navigate to "Forecast" page
```

### View Historical Data

```python
from src.quickbooks import QuickBooksClient

client = QuickBooksClient()
transactions = client.get_transactions(days=90)
print(f"Found {len(transactions)} transactions in last 90 days")
```

### Run Scenario Analysis

```bash
# In the dashboard, go to "Scenarios" page
# Configure different scenarios and compare results
```

---

## 🎓 Key Features

### 1. QuickBooks Integration
- OAuth 2.0 authentication
- Automatic transaction sync
- Category mapping

### 2. AI/ML Forecasting
- 13-week predictions
- Multiple models (ARIMA, Prophet, XGBoost)
- Confidence intervals
- Category-level forecasting

### 3. Interactive Dashboard
- Real-time visualizations
- Cash flow projections
- Scenario planning
- Executive summaries

### 4. Smart Analytics
- Burn rate calculation
- Cash runway prediction
- Trend analysis
- Anomaly detection

---

## ⚠️ Troubleshooting

### QuickBooks Connection Issues

**Problem:** "Authentication failed"
**Solution:**
- Verify credentials in `.env` file
- Check that redirect URI matches QuickBooks app settings
- Ensure you're using correct environment (sandbox/production)

### Dashboard Won't Start

**Problem:** `ModuleNotFoundError`
**Solution:**
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Verify Python version (3.9+)
python --version
```

### Forecast Generation Errors

**Problem:** "Insufficient data"
**Solution:**
- Ensure you have at least 12 weeks of historical data
- Check that transactions are properly categorized
- Verify date ranges in QuickBooks

---

## 📈 Next Steps

1. **Connect Your QuickBooks Account**
   - Set up OAuth credentials
   - Run initial data sync

2. **Generate Your First Forecast**
   - Review historical transactions
   - Generate 13-week projection
   - Analyze results

3. **Explore Scenarios**
   - Create best/worst case scenarios
   - Compare different business strategies
   - Make data-driven decisions

4. **Customize Categories**
   - Map QuickBooks categories to your business
   - Adjust forecasting parameters
   - Fine-tune model settings

---

## 📚 Additional Resources

- [QuickBooks API Documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Prophet Forecasting Guide](https://facebook.github.io/prophet/)

---

## 🤝 Support

For questions or issues:
- Review the main [README.md](README.md)
- Check configuration files in `config/`
- Examine example code in project files

---

**Ready to forecast? Let's go!** 🚀

```bash
streamlit run src/dashboard/app.py
```
