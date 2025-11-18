"""
Hybrid Ensemble Forecasting Engine
Combines ARIMA, Regression, and XGBoost models
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict
import warnings
warnings.filterwarnings('ignore')

from .arima_model import CategoryARIMAForecaster
from .regression_model import MultiCategoryRegressionForecaster
from .xgboost_model import MultiCategoryXGBoostForecaster


class HybridEnsembleForecaster:
    """
    Hybrid ensemble combining three forecasting approaches:
    1. ARIMA - Time series analysis
    2. Regression - Linear patterns with feature engineering
    3. XGBoost - Non-linear machine learning

    Uses intelligent weighted averaging based on historical performance
    """

    def __init__(self,
                 enable_arima: bool = True,
                 enable_regression: bool = True,
                 enable_xgboost: bool = True,
                 weights: Optional[Dict[str, float]] = None):
        """
        Initialize hybrid ensemble forecaster

        Args:
            enable_arima: Enable ARIMA model
            enable_regression: Enable regression model
            enable_xgboost: Enable XGBoost model
            weights: Custom weights for ensemble (default: equal weights)
        """
        self.enable_arima = enable_arima
        self.enable_regression = enable_regression
        self.enable_xgboost = enable_xgboost

        # Initialize models
        self.arima_forecaster = CategoryARIMAForecaster() if enable_arima else None
        self.regression_forecaster = MultiCategoryRegressionForecaster() if enable_regression else None
        self.xgboost_forecaster = MultiCategoryXGBoostForecaster() if enable_xgboost else None

        # Model weights (default: equal)
        self.weights = weights or {'arima': 0.33, 'regression': 0.33, 'xgboost': 0.34}
        self._normalize_weights()

        # Storage
        self.category_performance = {}
        self.fitted_categories = set()

    def _normalize_weights(self):
        """Normalize weights to sum to 1.0"""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def fit_category(self,
                    transactions_df: pd.DataFrame,
                    category: str,
                    frequency: str = 'W') -> Dict[str, bool]:
        """
        Fit all enabled models for a category

        Args:
            transactions_df: Transaction DataFrame
            category: Category name
            frequency: Time frequency

        Returns:
            Dictionary of fit results for each model
        """
        results = {}

        # Fit ARIMA
        if self.enable_arima:
            try:
                success = self.arima_forecaster.fit_category(
                    transactions_df, category, frequency
                )
                results['arima'] = success
            except Exception as e:
                print(f"ARIMA fit failed for {category}: {e}")
                results['arima'] = False

        # Fit Regression
        if self.enable_regression:
            try:
                success = self.regression_forecaster.fit_category(
                    transactions_df, category, frequency
                )
                results['regression'] = success
            except Exception as e:
                print(f"Regression fit failed for {category}: {e}")
                results['regression'] = False

        # Fit XGBoost
        if self.enable_xgboost:
            try:
                success = self.xgboost_forecaster.fit_category(
                    transactions_df, category, frequency
                )
                results['xgboost'] = success
            except Exception as e:
                print(f"XGBoost fit failed for {category}: {e}")
                results['xgboost'] = False

        # Mark as fitted if at least one model succeeded
        if any(results.values()):
            self.fitted_categories.add(category)

        return results

    def fit_all_categories(self,
                          transactions_df: pd.DataFrame,
                          categories: List[str],
                          frequency: str = 'W') -> Dict[str, Dict[str, bool]]:
        """
        Fit all models for all categories

        Args:
            transactions_df: Transaction DataFrame
            categories: List of categories
            frequency: Time frequency

        Returns:
            Nested dictionary of fit results
        """
        all_results = {}

        for category in categories:
            results = self.fit_category(transactions_df, category, frequency)
            all_results[category] = results

        return all_results

    def calculate_model_accuracy(self,
                                 category: str,
                                 ts_data: pd.Series,
                                 test_size: int = 4) -> Dict[str, float]:
        """
        Calculate historical accuracy for each model using walk-forward validation

        Args:
            category: Category name
            ts_data: Historical time series
            test_size: Number of periods to use for testing

        Returns:
            Dictionary of MAE scores for each model
        """
        if len(ts_data) < test_size + 12:
            return {}

        scores = {}
        train_data = ts_data[:-test_size]
        test_data = ts_data[-test_size:]

        # Test ARIMA
        if self.enable_arima and category in self.arima_forecaster.category_models:
            try:
                forecaster = self.arima_forecaster.category_models[category]
                forecast, _, _ = forecaster.forecast(test_size)
                mae = np.mean(np.abs(test_data.values - forecast))
                scores['arima'] = mae
            except:
                pass

        # Test Regression
        if self.enable_regression and category in self.regression_forecaster.category_models:
            try:
                forecaster = self.regression_forecaster.category_models[category]
                ts = self.regression_forecaster.category_data[category][:-test_size]
                forecast, _, _ = forecaster.forecast(ts, test_size)
                mae = np.mean(np.abs(test_data.values - forecast))
                scores['regression'] = mae
            except:
                pass

        # Test XGBoost
        if self.enable_xgboost and category in self.xgboost_forecaster.category_models:
            try:
                forecaster = self.xgboost_forecaster.category_models[category]
                ts = self.xgboost_forecaster.category_data[category][:-test_size]
                forecast, _, _ = forecaster.forecast(ts, test_size)
                mae = np.mean(np.abs(test_data.values - forecast))
                scores['xgboost'] = mae
            except:
                pass

        return scores

    def calculate_adaptive_weights(self,
                                   category: str,
                                   ts_data: pd.Series) -> Dict[str, float]:
        """
        Calculate adaptive weights based on historical performance

        Args:
            category: Category name
            ts_data: Historical time series

        Returns:
            Dictionary of weights for each model
        """
        # Get accuracy scores (MAE - lower is better)
        scores = self.calculate_model_accuracy(category, ts_data)

        if not scores:
            # No scores available, use default weights
            return self.weights.copy()

        # Convert MAE to weights (inverse of error)
        # Add small constant to avoid division by zero
        inverse_errors = {model: 1 / (mae + 1e-10) for model, mae in scores.items()}

        # Normalize to sum to 1.0
        total = sum(inverse_errors.values())
        adaptive_weights = {model: weight / total for model, weight in inverse_errors.items()}

        return adaptive_weights

    def forecast_category(self,
                         category: str,
                         steps: int,
                         use_adaptive_weights: bool = True) -> Optional[dict]:
        """
        Generate ensemble forecast for category

        Args:
            category: Category name
            steps: Steps ahead
            use_adaptive_weights: Use adaptive weights based on performance

        Returns:
            Forecast dictionary with ensemble predictions
        """
        if category not in self.fitted_categories:
            return None

        forecasts = {}
        lower_bounds = {}
        upper_bounds = {}

        # Get ARIMA forecast
        if self.enable_arima:
            result = self.arima_forecaster.forecast_category(category, steps)
            if result:
                forecasts['arima'] = np.array(result['forecast'])
                lower_bounds['arima'] = np.array(result['lower_bound'])
                upper_bounds['arima'] = np.array(result['upper_bound'])

        # Get Regression forecast
        if self.enable_regression:
            result = self.regression_forecaster.forecast_category(category, steps)
            if result:
                forecasts['regression'] = np.array(result['forecast'])
                lower_bounds['regression'] = np.array(result['lower_bound'])
                upper_bounds['regression'] = np.array(result['upper_bound'])

        # Get XGBoost forecast
        if self.enable_xgboost:
            result = self.xgboost_forecaster.forecast_category(category, steps)
            if result:
                forecasts['xgboost'] = np.array(result['forecast'])
                lower_bounds['xgboost'] = np.array(result['lower_bound'])
                upper_bounds['xgboost'] = np.array(result['upper_bound'])

        if not forecasts:
            return None

        # Determine weights
        if use_adaptive_weights:
            # Get historical data for adaptive weights
            if self.enable_arima and category in self.arima_forecaster.category_data:
                ts_data = self.arima_forecaster.category_data[category]
            elif self.enable_regression and category in self.regression_forecaster.category_data:
                ts_data = self.regression_forecaster.category_data[category]
            else:
                ts_data = self.xgboost_forecaster.category_data[category]

            weights = self.calculate_adaptive_weights(category, ts_data)
        else:
            weights = self.weights.copy()

        # Ensemble forecasts using weighted average
        ensemble_forecast = np.zeros(steps)
        ensemble_lower = np.zeros(steps)
        ensemble_upper = np.zeros(steps)

        for model, forecast in forecasts.items():
            weight = weights.get(model, 0)
            ensemble_forecast += weight * forecast
            ensemble_lower += weight * lower_bounds[model]
            ensemble_upper += weight * upper_bounds[model]

        # Store individual model forecasts for comparison
        individual_forecasts = {
            model: forecast.tolist()
            for model, forecast in forecasts.items()
        }

        return {
            'forecast': ensemble_forecast.tolist(),
            'lower_bound': ensemble_lower.tolist(),
            'upper_bound': ensemble_upper.tolist(),
            'category': category,
            'model_type': 'Hybrid Ensemble',
            'weights': weights,
            'individual_forecasts': individual_forecasts,
            'models_used': list(forecasts.keys())
        }

    def forecast_all_categories(self,
                               steps: int,
                               use_adaptive_weights: bool = True) -> dict:
        """
        Generate ensemble forecasts for all fitted categories

        Args:
            steps: Steps ahead
            use_adaptive_weights: Use adaptive weights

        Returns:
            Dictionary of ensemble forecasts
        """
        forecasts = {}

        for category in self.fitted_categories:
            forecast_result = self.forecast_category(category, steps, use_adaptive_weights)
            if forecast_result:
                forecasts[category] = forecast_result

        return forecasts

    def compare_models(self,
                      category: str,
                      steps: int = 13) -> Optional[pd.DataFrame]:
        """
        Compare all model forecasts side by side

        Args:
            category: Category name
            steps: Steps ahead

        Returns:
            DataFrame with model comparisons
        """
        if category not in self.fitted_categories:
            return None

        result = self.forecast_category(category, steps, use_adaptive_weights=False)
        if not result:
            return None

        # Create comparison DataFrame
        comparison = pd.DataFrame({
            'Week': range(1, steps + 1),
            'Ensemble': result['forecast']
        })

        # Add individual model forecasts
        for model, forecast in result['individual_forecasts'].items():
            comparison[model.upper()] = forecast

        return comparison

    def get_model_summary(self) -> dict:
        """Get summary of the ensemble"""
        return {
            'model_type': 'Hybrid Ensemble',
            'models_enabled': {
                'arima': self.enable_arima,
                'regression': self.enable_regression,
                'xgboost': self.enable_xgboost
            },
            'default_weights': self.weights,
            'fitted_categories': list(self.fitted_categories),
            'n_categories': len(self.fitted_categories)
        }


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("  Hybrid Ensemble Forecasting - Example Usage")
    print("=" * 70 + "\n")

    # Load data
    df = pd.read_csv('data/transactions.csv')
    print(f"✓ Loaded {len(df)} transactions\n")

    # Initialize hybrid ensemble
    print("Initializing Hybrid Ensemble Forecaster...")
    ensemble = HybridEnsembleForecaster(
        enable_arima=True,
        enable_regression=True,
        enable_xgboost=True
    )
    print("✓ Ensemble initialized with 3 models\n")

    # Fit for revenue category
    print("Fitting models for 'revenue' category...")
    results = ensemble.fit_category(df, 'revenue', frequency='W')

    print("\nModel Fit Results:")
    for model, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {model.upper():12} {status}")

    # Generate ensemble forecast
    if any(results.values()):
        print("\nGenerating 13-week ensemble forecast...")
        forecast = ensemble.forecast_category('revenue', steps=13)

        if forecast:
            print("\n" + "=" * 70)
            print("  13-Week Revenue Forecast (Hybrid Ensemble)")
            print("=" * 70)
            print(f"\nModels Used: {', '.join([m.upper() for m in forecast['models_used']])}")
            print(f"\nModel Weights:")
            for model, weight in forecast['weights'].items():
                print(f"  {model.upper():12} {weight:.2%}")

            print(f"\nEnsemble Forecast:")
            print(f"  Week 1:  ${forecast['forecast'][0]:,.2f}")
            print(f"  Week 7:  ${forecast['forecast'][6]:,.2f}")
            print(f"  Week 13: ${forecast['forecast'][-1]:,.2f}")

            print(f"\nConfidence Interval (Week 1):")
            print(f"  Lower: ${forecast['lower_bound'][0]:,.2f}")
            print(f"  Upper: ${forecast['upper_bound'][0]:,.2f}")

            # Model comparison
            print("\n" + "=" * 70)
            print("  Model Comparison (First 5 Weeks)")
            print("=" * 70)
            comparison = ensemble.compare_models('revenue', steps=13)
            if comparison is not None:
                print(comparison.head().to_string(index=False))

    print("\n" + "=" * 70)
    print("  Hybrid Ensemble Demo Complete!")
    print("=" * 70 + "\n")
