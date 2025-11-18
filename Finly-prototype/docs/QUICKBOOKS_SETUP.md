# QuickBooks Integration Setup Guide

Complete guide to setting up QuickBooks integration with Finly.

---

## 📋 Prerequisites

Before you begin, make sure you have:

- [ ] QuickBooks Online account (Sandbox or Production)
- [ ] Intuit Developer account
- [ ] Python 3.9 or higher installed
- [ ] Finly-prototype project set up

---

## 🔑 Step 1: Get QuickBooks Developer Credentials

### 1.1 Create Intuit Developer Account

1. Go to [Intuit Developer Portal](https://developer.intuit.com/)
2. Click **"Sign Up"** or **"Sign In"** if you have an account
3. Complete the registration process

### 1.2 Create a New App

1. Navigate to **"My Apps"** in the developer dashboard
2. Click **"Create an app"**
3. Select **"QuickBooks Online and Payments"**
4. Fill in app details:
   - **App Name**: "Finly Cash Flow Forecasting" (or your choice)
   - **Description**: "AI-powered cash flow forecasting for SMBs"
5. Click **"Create app"**

### 1.3 Get App Credentials

1. In your app dashboard, go to **"Keys & OAuth"** tab
2. You'll see:
   - **Development** (Sandbox) credentials
   - **Production** credentials

3. Copy the following:
   - **Client ID**
   - **Client Secret**

**Important:** Keep these credentials secure! Never commit them to git.

### 1.4 Configure Redirect URI

1. In the **"Keys & OAuth"** tab, scroll to **"Redirect URIs"**
2. Add: `http://localhost:8000/callback`
3. Click **"Save"**

This is where QuickBooks will redirect after authentication.

---

## ⚙️ Step 2: Configure Finly

### 2.1 Set Environment Variables

Create or edit your `.env` file:

```bash
cd /Users/lhr/Desktop/Finly-prototype
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# QuickBooks Credentials
QB_CLIENT_ID=your_client_id_here
QB_CLIENT_SECRET=your_client_secret_here
QB_REDIRECT_URI=http://localhost:8000/callback
QB_ENVIRONMENT=sandbox  # or "production"

# Optional: If you already know your company ID
QB_COMPANY_ID=your_company_id_here
```

**For Development/Testing:**
- Use **Sandbox** credentials
- Set `QB_ENVIRONMENT=sandbox`

**For Production:**
- Use **Production** credentials
- Set `QB_ENVIRONMENT=production`

### 2.2 Configure QuickBooks YAML

```bash
cp config/quickbooks.example.yaml config/quickbooks.yaml
```

Edit `config/quickbooks.yaml`:

```yaml
quickbooks:
  client_id: "your_client_id_here"
  client_secret: "your_client_secret_here"
  redirect_uri: "http://localhost:8000/callback"
  company_id: "your_company_id_here"  # Optional, obtained after first auth
  environment: "sandbox"  # or "production"
```

---

## 🧪 Step 3: Test in Sandbox

### 3.1 Create Sandbox Test Company

1. In Intuit Developer Portal, go to your app
2. Click **"Sandbox"** tab
3. Click **"Create new sandbox company"**
4. Select a sample company type (e.g., "Retail", "Services")
5. Wait for company creation (takes ~30 seconds)

### 3.2 Add Sample Data

1. Once created, click **"View company"**
2. This opens QuickBooks Online in sandbox mode
3. Add some sample transactions:
   - Create invoices
   - Record payments
   - Add bills
   - Enter expenses

**Or use the sample data generator:**
- QuickBooks sandbox comes pre-populated with data
- You can use this for testing

---

## 🔐 Step 4: Authenticate with QuickBooks

### 4.1 Using the Demo Script

```bash
cd /Users/lhr/Desktop/Finly-prototype

# Install dependencies if not already installed
pip install -r requirements.txt

# Run the demo
python quickbooks_demo.py
```

**What happens:**
1. Script starts OAuth flow
2. Browser opens to QuickBooks login
3. Log in with your Intuit account
4. Authorize the app to access your data
5. Browser redirects to callback (shows success page)
6. Script receives access token
7. Token is saved to `~/.finly/qb_tokens.json`

### 4.2 Manual Authentication in Python

```python
from src.quickbooks import QuickBooksAuth, authenticate_quickbooks

# Initialize auth
auth = QuickBooksAuth(environment='sandbox')

# Start authentication flow
access_token, company_id = authenticate_quickbooks(auth)

print(f"Authenticated! Company ID: {company_id}")
```

### 4.3 Save Company ID

After first authentication, you'll get a **Company ID** (also called Realm ID).

Add it to your `.env`:

```bash
QB_COMPANY_ID=1234567890  # Your actual company ID
```

---

## 📊 Step 5: Test Data Fetching

### 5.1 Test Connection

```python
from src.quickbooks import QuickBooksClient, QuickBooksAuth

# Initialize
auth = QuickBooksAuth()
client = QuickBooksClient(auth=auth, company_id="YOUR_COMPANY_ID")

# Test connection
if client.test_connection():
    print("✓ Connected to QuickBooks!")

# Get company info
company = client.get_company_info()
print(f"Company: {company['CompanyInfo']['CompanyName']}")
```

### 5.2 Fetch Transactions

```python
from datetime import datetime, timedelta

# Get last 90 days of transactions
transactions = client.get_transactions(days=90)
print(f"Found {len(transactions)} transactions")

# Get invoices
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
invoices = client.get_invoices(start_date, end_date)
print(f"Found {len(invoices)} invoices")
```

### 5.3 Get Account Balances

```python
# Cash balance
cash = client.get_cash_balance()
print(f"Cash Balance: ${cash:,.2f}")

# Accounts Receivable
ar_data = client.get_accounts_receivable()
print(f"AR Balance: ${ar_data['total_balance']:,.2f}")

# Accounts Payable
ap = client.get_accounts_payable()
print(f"AP Balance: ${ap:,.2f}")
```

---

## 🔄 Step 6: Token Management

### 6.1 Token Storage

Tokens are automatically stored in:
```
~/.finly/qb_tokens.json
```

**Security:**
- File permissions are set to `600` (owner read/write only)
- Never commit this file to git
- It's in `.gitignore` by default

### 6.2 Token Refresh

Access tokens expire after **1 hour**. Refresh tokens last **100 days**.

**Automatic refresh:**
```python
# The client automatically refreshes tokens
client = QuickBooksClient(auth=auth, company_id=company_id)

# This will auto-refresh if expired
transactions = client.get_transactions()
```

**Manual refresh:**
```python
from src.quickbooks import QuickBooksAuth

auth = QuickBooksAuth()

# Check if authenticated
if not auth.is_authenticated():
    # Need to re-authenticate
    print("Token expired, please re-authenticate")
```

### 6.3 Revoke Access

```python
auth = QuickBooksAuth()
auth.revoke_tokens()
print("Access revoked")
```

---

## 🚀 Step 7: Go to Production

### 7.1 Production App Review

1. In Intuit Developer Portal, go to your app
2. Click **"Production"** tab
3. Complete **"Production Readiness Checklist"**:
   - Privacy policy URL
   - Terms of service URL
   - App description
   - Screenshots

4. Submit for review
5. Wait for approval (typically 1-3 business days)

### 7.2 Switch to Production

Once approved:

1. Update `.env`:
   ```bash
   QB_ENVIRONMENT=production
   ```

2. Use production credentials from developer portal

3. Re-authenticate with production QuickBooks account

---

## 🐛 Troubleshooting

### Error: "invalid_client"

**Cause:** Incorrect Client ID or Client Secret

**Solution:**
- Double-check credentials in `.env`
- Ensure no extra spaces or quotes
- Verify you're using correct environment (sandbox/production)

### Error: "redirect_uri_mismatch"

**Cause:** Redirect URI doesn't match app settings

**Solution:**
- Check redirect URI in developer portal matches exactly: `http://localhost:8000/callback`
- No trailing slash
- Lowercase "localhost"

### Error: "unauthorized_client"

**Cause:** App not approved for production

**Solution:**
- Use sandbox environment for development
- Complete production review process before using production

### Error: "Token expired"

**Cause:** Access token expired (>1 hour old)

**Solution:**
- Tokens auto-refresh automatically
- If refresh token expired (>100 days), re-authenticate:
  ```python
  from src.quickbooks import QuickBooksAuth, authenticate_quickbooks

  auth = QuickBooksAuth()
  access_token, company_id = authenticate_quickbooks(auth)
  ```

### Browser doesn't open

**Manual authentication:**
1. Script will print authorization URL
2. Copy and paste into browser manually
3. Complete authorization
4. Continue as normal

---

## 📋 Quick Reference

### Authentication Flow

```
1. User runs app/script
   ↓
2. App generates authorization URL
   ↓
3. Browser opens to QuickBooks login
   ↓
4. User logs in and authorizes
   ↓
5. QuickBooks redirects to callback URL
   ↓
6. Callback server receives authorization code
   ↓
7. App exchanges code for access token
   ↓
8. Token saved to ~/.finly/qb_tokens.json
   ↓
9. App can now make API calls
```

### API Endpoints Used

| Function | QuickBooks API Endpoint |
|----------|------------------------|
| Get Invoices | `/query?query=SELECT * FROM Invoice` |
| Get Payments | `/query?query=SELECT * FROM Payment` |
| Get Bills | `/query?query=SELECT * FROM Bill` |
| Get Accounts | `/query?query=SELECT * FROM Account` |
| Get Company | `/companyinfo/1` |

### Token Lifetimes

| Token Type | Lifetime | What Happens When Expired |
|------------|----------|--------------------------|
| Access Token | 1 hour | Auto-refresh with refresh token |
| Refresh Token | 100 days | Must re-authenticate |

---

## 🔐 Security Best Practices

1. **Never commit credentials:**
   - `.env` is in `.gitignore`
   - `config/quickbooks.yaml` is in `.gitignore`
   - Tokens stored in `~/.finly/` (outside project)

2. **Use environment variables:**
   - Preferred over config files
   - Easier to manage across environments

3. **Rotate credentials periodically:**
   - Generate new Client Secret every 6 months
   - Update in `.env`

4. **Limit API scope:**
   - Only request scopes you need
   - Default: `com.intuit.quickbooks.accounting` (read/write)

5. **Monitor API usage:**
   - Check developer dashboard for API calls
   - Stay within rate limits

---

## 📚 Additional Resources

- [QuickBooks API Documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice)
- [OAuth 2.0 Guide](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)
- [API Explorer](https://developer.intuit.com/app/developer/qbo/docs/develop/sandboxes/manage-your-sandboxes)
- [Rate Limits](https://developer.intuit.com/app/developer/qbo/docs/develop/explore-the-quickbooks-online-api/api-rate-limits)

---

## ✅ Setup Checklist

- [ ] Created Intuit Developer account
- [ ] Created QuickBooks app
- [ ] Got Client ID and Client Secret
- [ ] Configured Redirect URI
- [ ] Created sandbox test company
- [ ] Set up `.env` file
- [ ] Installed Python dependencies
- [ ] Ran authentication flow
- [ ] Successfully fetched data
- [ ] Tested in Finly dashboard

---

**Need help?** Check the troubleshooting section or review the demo script at `quickbooks_demo.py`
