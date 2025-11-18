"""
QuickBooks Integration Test (No Credentials Required)
Tests the QuickBooks module with mock data
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.quickbooks import QuickBooksTransformer


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_data_transformation():
    """Test QuickBooks to Finly data transformation"""
    print_section("QuickBooks Data Transformation Test")

    # Create mock QuickBooks transactions
    mock_qb_transactions = [
        # Invoice
        {
            'TxnDate': '2025-01-15',
            'TotalAmt': 5000.00,
            'DocNumber': 'INV-001',
            'CustomerRef': {'name': 'Acme Corp'},
            'Id': '123',
            'domain': 'Invoice'
        },
        # Payment
        {
            'TxnDate': '2025-01-20',
            'TotalAmt': 5000.00,
            'CustomerRef': {'name': 'Acme Corp'},
            'Id': '124',
            'domain': 'Payment'
        },
        # Bill
        {
            'TxnDate': '2025-01-10',
            'TotalAmt': 2000.00,
            'VendorRef': {'name': 'Office Supplies Co'},
            'Id': '125',
            'domain': 'Bill',
            'Line': [
                {
                    'DetailType': 'AccountBasedExpenseLineDetail',
                    'Amount': 2000.00,
                    'AccountBasedExpenseLineDetail': {
                        'AccountRef': {'name': 'Office Supplies'}
                    }
                }
            ]
        },
        # Expense
        {
            'TxnDate': '2025-01-12',
            'TotalAmt': 1500.00,
            'EntityRef': {'name': 'Tech Vendor'},
            'Id': '126',
            'domain': 'Purchase',
            'Line': [
                {
                    'DetailType': 'AccountBasedExpenseLineDetail',
                    'Amount': 1500.00,
                    'AccountBasedExpenseLineDetail': {
                        'AccountRef': {'name': 'Software'}
                    }
                }
            ]
        }
    ]

    print("Mock QuickBooks Transactions:")
    print(f"  Total: {len(mock_qb_transactions)} transactions\n")

    # Transform to Finly format
    transformer = QuickBooksTransformer()
    finly_transactions = transformer.transform_transactions(mock_qb_transactions)

    print(f"✓ Transformed to Finly format")
    print(f"  Total: {len(finly_transactions)} transactions\n")

    # Display transformed transactions
    print("Transformed Transactions:")
    for i, txn in enumerate(finly_transactions, 1):
        print(f"\n  Transaction {i}:")
        print(f"    Date: {txn['date']}")
        print(f"    Amount: ${txn['amount']:,.2f}")
        print(f"    Category: {txn['category']}")
        print(f"    Type: {txn['transaction_type']}")
        print(f"    Description: {txn['description']}")
        if txn['customer']:
            print(f"    Customer: {txn['customer']}")
        if txn['vendor']:
            print(f"    Vendor: {txn['vendor']}")

    # Get summary
    summary = transformer.get_historical_summary(finly_transactions)

    print(f"\n{'='*70}")
    print("Historical Summary:")
    print(f"{'='*70}")
    print(f"  Total transactions: {summary['total_transactions']}")
    print(f"  Total inflows: ${summary['total_inflows']:,.2f}")
    print(f"  Total outflows: ${summary['total_outflows']:,.2f}")
    print(f"  Net cash flow: ${summary['net_cash_flow']:,.2f}")

    print(f"\nCategory Breakdown:")
    for category, data in summary['categories'].items():
        print(f"  {category}:")
        print(f"    Count: {data['count']}")
        print(f"    Total: ${data['total']:,.2f}")


def test_category_mapping():
    """Test category mapping functionality"""
    print_section("Category Mapping Test")

    transformer = QuickBooksTransformer()

    test_categories = [
        'Sales',
        'Service Income',
        'Payroll Expenses',
        'Rent Expense',
        'Marketing',
        'Software',
        'Utilities',
        'Unknown Category'
    ]

    print("Testing category mappings:")
    for qb_category in test_categories:
        finly_category = transformer._map_category(qb_category)
        print(f"  {qb_category:25} → {finly_category.value}")


def test_custom_category_mapping():
    """Test custom category mapping"""
    print_section("Custom Category Mapping Test")

    from src.quickbooks.transformer import CashFlowCategory

    # Create custom mappings
    custom_map = {
        'Consulting Income': CashFlowCategory.REVENUE,
        'Cloud Services': CashFlowCategory.TECHNOLOGY,
        'Employee Benefits': CashFlowCategory.PAYROLL
    }

    transformer = QuickBooksTransformer(custom_category_map=custom_map)

    print("Testing custom mappings:")
    for qb_cat, expected_cat in custom_map.items():
        mapped = transformer._map_category(qb_cat)
        status = "✓" if mapped == expected_cat else "✗"
        print(f"  {status} {qb_cat} → {mapped.value}")


def test_date_parsing():
    """Test date parsing"""
    print_section("Date Parsing Test")

    transformer = QuickBooksTransformer()

    test_dates = [
        '2025-01-15',
        '2024-12-31',
        '2025-06-30',
    ]

    print("Testing date parsing:")
    for date_str in test_dates:
        parsed = transformer._parse_date(date_str)
        print(f"  {date_str} → {parsed}")


def test_transaction_types():
    """Test different transaction types"""
    print_section("Transaction Type Detection Test")

    transformer = QuickBooksTransformer()

    # Test invoice transformation
    invoice = {
        'TxnDate': '2025-01-15',
        'TotalAmt': 1000.00,
        'DocNumber': 'INV-001',
        'CustomerRef': {'name': 'Test Customer'},
        'Id': '1',
        'domain': 'Invoice'
    }

    result = transformer._transform_invoice(invoice)
    print("Invoice transformation:")
    print(f"  Input: QB Invoice")
    print(f"  Output: {result[0]['transaction_type']} - {result[0]['category']}")

    # Test payment transformation
    payment = {
        'TxnDate': '2025-01-20',
        'TotalAmt': 1000.00,
        'CustomerRef': {'name': 'Test Customer'},
        'Id': '2',
        'domain': 'Payment'
    }

    result = transformer._transform_payment(payment)
    print(f"\nPayment transformation:")
    print(f"  Input: QB Payment")
    print(f"  Output: {result[0]['transaction_type']} - {result[0]['category']}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("  FINLY - QuickBooks Integration Tests (No Credentials Required)")
    print("="*70)

    tests = [
        ("Data Transformation", test_data_transformation),
        ("Category Mapping", test_category_mapping),
        ("Custom Mappings", test_custom_category_mapping),
        ("Date Parsing", test_date_parsing),
        ("Transaction Types", test_transaction_types)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, "✓ PASSED"))
        except Exception as e:
            results.append((test_name, f"✗ FAILED: {e}"))

    # Summary
    print_section("Test Results Summary")

    for test_name, result in results:
        print(f"  {result:20} - {test_name}")

    passed = sum(1 for _, r in results if "✓" in r)
    total = len(results)

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  ✓ All tests passed!")
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed")

    print("\n" + "="*70)
    print("Next Steps:")
    print("  1. Set up QuickBooks credentials (see docs/QUICKBOOKS_SETUP.md)")
    print("  2. Run quickbooks_demo.py to test with real data")
    print("  3. Use the dashboard to visualize forecasts")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()
