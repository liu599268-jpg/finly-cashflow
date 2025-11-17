"""
Comprehensive Test Suite for Finly-Prototype
Tests all modules and integration
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def print_header(title: str):
    """Print test section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_test_result(test_name: str, passed: bool, message: str = ""):
    """Print individual test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status:10}{reset} - {test_name}")
    if message and not passed:
        print(f"           {message}")


class TestResults:
    """Track test results"""

    def __init__(self):
        self.tests = []
        self.current_section = ""

    def add_test(self, name: str, passed: bool, message: str = ""):
        """Add test result"""
        self.tests.append({
            'section': self.current_section,
            'name': name,
            'passed': passed,
            'message': message
        })
        print_test_result(name, passed, message)

    def set_section(self, section: str):
        """Set current test section"""
        self.current_section = section

    def get_summary(self):
        """Get test summary"""
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t['passed'])
        failed = total - passed
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }

    def print_summary(self):
        """Print test summary"""
        summary = self.get_summary()

        print_header("TEST SUMMARY")

        print(f"Total Tests:  {summary['total']}")
        print(f"Passed:       {summary['passed']} (\033[92m{summary['pass_rate']:.1f}%\033[0m)")
        print(f"Failed:       {summary['failed']}")

        if summary['failed'] > 0:
            print(f"\n\033[91mFailed Tests:\033[0m")
            for test in self.tests:
                if not test['passed']:
                    print(f"  - {test['section']}: {test['name']}")
                    if test['message']:
                        print(f"    {test['message']}")

        return summary['failed'] == 0


def test_quickbooks_module(results: TestResults):
    """Test QuickBooks integration module"""
    print_header("1. QuickBooks Module Tests")
    results.set_section("QuickBooks")

    # Test imports
    try:
        from src.quickbooks import (
            QuickBooksAuth,
            QuickBooksClient,
            QuickBooksTransformer,
            QuickBooksDataFetcher,
            QuickBooksOAuthServer,
            authenticate_quickbooks
        )
        results.add_test("Import QuickBooks modules", True)
    except Exception as e:
        results.add_test("Import QuickBooks modules", False, str(e))
        return

    # Test auth initialization
    try:
        auth = QuickBooksAuth(environment='sandbox')
        results.add_test("Initialize QuickBooksAuth", True)
    except Exception as e:
        results.add_test("Initialize QuickBooksAuth", False, str(e))

    # Test transformer
    try:
        transformer = QuickBooksTransformer()

        # Mock QuickBooks transaction
        mock_txn = {
            'TxnDate': '2025-01-15',
            'TotalAmt': 1000.00,
            'DocNumber': 'INV-001',
            'CustomerRef': {'name': 'Test Customer'},
            'Id': '123',
            'domain': 'Invoice'
        }

        result = transformer._transform_invoice(mock_txn)

        assert len(result) == 1
        assert result[0]['amount'] == 1000.00
        assert result[0]['transaction_type'] == 'inflow'
        assert result[0]['category'] == 'revenue'

        results.add_test("Transform QuickBooks invoice", True)
    except Exception as e:
        results.add_test("Transform QuickBooks invoice", False, str(e))

    # Test category mapping
    try:
        mapped = transformer._map_category('Payroll Expenses')
        assert mapped.value == 'payroll'

        mapped = transformer._map_category('Software')
        assert mapped.value == 'technology'

        results.add_test("Category mapping", True)
    except Exception as e:
        results.add_test("Category mapping", False, str(e))

    # Test date parsing
    try:
        parsed = transformer._parse_date('2025-01-15')
        assert '2025-01-15' in parsed
        results.add_test("Date parsing", True)
    except Exception as e:
        results.add_test("Date parsing", False, str(e))


def test_forecasting_module(results: TestResults):
    """Test forecasting engine"""
    print_header("2. Forecasting Engine Tests")
    results.set_section("Forecasting")

    # Test imports
    try:
        from src.forecasting import (
            ForecastEngine,
            ForecastValidator,
            CategoryPredictor,
            Transaction,
            HistoricalData,
            CashFlowCategory,
            TransactionType
        )
        results.add_test("Import forecasting modules", True)
    except Exception as e:
        results.add_test("Import forecasting modules", False, str(e))
        return

    # Test data models
    try:
        from src.forecasting.models import Transaction, TransactionType, CashFlowCategory

        txn = Transaction(
            date=datetime.now(),
            amount=1000.0,
            category=CashFlowCategory.REVENUE,
            transaction_type=TransactionType.INFLOW,
            description="Test transaction"
        )

        assert txn.amount == 1000.0
        assert txn.category == CashFlowCategory.REVENUE

        results.add_test("Create Transaction object", True)
    except Exception as e:
        results.add_test("Create Transaction object", False, str(e))

    # Test sample data generation
    try:
        from utils.sample_data import SampleDataGenerator

        generator = SampleDataGenerator(seed=42)
        historical = generator.generate_transactions(num_weeks=12)

        assert len(historical.transactions) > 0
        assert historical.opening_balance == 500000

        results.add_test("Generate sample data", True)
    except Exception as e:
        results.add_test("Generate sample data", False, str(e))
        return

    # Test forecast engine
    try:
        engine = ForecastEngine(use_ensemble=False)

        forecast = engine.generate_forecast(
            historical_data=historical,
            company_name="Test Company",
            weeks_ahead=13
        )

        assert len(forecast.forecast_points) == 13
        assert forecast.company_name == "Test Company"
        assert forecast.current_balance is not None

        results.add_test("Generate 13-week forecast", True)
    except Exception as e:
        results.add_test("Generate 13-week forecast", False, str(e))

    # Test forecast calculations
    try:
        final_balance = forecast.get_final_balance()
        min_balance = forecast.get_minimum_balance()
        weeks_zero = forecast.get_weeks_until_zero()
        burn_rate = forecast.get_average_weekly_burn()

        assert final_balance is not None
        assert min_balance is not None

        results.add_test("Forecast calculations", True)
    except Exception as e:
        results.add_test("Forecast calculations", False, str(e))

    # Test forecast validation
    try:
        validator = ForecastValidator()
        validation = validator.validate_forecast(forecast, historical)

        assert 'is_valid' in validation
        assert 'confidence_score' in validation

        results.add_test("Forecast validation", True)
    except Exception as e:
        results.add_test("Forecast validation", False, str(e))


def test_data_processor(results: TestResults):
    """Test data processing utilities"""
    print_header("3. Data Processor Tests")
    results.set_section("DataProcessor")

    try:
        from src.forecasting.processor import DataProcessor
        from src.forecasting.models import HistoricalData, Transaction, CashFlowCategory, TransactionType
        from datetime import datetime, timedelta

        processor = DataProcessor()

        # Create test data
        transactions = []
        for i in range(30):
            txn = Transaction(
                date=datetime.now() - timedelta(days=30-i),
                amount=1000.0,
                category=CashFlowCategory.REVENUE,
                transaction_type=TransactionType.INFLOW,
                description=f"Test {i}"
            )
            transactions.append(txn)

        historical = HistoricalData(
            transactions=transactions,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            opening_balance=100000
        )

        results.add_test("Create test historical data", True)
    except Exception as e:
        results.add_test("Create test historical data", False, str(e))
        return

    # Test validation
    try:
        is_valid, issues = processor.validate_data(historical)
        assert isinstance(is_valid, bool)
        results.add_test("Validate historical data", True)
    except Exception as e:
        results.add_test("Validate historical data", False, str(e))

    # Test data cleaning
    try:
        cleaned = processor.clean_data(historical)
        assert len(cleaned.transactions) > 0
        results.add_test("Clean data", True)
    except Exception as e:
        results.add_test("Clean data", False, str(e))

    # Test aggregation
    try:
        aggregated = processor.aggregate_by_category(historical, frequency='W')
        assert len(aggregated) > 0
        results.add_test("Aggregate by category", True)
    except Exception as e:
        results.add_test("Aggregate by category", False, str(e))

    # Test statistics
    try:
        stats = processor.get_category_stats(historical, CashFlowCategory.REVENUE)
        assert 'count' in stats
        assert 'mean' in stats
        results.add_test("Calculate category statistics", True)
    except Exception as e:
        results.add_test("Calculate category statistics", False, str(e))


def test_integration(results: TestResults):
    """Test integration between modules"""
    print_header("4. Integration Tests")
    results.set_section("Integration")

    # Test QuickBooks to Forecasting pipeline
    try:
        from src.quickbooks import QuickBooksTransformer
        from src.forecasting import ForecastEngine
        from src.forecasting.models import Transaction, HistoricalData, TransactionType, CashFlowCategory
        from datetime import datetime, timedelta

        # Mock QuickBooks data
        mock_qb_data = [
            {
                'TxnDate': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'TotalAmt': 1000.0 + (i * 100),
                'DocNumber': f'INV-{i}',
                'CustomerRef': {'name': 'Test Customer'},
                'Id': str(i),
                'domain': 'Invoice'
            }
            for i in range(30)
        ]

        # Transform
        transformer = QuickBooksTransformer()
        finly_transactions = transformer.transform_transactions(mock_qb_data)

        assert len(finly_transactions) == 30

        results.add_test("Transform QB data to Finly format", True)
    except Exception as e:
        results.add_test("Transform QB data to Finly format", False, str(e))
        return

    # Create HistoricalData from transformed transactions
    try:
        transactions = []
        for txn_dict in finly_transactions:
            txn = Transaction(
                date=datetime.fromisoformat(txn_dict['date']),
                amount=txn_dict['amount'],
                category=CashFlowCategory(txn_dict['category']),
                transaction_type=TransactionType(txn_dict['transaction_type']),
                description=txn_dict['description']
            )
            transactions.append(txn)

        historical = HistoricalData(
            transactions=transactions,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            opening_balance=500000
        )

        results.add_test("Create HistoricalData from QB data", True)
    except Exception as e:
        results.add_test("Create HistoricalData from QB data", False, str(e))
        return

    # Generate forecast from QB data
    try:
        engine = ForecastEngine()
        forecast = engine.generate_forecast(
            historical_data=historical,
            company_name="Test Company",
            weeks_ahead=13
        )

        assert len(forecast.forecast_points) == 13

        results.add_test("Generate forecast from QB data", True)
    except Exception as e:
        results.add_test("Generate forecast from QB data", False, str(e))

    # Test data export
    try:
        forecast_dict = forecast.to_dict()
        assert 'company_name' in forecast_dict
        assert 'forecast_points' in forecast_dict

        results.add_test("Export forecast to dict", True)
    except Exception as e:
        results.add_test("Export forecast to dict", False, str(e))


def test_sample_data(results: TestResults):
    """Test sample data generator"""
    print_header("5. Sample Data Generator Tests")
    results.set_section("SampleData")

    try:
        from utils.sample_data import SampleDataGenerator

        generator = SampleDataGenerator(seed=42)

        results.add_test("Initialize SampleDataGenerator", True)
    except Exception as e:
        results.add_test("Initialize SampleDataGenerator", False, str(e))
        return

    # Test transaction generation
    try:
        historical = generator.generate_transactions(num_weeks=52)

        assert len(historical.transactions) > 0
        assert historical.start_date < historical.end_date

        results.add_test("Generate 52 weeks of transactions", True)
    except Exception as e:
        results.add_test("Generate 52 weeks of transactions", False, str(e))

    # Test scenario data
    try:
        growth = generator.create_scenario_data('growth', num_weeks=26)
        stable = generator.create_scenario_data('stable', num_weeks=26)
        declining = generator.create_scenario_data('declining', num_weeks=26)

        assert len(growth.transactions) > 0
        assert len(stable.transactions) > 0
        assert len(declining.transactions) > 0

        results.add_test("Generate scenario data", True)
    except Exception as e:
        results.add_test("Generate scenario data", False, str(e))

    # Test AR aging
    try:
        ar_aging = generator.generate_ar_aging(total_ar=200000)

        assert '0-30' in ar_aging
        assert '31-45' in ar_aging
        assert sum(ar_aging.values()) == 200000

        results.add_test("Generate AR aging data", True)
    except Exception as e:
        results.add_test("Generate AR aging data", False, str(e))


def test_file_structure(results: TestResults):
    """Test that all required files exist"""
    print_header("6. File Structure Tests")
    results.set_section("FileStructure")

    required_files = [
        # QuickBooks module
        'src/quickbooks/__init__.py',
        'src/quickbooks/auth.py',
        'src/quickbooks/client.py',
        'src/quickbooks/oauth_server.py',
        'src/quickbooks/transformer.py',
        'src/quickbooks/data_fetcher.py',

        # Forecasting module
        'src/forecasting/__init__.py',
        'src/forecasting/models.py',
        'src/forecasting/engine.py',
        'src/forecasting/predictor.py',
        'src/forecasting/processor.py',

        # Dashboard
        'src/dashboard/__init__.py',
        'src/dashboard/app.py',

        # Utils
        'utils/__init__.py',
        'utils/sample_data.py',

        # Config
        'config/quickbooks.example.yaml',
        'config/models.yaml',

        # Docs
        'docs/QUICKBOOKS_SETUP.md',
        'docs/QUICKBOOKS_INTEGRATION.md',
        'docs/PROJECT_STRUCTURE.md',

        # Root
        'README.md',
        'QUICKSTART.md',
        'requirements.txt',
        '.env.example',
        '.gitignore',
    ]

    project_root = Path(__file__).parent

    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        results.add_test(f"File exists: {file_path}", exists)


def test_configuration(results: TestResults):
    """Test configuration files"""
    print_header("7. Configuration Tests")
    results.set_section("Configuration")

    # Test .env.example
    try:
        env_example = Path(__file__).parent / '.env.example'
        content = env_example.read_text()

        required_vars = ['QB_CLIENT_ID', 'QB_CLIENT_SECRET', 'QB_REDIRECT_URI']
        for var in required_vars:
            assert var in content

        results.add_test("Check .env.example", True)
    except Exception as e:
        results.add_test("Check .env.example", False, str(e))

    # Test models.yaml
    try:
        import yaml

        models_config = Path(__file__).parent / 'config' / 'models.yaml'
        with open(models_config) as f:
            config = yaml.safe_load(f)

        assert 'forecasting' in config
        assert 'arima' in config

        results.add_test("Check models.yaml", True)
    except Exception as e:
        results.add_test("Check models.yaml", False, str(e))


def test_documentation(results: TestResults):
    """Test that documentation files are comprehensive"""
    print_header("8. Documentation Tests")
    results.set_section("Documentation")

    docs = [
        ('README.md', 100),
        ('QUICKSTART.md', 100),
        ('docs/QUICKBOOKS_SETUP.md', 200),
        ('docs/QUICKBOOKS_INTEGRATION.md', 200),
        ('docs/PROJECT_STRUCTURE.md', 200),
    ]

    project_root = Path(__file__).parent

    for doc_file, min_lines in docs:
        try:
            doc_path = project_root / doc_file
            content = doc_path.read_text()
            lines = len(content.split('\n'))

            assert lines >= min_lines

            results.add_test(f"{doc_file} ({lines} lines)", True)
        except Exception as e:
            results.add_test(f"{doc_file}", False, str(e))


def save_test_report(results: TestResults):
    """Save test results to JSON"""
    try:
        output_dir = Path(__file__).parent / 'outputs'
        output_dir.mkdir(exist_ok=True)

        report = {
            'test_date': datetime.now().isoformat(),
            'summary': results.get_summary(),
            'tests': results.tests
        }

        output_file = output_dir / 'test_results.json'
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Test report saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Failed to save test report: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  FINLY-PROTOTYPE - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"\nTest started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = TestResults()

    # Run all test suites
    test_quickbooks_module(results)
    test_forecasting_module(results)
    test_data_processor(results)
    test_integration(results)
    test_sample_data(results)
    test_file_structure(results)
    test_configuration(results)
    test_documentation(results)

    # Print summary
    all_passed = results.print_summary()

    # Save report
    save_test_report(results)

    # Final status
    print("\n" + "="*80)
    if all_passed:
        print("  ✓ ALL TESTS PASSED - SYSTEM READY!")
    else:
        print("  ⚠ SOME TESTS FAILED - REVIEW ABOVE")
    print("="*80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
