# QuickBooks Integration Module

Complete reference for the Finly QuickBooks integration.

---

## 📋 Overview

The QuickBooks integration module provides seamless OAuth 2.0 authentication and comprehensive data retrieval from QuickBooks Online. It includes automatic token management, data transformation, and enhanced fetching capabilities.

---

## 🎯 Features

### ✅ OAuth 2.0 Authentication
- Secure OAuth 2.0 flow with automatic token refresh
- Local callback server for authorization
- Encrypted token storage
- Sandbox and production environment support

### ✅ Transaction Data Fetching
- Invoices (paid and unpaid)
- Payments and collections
- Bills and expenses
- Purchase transactions
- Historical data with date filtering

### ✅ Account Balance Retrieval
- Cash and bank account balances
- Accounts Receivable with aging
- Accounts Payable
- Detailed account breakdowns by type

### ✅ Enhanced Data Features
- Revenue and expense summaries
- Cash flow analysis
- Customer and vendor management
- Profit & Loss reports
- Balance Sheet reports

### ✅ Data Transformation
- QuickBooks to Finly format conversion
- Automatic category mapping
- Custom category support
- Transaction normalization

---

## 📁 Module Structure

```
src/quickbooks/
├── __init__.py           # Module exports
├── auth.py              # OAuth 2.0 authentication
├── client.py            # QuickBooks API client
├── oauth_server.py      # OAuth callback server
├── transformer.py       # Data transformation
└── data_fetcher.py      # Enhanced data fetching
```

---

## 🔐 Authentication

### Basic Authentication

```python
from src.quickbooks import QuickBooksAuth, authenticate_quickbooks

# Initialize authentication
auth = QuickBooksAuth(environment='sandbox')

# Start OAuth flow (opens browser)
access_token, company_id = authenticate_quickbooks(auth)

print(f"Authenticated! Company ID: {company_id}")
```

### Check Authentication Status

```python
if auth.is_authenticated():
    print("Already authenticated")
else:
    print("Need to authenticate")
```

### Manual Token Management

```python
# Get current access token (auto-refreshes if needed)
token = auth.get_access_token()

# Manually refresh token
new_tokens = auth.refresh_access_token(refresh_token)

# Revoke tokens
auth.revoke_tokens()
```

---

## 📊 Data Fetching

### Initialize Client

```python
from src.quickbooks import QuickBooksClient, QuickBooksAuth

auth = QuickBooksAuth()
client = QuickBooksClient(
    auth=auth,
    company_id="YOUR_COMPANY_ID"
)

# Test connection
if client.test_connection():
    print("Connected!")
```

### Fetch Transactions

```python
from datetime import datetime, timedelta

# Get all transactions (last 365 days)
transactions = client.get_transactions(days=365)
print(f"Found {len(transactions)} transactions")

# Get transactions for specific date range
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

invoices = client.get_invoices(start_date, end_date)
payments = client.get_payments(start_date, end_date)
bills = client.get_bills(start_date, end_date)
expenses = client.get_expenses(start_date, end_date)
```

### Get Invoice Information

```python
# Get all invoices
invoices = client.get_invoices(start_date, end_date)

for invoice in invoices:
    print(f"Invoice #{invoice['DocNumber']}")
    print(f"  Customer: {invoice['CustomerRef']['name']}")
    print(f"  Amount: ${invoice['TotalAmt']}")
    print(f"  Balance: ${invoice.get('Balance', 0)}")
    print(f"  Status: {invoice.get('Status', 'N/A')}")
```

### Get Account Balances

```python
# Cash balance
cash = client.get_cash_balance()
print(f"Cash Balance: ${cash:,.2f}")

# Accounts Receivable
ar_data = client.get_accounts_receivable()
print(f"Total AR: ${ar_data['total_balance']:,.2f}")
print(f"AR Aging:")
for bucket, amount in ar_data['aging'].items():
    print(f"  {bucket}: ${amount:,.2f}")

# Accounts Payable
ap = client.get_accounts_payable()
print(f"Total AP: ${ap:,.2f}")
```

### Get Company Information

```python
company_info = client.get_company_info()
company = company_info['CompanyInfo']

print(f"Company: {company['CompanyName']}")
print(f"Legal Name: {company.get('LegalName')}")
print(f"Industry: {company.get('Industry', 'N/A')}")
```

---

## 🚀 Enhanced Data Fetching

### Initialize Enhanced Fetcher

```python
from src.quickbooks import QuickBooksDataFetcher

fetcher = QuickBooksDataFetcher(client)
```

### Invoice Operations

