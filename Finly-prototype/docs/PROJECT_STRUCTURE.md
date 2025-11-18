# Finly Project Structure

Complete overview of the Finly cash flow forecasting application architecture.

---

## 📁 Directory Structure

```
Finly-prototype/
│
├── src/                          # Main source code
│   ├── __init__.py
│   │
│   ├── quickbooks/              # QuickBooks integration (Feature #1)
│   │   ├── __init__.py
│   │   ├── auth.py             # OAuth 2.0 authentication
│   │   ├── client.py           # QuickBooks API client
│   │   └── transformer.py      # Data transformation
│   │
│   ├── forecasting/             # ML forecasting engine (Feature #3)
│   │   ├── __init__.py
│   │   ├── models.py           # Data models
│   │   ├── engine.py           # Main forecast engine
│   │   ├── predictor.py        # Category predictors
│   │   └── processor.py        # Data processing/validation
│   │
│   ├── dashboard/               # Web dashboard (Feature #4)
│   │   ├── __init__.py
│   │   ├── app.py              # Main Streamlit application
│   │   └── components/         # Dashboard components
│   │
│   └── database/                # Data persistence (Optional)
│       ├── __init__.py
│       ├── models.py           # Database models
│       └── repository.py       # Data access layer
│
├── config/                       # Configuration files
│   ├── quickbooks.example.yaml  # QuickBooks config template
│   └── models.yaml              # ML model configuration
│
├── utils/                        # Utility functions
│   ├── __init__.py
│   └── sample_data.py           # Sample data generator
│
├── tests/                        # Unit and integration tests
│   ├── __init__.py
│   ├── test_quickbooks.py
│   ├── test_forecasting.py
│   └── test_dashboard.py
│
├── docs/                         # Documentation
│   ├── PROJECT_STRUCTURE.md     # This file
│   ├── API.md                   # API documentation
│   └── DEPLOYMENT.md            # Deployment guide
│
├── outputs/                      # Generated forecasts and reports
│   ├── forecasts/
│   ├── reports/
│   └── exports/
│
├── data/                         # Data storage
│   ├── cache/                   # Cached data
│   └── raw/                     # Raw data (gitignored)
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
└── requirements.txt              # Python dependencies
```

---

## 🎯 Core Modules

### 1. QuickBooks Integration (`src/quickbooks/`)

**Purpose:** Connect to QuickBooks Online and retrieve transaction data

**Components:**

- **auth.py** - OAuth 2.0 authentication
  - Manages access tokens
  - Handles token refresh
  - Secures credentials

- **client.py** - API client
  - Retrieves invoices, payments, bills
  - Gets AR/AP balances
  - Tests connection

- **transformer.py** - Data transformation
  - Converts QuickBooks format to Finly format
  - Maps categories
  - Generates summaries

**Usage:**
```python
from src.quickbooks import QuickBooksClient

client = QuickBooksClient()
transactions = client.get_transactions(days=365)
```

---

### 2. Forecasting Engine (`src/forecasting/`)

**Purpose:** Generate AI/ML-powered cash flow forecasts

**Components:**

- **models.py** - Data models
  - Transaction, HistoricalData, Forecast
  - Type definitions
  - Data structures

- **engine.py** - Main forecast engine
  - Orchestrates forecasting process
  - Combines category predictions
  - Calculates confidence intervals

- **predictor.py** - Category predictors
  - Per-category forecasting
  - Multiple ML models
  - Ensemble methods

- **processor.py** - Data processing
  - Data validation
  - Cleaning and normalization
  - Statistical analysis

**Usage:**
```python
from src.forecasting import ForecastEngine

engine = ForecastEngine()
forecast = engine.generate_forecast(
    historical_data=transactions,
    company_name="My Company",
    weeks_ahead=13
)
```

---

### 3. Web Dashboard (`src/dashboard/`)

**Purpose:** Interactive web interface for forecasting

**Components:**

- **app.py** - Main Streamlit application
  - Dashboard overview
  - Forecast generation
  - Scenario analysis
  - Settings

**Pages:**
1. **Dashboard** - Overview and key metrics
2. **Forecast** - Generate new forecasts
3. **Scenarios** - Compare business scenarios
4. **Settings** - Configuration

**Usage:**
```bash
streamlit run src/dashboard/app.py
```

---

## 🔄 Data Flow

