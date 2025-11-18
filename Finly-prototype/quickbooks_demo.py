"""
QuickBooks Integration Demo
Demonstrates how to authenticate and fetch data from QuickBooks
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.quickbooks import (
    QuickBooksAuth,
    QuickBooksClient,
    QuickBooksDataFetcher,
    QuickBooksTransformer,
    authenticate_quickbooks
)


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def demo_authentication():
    """Demonstrate OAuth authentication flow"""
    print_section("1. QuickBooks OAuth Authentication")

    print("This will open your browser to authenticate with QuickBooks.")
    print("You'll need:")
    print("  - QuickBooks Online account (Sandbox or Production)")
    print("  - QuickBooks app credentials (Client ID & Secret)")
    print("\nGet credentials at: https://developer.intuit.com/")

    input("\nPress Enter to continue...")

    # Initialize auth
    auth = QuickBooksAuth(
        environment='sandbox'  # or 'production'
    )

    # Check if already authenticated
    if auth.is_authenticated():
        print("\n✓ Already authenticated!")
        print(f"  Token file: {auth.token_file}")
        return auth, None

    # Start authentication flow
    try:
        access_token, realm_id = authenticate_quickbooks(auth)
        print(f"\n✓ Successfully authenticated!")
        print(f"  Company ID: {realm_id}")
        return auth, realm_id

    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nPlease ensure:")
        print("  1. QB_CLIENT_ID and QB_CLIENT_SECRET are set in .env")
        print("  2. Redirect URI matches your app settings")
        print("  3. You're using the correct environment (sandbox/production)")
        return None, None


def demo_fetch_data(client: QuickBooksClient):
    """Demonstrate data fetching"""
    print_section("2. Fetching QuickBooks Data")

    # Test connection
    print("Testing connection...")
    if not client.test_connection():
        print("✗ Connection failed")
        return

    print("✓ Connection successful\n")

    # Get company info
    print("Fetching company information...")
    try:
        company_info = client.get_company_info()
        company = company_info.get('CompanyInfo', {})
        print(f"  Company: {company.get('CompanyName')}")
        print(f"  Legal Name: {company.get('LegalName')}")
        print(f"  Industry: {company.get('Industry', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")

    # Get cash balance
    print("\nFetching cash balances...")
    try:
        cash_balance = client.get_cash_balance()
        print(f"  Total Cash: {format_currency(cash_balance)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Get AR balance
    print("\nFetching accounts receivable...")
    try:
        ar_data = client.get_accounts_receivable()
        print(f"  Total AR: {format_currency(ar_data['total_balance'])}")
        print(f"  Aging breakdown:")
        for bucket, amount in ar_data['aging'].items():
            print(f"    {bucket}: {format_currency(amount)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Get AP balance
    print("\nFetching accounts payable...")
    try:
        ap_balance = client.get_accounts_payable()
        print(f"  Total AP: {format_currency(ap_balance)}")
    except Exception as e:
        print(f"  Error: {e}")


def demo_fetch_transactions(client: QuickBooksClient):
    """Demonstrate transaction fetching"""
    print_section("3. Fetching Transaction Data")

    # Fetch last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    print(f"Fetching transactions from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

    try:
        transactions = client.get_transactions(days=90)
        print(f"\n✓ Found {len(transactions)} transactions")

        # Count by type
        invoices = [t for t in transactions if 'Invoice' in str(type(t)) or t.get('domain') == 'Invoice']
        payments = [t for t in transactions if 'Payment' in str(type(t)) or t.get('domain') == 'Payment']
        bills = [t for t in transactions if 'Bill' in str(type(t)) or t.get('domain') == 'Bill']
        expenses = [t for t in transactions if 'Purchase' in str(type(t)) or t.get('domain') == 'Purchase']

        print(f"\nBreakdown:")
        print(f"  Invoices: {len(invoices)}")
        print(f"  Payments: {len(payments)}")
        print(f"  Bills: {len(bills)}")
        print(f"  Expenses: {len(expenses)}")

        # Show sample transactions
        if transactions:
            print(f"\nSample transactions (first 3):")
            for i, txn in enumerate(transactions[:3]):
                print(f"\n  Transaction {i+1}:")
                print(f"    Date: {txn.get('TxnDate', 'N/A')}")
                print(f"    Amount: {format_currency(float(txn.get('TotalAmt', 0)))}")
                print(f"    Type: {txn.get('domain', 'Unknown')}")

    except Exception as e:
        print(f"✗ Error fetching transactions: {e}")


def demo_enhanced_data_fetcher(client: QuickBooksClient):
    """Demonstrate enhanced data fetcher"""
    print_section("4. Enhanced Data Fetching")

    fetcher = QuickBooksDataFetcher(client)

    # Get invoice summary
    print("Fetching invoice data...")
    try:
        # Outstanding invoices
        outstanding = fetcher.get_outstanding_invoices()
        print(f"  Outstanding invoices: {len(outstanding)}")

        total_outstanding = sum(float(inv.get('Balance', 0)) for inv in outstanding)
        print(f"  Total outstanding: {format_currency(total_outstanding)}")

        # Overdue invoices
        overdue = fetcher.get_overdue_invoices()
        print(f"  Overdue invoices: {len(overdue)}")

        total_overdue = sum(float(inv.get('Balance', 0)) for inv in overdue)
        print(f"  Total overdue: {format_currency(total_overdue)}")

    except Exception as e:
        print(f"  Error: {e}")

    # Get cash flow summary
    print("\nFetching cash flow summary (last 30 days)...")
    try:
        cash_flow = fetcher.get_cash_flow_summary()
        print(f"  Period: {cash_flow['period_start']} to {cash_flow['period_end']}")
        print(f"  Current cash: {format_currency(cash_flow['current_cash_balance'])}")
        print(f"  Total inflows: {format_currency(cash_flow['total_inflows'])}")
        print(f"  Total outflows: {format_currency(cash_flow['total_outflows'])}")
        print(f"  Net cash flow: {format_currency(cash_flow['net_cash_flow'])}")

    except Exception as e:
        print(f"  Error: {e}")

    # Get account balances
    print("\nFetching detailed account balances...")
    try:
        balances = fetcher.get_account_balances_detailed()

        print(f"\nBank Accounts:")
        for account in balances.get('bank', []):
            print(f"  {account['name']}: {format_currency(account['current_balance'])}")

        print(f"\nCredit Cards:")
        for account in balances.get('credit_card', []):
            print(f"  {account['name']}: {format_currency(account['current_balance'])}")

    except Exception as e:
        print(f"  Error: {e}")


def demo_data_transformation(client: QuickBooksClient):
    """Demonstrate data transformation"""
    print_section("5. Data Transformation")

    print("Fetching transactions and transforming to Finly format...")

    try:
        # Get QuickBooks transactions
        qb_transactions = client.get_transactions(days=90)

        # Transform to Finly format
        transformer = QuickBooksTransformer()
        finly_transactions = transformer.transform_transactions(qb_transactions)

        print(f"\n✓ Transformed {len(finly_transactions)} transactions")

        # Show sample
        if finly_transactions:
            print(f"\nSample transformed transaction:")
            sample = finly_transactions[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")

        # Get summary
        summary = transformer.get_historical_summary(finly_transactions)

        print(f"\nHistorical Summary:")
        print(f"  Total transactions: {summary['total_transactions']}")
        print(f"  Total inflows: {format_currency(summary['total_inflows'])}")
        print(f"  Total outflows: {format_currency(summary['total_outflows'])}")
        print(f"  Net cash flow: {format_currency(summary['net_cash_flow'])}")
        print(f"  Date range: {summary['date_range']['days']} days")

        # Category breakdown
        print(f"\nTop categories:")
        categories = summary.get('categories', {})
        sorted_categories = sorted(
            categories.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:5]

        for category, data in sorted_categories:
            print(f"  {category}: {format_currency(data['total'])} ({data['count']} txns)")

    except Exception as e:
        print(f"✗ Error: {e}")


def demo_export_data(client: QuickBooksClient):
    """Demonstrate exporting data"""
    print_section("6. Exporting Data")

    print("Fetching and exporting data...")

    try:
        # Get transactions
        qb_transactions = client.get_transactions(days=90)

        # Transform
        transformer = QuickBooksTransformer()
        finly_transactions = transformer.transform_transactions(qb_transactions)

        # Export to JSON
        output_file = Path(__file__).parent / 'outputs' / 'quickbooks_export.json'
        output_file.parent.mkdir(exist_ok=True)

        export_data = {
            'export_date': datetime.now().isoformat(),
            'company_id': client.company_id,
            'transaction_count': len(finly_transactions),
            'transactions': finly_transactions[:100],  # Export first 100
            'summary': transformer.get_historical_summary(finly_transactions)
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n✓ Data exported to: {output_file}")
        print(f"  Transactions exported: {min(len(finly_transactions), 100)}")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Main demo function"""
    print("\n" + "="*70)
    print("  FINLY - QuickBooks Integration Demo")
    print("="*70)

    # Step 1: Authentication
    auth, realm_id = demo_authentication()

    if not auth:
        print("\n✗ Authentication failed. Cannot proceed.")
        print("\nTo set up QuickBooks credentials:")
        print("  1. Visit https://developer.intuit.com/")
        print("  2. Create an app and get Client ID & Secret")
        print("  3. Add to .env file:")
        print("     QB_CLIENT_ID=your_client_id")
        print("     QB_CLIENT_SECRET=your_client_secret")
        return

    # Initialize client
    client = QuickBooksClient(auth=auth, company_id=realm_id)

    # Step 2: Fetch basic data
    demo_fetch_data(client)

    # Step 3: Fetch transactions
    demo_fetch_transactions(client)

    # Step 4: Enhanced data fetching
    demo_enhanced_data_fetcher(client)

    # Step 5: Data transformation
    demo_data_transformation(client)

    # Step 6: Export data
    demo_export_data(client)

    # Summary
    print_section("Demo Complete!")

    print("You've successfully:")
    print("  ✓ Authenticated with QuickBooks")
    print("  ✓ Fetched company and account data")
    print("  ✓ Retrieved transaction history")
    print("  ✓ Used enhanced data fetching features")
    print("  ✓ Transformed data to Finly format")
    print("  ✓ Exported data to JSON")

    print(f"\nNext steps:")
    print("  - Use this data with the forecasting engine")
    print("  - View in the dashboard")
    print("  - Generate cash flow forecasts")

    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