```python
# Get all invoices with filtering
invoices = fetcher.get_all_invoices(
    status='Unpaid',
    start_date=start_date,
    end_date=end_date
)

# Get specific invoice details
invoice = fetcher.get_invoice_details(invoice_id='123')

# Get outstanding invoices
outstanding = fetcher.get_outstanding_invoices()
total_outstanding = sum(float(inv['Balance']) for inv in outstanding)

# Get overdue invoices
overdue = fetcher.get_overdue_invoices()
print(f"Overdue invoices: {len(overdue)}")
```

### Revenue & Expense Analysis

```python
# Revenue summary
revenue = fetcher.get_revenue_summary(start_date, end_date)
print(f"Total Invoiced: ${revenue['total_invoiced']:,.2f}")
print(f"Total Collected: ${revenue['total_collected']:,.2f}")
print(f"Collection Rate: {revenue['collection_rate']:.1f}%")

# Expense summary
expenses = fetcher.get_expense_summary(start_date, end_date)
print(f"Total Bills: ${expenses['total_bills']:,.2f}")
print(f"Total Expenses: ${expenses['total_expenses']:,.2f}")
print(f"Total Outflows: ${expenses['total_outflows']:,.2f}")
```

### Cash Flow Summary

```python
# Comprehensive cash flow summary
cash_flow = fetcher.get_cash_flow_summary(start_date, end_date)

print(f"Current Cash: ${cash_flow['current_cash_balance']:,.2f}")
print(f"Total Inflows: ${cash_flow['total_inflows']:,.2f}")
print(f"Total Outflows: ${cash_flow['total_outflows']:,.2f}")
print(f"Net Cash Flow: ${cash_flow['net_cash_flow']:,.2f}")
```

### Detailed Account Balances

```python
# Get detailed balances by account type
balances = fetcher.get_account_balances_detailed()

print("Bank Accounts:")
for account in balances['bank']:
    print(f"  {account['name']}: ${account['current_balance']:,.2f}")

print("\nCredit Cards:")
for account in balances['credit_card']:
    print(f"  {account['name']}: ${account['current_balance']:,.2f}")
```

### Reports

```python
# Profit & Loss
p_and_l = fetcher.get_profit_and_loss(start_date, end_date)

# Balance Sheet
balance_sheet = fetcher.get_balance_sheet(as_of_date=datetime.now())

# Transaction counts
counts = fetcher.get_transaction_count_by_type(start_date, end_date)
print(f"Invoices: {counts['invoices']}")
print(f"Payments: {counts['payments']}")
print(f"Bills: {counts['bills']}")
print(f"Total: {counts['total']}")
```

---

## 🔄 Data Transformation

### Transform QuickBooks Data to Finly Format

```python
from src.quickbooks import QuickBooksTransformer

# Initialize transformer
transformer = QuickBooksTransformer()

# Get QuickBooks transactions
qb_transactions = client.get_transactions(days=90)

# Transform to Finly format
finly_transactions = transformer.transform_transactions(qb_transactions)

# Each Finly transaction has:
# - date: ISO format datetime
# - amount: float
# - category: CashFlowCategory enum value
# - transaction_type: 'inflow' or 'outflow'
# - description: string
# - customer: string (if applicable)
# - vendor: string (if applicable)
# - reference_id: original QB ID
# - reference_type: transaction type
```

### Custom Category Mapping

```python
from src.quickbooks.transformer import CashFlowCategory

# Define custom mappings
custom_mappings = {
    'Consulting Income': CashFlowCategory.REVENUE,
    'Cloud Services': CashFlowCategory.TECHNOLOGY,
    'Employee Benefits': CashFlowCategory.PAYROLL
}

# Create transformer with custom mappings
transformer = QuickBooksTransformer(custom_category_map=custom_mappings)

# Transform with custom mappings
finly_transactions = transformer.transform_transactions(qb_transactions)
```

### Get Summary Statistics

```python
# Get historical summary
summary = transformer.get_historical_summary(finly_transactions)

print(f"Total Transactions: {summary['total_transactions']}")
print(f"Total Inflows: ${summary['total_inflows']:,.2f}")
print(f"Total Outflows: ${summary['total_outflows']:,.2f}")
print(f"Net Cash Flow: ${summary['net_cash_flow']:,.2f}")
print(f"Date Range: {summary['date_range']['days']} days")

# Category breakdown
for category, data in summary['categories'].items():
    print(f"{category}: ${data['total']:,.2f} ({data['count']} txns)")
```

---

## 🎯 Common Use Cases

### Use Case 1: Daily Data Sync