```
1. QuickBooks → Retrieve Transactions
         ↓
2. Transformer → Convert to Finly Format
         ↓
3. Processor → Validate & Clean Data
         ↓
4. Forecasting Engine → Generate Predictions
         ↓
5. Dashboard → Display Results
```

---

## 📊 Data Models

### Transaction
- date: datetime
- amount: float
- category: CashFlowCategory
- transaction_type: TransactionType (inflow/outflow)
- description: str
- customer/vendor: str

### HistoricalData
- transactions: List[Transaction]
- start_date: datetime
- end_date: datetime
- opening_balance: float

### Forecast
- company_name: str
- forecast_date: datetime
- current_balance: float
- forecast_points: List[ForecastPoint]
- model_accuracy: float

### ForecastPoint
- date: datetime
- predicted_balance: float
- confidence_lower: float
- confidence_upper: float
- predicted_inflows: float
- predicted_outflows: float

---

## 🔧 Configuration

### QuickBooks Config (`config/quickbooks.yaml`)
- OAuth credentials
- Company ID
- Environment (sandbox/production)
- Category mappings

### Model Config (`config/models.yaml`)
- Forecast horizon
- Confidence levels
- Model parameters (ARIMA, Prophet, XGBoost)
- Ensemble weights

### Environment Variables (`.env`)
- QB_CLIENT_ID
- QB_CLIENT_SECRET
- QB_COMPANY_ID
- DATABASE_URL
- SECRET_KEY

---

## 🧪 Testing Structure

```
tests/
├── test_quickbooks.py      # QuickBooks integration tests
│   ├── test_auth
│   ├── test_client
│   └── test_transformer
│
├── test_forecasting.py     # Forecasting engine tests
│   ├── test_engine
│   ├── test_predictor
│   └── test_processor
│
└── test_dashboard.py       # Dashboard tests
    └── test_pages
```

**Run tests:**
```bash
pytest tests/
pytest tests/ --cov=src
```

---

## 📦 Dependencies

### Core
- numpy, pandas - Data processing
- scikit-learn - ML models
- statsmodels - Time series
- prophet, xgboost - Advanced forecasting

### Dashboard
- streamlit - Web framework
- plotly - Interactive charts
- altair - Visualizations

### Integration
- requests - HTTP client
- requests-oauthlib - OAuth
- python-dotenv - Environment variables

---

## 🚀 Development Workflow

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Application**
   ```bash
   cp .env.example .env
   cp config/quickbooks.example.yaml config/quickbooks.yaml
   # Edit files with your credentials
   ```

3. **Run in Development**
   ```bash
   streamlit run src/dashboard/app.py
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

---

## 📈 Scaling Considerations

### Current (Prototype)
- Single user
- Local storage
- Sample/demo data

### Production Ready
- Multi-tenant
- PostgreSQL database
- Redis caching
- API endpoints
- Background jobs
- Docker deployment

---

## 🔐 Security

### Current Measures
- OAuth 2.0 for QuickBooks
- Token encryption
- Environment variables for secrets
- .gitignore for sensitive files

### Production Additions
- HTTPS only
- Database encryption
- Audit logging
- Rate limiting
- Input validation

---

## 📝 Key Files Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `src/quickbooks/auth.py` | QuickBooks auth | OAuth flow changes |
| `src/quickbooks/client.py` | API calls | New QB endpoints |
| `src/quickbooks/transformer.py` | Data mapping | Category changes |
| `src/forecasting/engine.py` | Forecast logic | Algorithm updates |
| `src/forecasting/predictor.py` | ML models | Model improvements |
| `src/dashboard/app.py` | Dashboard | UI changes |
| `config/models.yaml` | Model params | Tuning models |
| `requirements.txt` | Dependencies | New packages |

---

## 🎓 Learning Path

1. **Start Here:** README.md → QUICKSTART.md
2. **Understand Structure:** This file (PROJECT_STRUCTURE.md)
3. **Try Demo:** Run dashboard with sample data
4. **Connect QuickBooks:** Set up OAuth
5. **Generate Forecast:** Use your real data
6. **Customize:** Adjust categories and models
7. **Deploy:** Move to production

---

**For more information, see:**
- [README.md](../README.md) - Overview and features
- [QUICKSTART.md](../QUICKSTART.md) - Getting started guide
- Configuration files in `config/`
