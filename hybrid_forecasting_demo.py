"""
Hybrid Forecasting Engine - Quick Demo
Demonstrates ARIMA, Regression, XGBoost, and Hybrid Ensemble
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.forecasting.ml_models import (
    CategoryARIMAForecaster,
    MultiCategoryRegressionForecaster,
    MultiCategoryXGBoostForecaster,
    HybridEnsembleForecaster
)


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_forecast_summary(forecast, category):
    """Print forecast summary"""
    print(f"\n{category.upper()} - 13-Week Forecast:")
    print(f"  Model: {forecast.get('model_info', {}).get('model_type', forecast.get('model_type', 'N/A'))}")

    if 'weights' in forecast:
        print(f"  Weights:")
        for model, weight in forecast['weights'].items():
            print(f"    {model.upper():12} {weight:.1%}")

    if 'models_used' in forecast:
        print(f"  Models: {', '.join([m.upper() for m in forecast['models_used']])}")

    print(f"\n  Forecast Values:")
    print(f"    Week 1:  ${forecast['forecast'][0]:>12,.2f}")
    print(f"    Week 7:  ${forecast['forecast'][6]:>12,.2f}")
    print(f"    Week 13: ${forecast['forecast'][12]:>12,.2f}")

    print(f"\n  Confidence Interval (Week 1):")
    print(f"    Lower: ${forecast['lower_bound'][0]:>12,.2f}")
    print(f"    Upper: ${forecast['upper_bound'][0]:>12,.2f}")


def demo_individual_models():
    """Demo individual models (ARIMA, Regression, XGBoost)"""
    print_header("PART 1: Individual Model Demos")

    # Load sample data
    print("Loading sample data...")
    df = pd.read_csv('data/transactions.csv')
    print(f"✓ Loaded {len(df)} transactions\n")

    # Demo 1: ARIMA
    print("-" * 70)
    print("Demo 1: ARIMA Time Series Forecasting")
    print("-" * 70)

    arima = CategoryARIMAForecaster()
    print("Fitting ARIMA for 'revenue' category...")
    success = arima.fit_category(df, 'revenue', frequency='W')

    if success:
        print("✓ Model fitted successfully")
        forecast = arima.forecast_category('revenue', steps=13)
        if forecast:
            print_forecast_summary(forecast, 'revenue')

    # Demo 2: Regression
    print("\n" + "-" * 70)
    print("Demo 2: Regression with Feature Engineering")
    print("-" * 70)

    regression = MultiCategoryRegressionForecaster(model_type='ridge')
    print("Fitting Regression for 'revenue' category...")
    success = regression.fit_category(df, 'revenue', frequency='W')

    if success:
        print("✓ Model fitted successfully")
        forecast = regression.forecast_category('revenue', steps=13)
        if forecast:
            print_forecast_summary(forecast, 'revenue')

    # Demo 3: XGBoost
    print("\n" + "-" * 70)
    print("Demo 3: XGBoost Machine Learning")
    print("-" * 70)

    xgboost = MultiCategoryXGBoostForecaster(n_estimators=100, max_depth=5)
    print("Fitting XGBoost for 'revenue' category...")
    success = xgboost.fit_category(df, 'revenue', frequency='W')

    if success:
        print("✓ Model fitted successfully")
        forecast = xgboost.forecast_category('revenue', steps=13)
        if forecast:
            print_forecast_summary(forecast, 'revenue')


def demo_hybrid_ensemble():
    """Demo hybrid ensemble combining all models"""
    print_header("PART 2: Hybrid Ensemble (All Models Combined)")

    # Load sample data
    df = pd.read_csv('data/transactions.csv')

    # Initialize hybrid ensemble
    print("Initializing Hybrid Ensemble...")
    print("  • ARIMA enabled")
    print("  • Regression enabled")
    print("  • XGBoost enabled\n")

    ensemble = HybridEnsembleForecaster(
        enable_arima=True,
        enable_regression=True,
        enable_xgboost=True
    )

    # Fit for revenue
    print("Fitting all models for 'revenue' category...")
    results = ensemble.fit_category(df, 'revenue', frequency='W')

    print("\nModel Fit Results:")
    for model, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {model.upper():12} {status}")

    # Generate ensemble forecast
    if any(results.values()):
        print("\nGenerating 13-week ensemble forecast...")
        forecast = ensemble.forecast_category('revenue', steps=13, use_adaptive_weights=True)

        if forecast:
            print_forecast_summary(forecast, 'revenue')

            # Show individual model predictions
            if 'individual_forecasts' in forecast:
                print("\n  Individual Model Predictions (Week 1):")
                for model, predictions in forecast['individual_forecasts'].items():
                    print(f"    {model.upper():12} ${predictions[0]:>12,.2f}")


def demo_multi_category():
    """Demo forecasting multiple categories"""
    print_header("PART 3: Multi-Category Forecasting")

    # Load sample data
    df = pd.read_csv('data/transactions.csv')

    # Initialize ensemble
    ensemble = HybridEnsembleForecaster(
        enable_arima=True,
        enable_regression=True,
        enable_xgboost=True
    )

    # Get top categories by transaction count
    category_counts = df['category'].value_counts()
    top_categories = category_counts.head(5).index.tolist()

    print(f"Forecasting top {len(top_categories)} categories:")
    for cat in top_categories:
        print(f"  • {cat}")

    # Fit all categories
    print("\nFitting models...")
    fit_results = ensemble.fit_all_categories(df, top_categories, frequency='W')

    # Generate forecasts
    print("\nGenerating 13-week forecasts...\n")
    forecasts = ensemble.forecast_all_categories(steps=13, use_adaptive_weights=True)

    # Summary table
    print("-" * 70)
    print(f"{'Category':<20} {'Week 1':>15} {'Week 13':>15} {'Models':<20}")
    print("-" * 70)

    for category, forecast in forecasts.items():
        week_1 = forecast['forecast'][0]
        week_13 = forecast['forecast'][12]
        models = ', '.join([m.upper()[:3] for m in forecast['models_used']])

        print(f"{category:<20} ${week_1:>14,.2f} ${week_13:>14,.2f} {models:<20}")

    print("-" * 70)


def demo_model_comparison():
    """Demo comparing models side-by-side"""
    print_header("PART 4: Model Comparison")

    # Load sample data
    df = pd.read_csv('data/transactions.csv')

    # Initialize ensemble
    ensemble = HybridEnsembleForecaster(
        enable_arima=True,
        enable_regression=True,
        enable_xgboost=True
    )

    # Fit revenue category
    print("Fitting all models for 'revenue' category...")
    results = ensemble.fit_category(df, 'revenue', frequency='W')

    if any(results.values()):
        # Compare models
        print("\nGenerating model comparison...\n")
        comparison = ensemble.compare_models('revenue', steps=13)

        if comparison is not None:
            print("Week-by-Week Comparison (First 5 weeks):")
            print(comparison.head().to_string(index=False))

            print("\n\nWeek-by-Week Comparison (Last 5 weeks):")
            print(comparison.tail().to_string(index=False))

            # Calculate differences
            if 'ARIMA' in comparison.columns and 'Ensemble' in comparison.columns:
                avg_diff = abs(comparison['ARIMA'] - comparison['Ensemble']).mean()
                print(f"\nAverage difference between ARIMA and Ensemble: ${avg_diff:,.2f}")


def main():
    """Main demo execution"""
    print("\n" + "="*70)
    print("  HYBRID FORECASTING ENGINE - COMPREHENSIVE DEMO")
    print("="*70)
    print("\n  This demo showcases:")
    print("    • Individual models (ARIMA, Regression, XGBoost)")
    print("    • Hybrid ensemble combining all models")
    print("    • Multi-category forecasting")
    print("    • Model comparison")

    try:
        # Part 1: Individual models
        demo_individual_models()

        # Part 2: Hybrid ensemble
        demo_hybrid_ensemble()

        # Part 3: Multi-category
        demo_multi_category()

        # Part 4: Model comparison
        demo_model_comparison()

        # Final summary
        print_header("DEMO COMPLETE!")

        print("✅ Successfully demonstrated:")
        print("  • ARIMA time series forecasting")
        print("  • Regression with feature engineering")
        print("  • XGBoost machine learning")
        print("  • Hybrid ensemble (weighted averaging)")
        print("  • Multi-category forecasting")
        print("  • Model comparison\n")

        print("📚 For more information:")
        print("  • See docs/HYBRID_FORECASTING.md")
        print("  • Run test_hybrid_realistic.py for validation")
        print("  • Check src/forecasting/ml_models/ for implementation\n")

    except FileNotFoundError:
        print("\n❌ Error: data/transactions.csv not found")
        print("   Please run: python generate_sample_data.py")
        print("   Then try this demo again.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   See docs/HYBRID_FORECASTING.md for troubleshooting\n")


if __name__ == "__main__":
    main()