```python
from datetime import datetime, timedelta

# Get yesterday's transactions
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()

transactions = client.get_transactions(
    start_date=yesterday,
    end_date=today
)

# Transform and store
finly_txns = transformer.transform_transactions(transactions)

# Save to database or file
# ... your storage logic here
```

### Use Case 2: Monthly Financial Report

```python
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Get current month data
today = datetime.now()
month_start = today.replace(day=1)

fetcher = QuickBooksDataFetcher(client)

# Get summaries
revenue = fetcher.get_revenue_summary(month_start, today)
expenses = fetcher.get_expense_summary(month_start, today)
cash_flow = fetcher.get_cash_flow_summary(month_start, today)

# Generate report
report = {
    'period': f"{month_start.strftime('%B %Y')}",
    'revenue': revenue,
    'expenses': expenses,
    'cash_flow': cash_flow
}
```

### Use Case 3: Customer AR Analysis

```python
# Get all customers
customers = fetcher.get_customers(active_only=True)

# Get outstanding balance for each
customer_ar = []
for customer in customers:
    balance = fetcher.get_customer_balance(customer['Id'])
    customer_ar.append({
        'name': customer['DisplayName'],
        'balance': balance
    })

# Sort by balance
customer_ar.sort(key=lambda x: x['balance'], reverse=True)

# Top 10 customers by AR
print("Top 10 Customers by AR:")
for i, cust in enumerate(customer_ar[:10], 1):
    print(f"{i}. {cust['name']}: ${cust['balance']:,.2f}")
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret

# Optional
QB_REDIRECT_URI=http://localhost:8000/callback
QB_COMPANY_ID=your_company_id
QB_ENVIRONMENT=sandbox  # or production
```

### YAML Configuration

```yaml
# config/quickbooks.yaml
quickbooks:
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  redirect_uri: "http://localhost:8000/callback"
  company_id: "YOUR_COMPANY_ID"
  environment: "sandbox"

category_mappings:
  "Sales of Product Income": "revenue"
  "Consulting Income": "revenue"
  "Employee Benefits": "payroll"
```

---

## 🐛 Error Handling

```python
from src.quickbooks import QuickBooksClient, QuickBooksAuth

try:
    auth = QuickBooksAuth()
    client = QuickBooksClient(auth=auth, company_id="123")

    # Test connection
    if not client.test_connection():
        print("Connection failed")
        exit(1)

    # Fetch data
    transactions = client.get_transactions()

except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

---

## 📊 API Reference

### QuickBooksAuth

| Method | Description |
|--------|-------------|
| `get_authorization_url()` | Generate OAuth URL |
| `exchange_code_for_tokens(code)` | Exchange auth code for tokens |
| `get_access_token()` | Get valid access token (auto-refresh) |
| `refresh_access_token(refresh_token)` | Manually refresh token |
| `is_authenticated()` | Check if authenticated |
| `revoke_tokens()` | Revoke and delete tokens |

### QuickBooksClient

| Method | Description |
|--------|-------------|
| `get_company_info()` | Get company information |
| `get_transactions(days)` | Get all transactions |
| `get_invoices(start, end)` | Get invoices |
| `get_payments(start, end)` | Get payments |
| `get_bills(start, end)` | Get bills |
| `get_expenses(start, end)` | Get expenses |
| `get_cash_balance()` | Get cash balance |
| `get_accounts_receivable()` | Get AR balance with aging |
| `get_accounts_payable()` | Get AP balance |
| `test_connection()` | Test API connection |

### QuickBooksDataFetcher

| Method | Description |
|--------|-------------|
| `get_all_invoices()` | Get invoices with filtering |
| `get_outstanding_invoices()` | Get unpaid invoices |
| `get_overdue_invoices()` | Get past due invoices |
| `get_revenue_summary()` | Revenue metrics |
| `get_expense_summary()` | Expense metrics |
| `get_cash_flow_summary()` | Cash flow analysis |
| `get_account_balances_detailed()` | Detailed account balances |
| `get_customers()` | Get customer list |
| `get_vendors()` | Get vendor list |

### QuickBooksTransformer

| Method | Description |
|--------|-------------|
| `transform_transactions(qb_txns)` | Transform to Finly format |
| `get_historical_summary(txns)` | Get summary statistics |

---

## 🧪 Testing

### Run Tests (No Credentials Required)

```bash
python quickbooks_test.py
```

### Run Demo (Requires Credentials)

```bash
python quickbooks_demo.py
```

---

## 📚 Additional Resources

- [Setup Guide](QUICKBOOKS_SETUP.md)
- [QuickBooks API Docs](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice)
- [OAuth 2.0 Guide](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)

---

**Complete integration ready for production use!**
