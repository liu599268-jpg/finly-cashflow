"""
ARIMA Time Series Forecasting Model
Uses Auto-ARIMA for automatic parameter selection
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.arima.model import ARIMA
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False


class ARIMAForecaster:
    """
    ARIMA-based time series forecaster
    Automatically selects best parameters using grid search
    """

    def __init__(self,
                 p_range: Tuple[int, int] = (0, 3),
                 d_range: Tuple[int, int] = (0, 2),
                 q_range: Tuple[int, int] = (0, 3)):
        """
        Initialize ARIMA forecaster

        Args:
            p_range: Range for AR order (p)
            d_range: Range for differencing order (d)
            q_range: Range for MA order (q)
        """
        if not HAS_STATSMODELS:
            raise ImportError("statsmodels is required for ARIMA forecasting")

        self.p_range = p_range
        self.d_range = d_range
        self.q_range = q_range
        self.best_order = None
        self.model = None
        self.fitted_model = None

    def find_best_order(self, data: pd.Series) -> Tuple[int, int, int]:
        """
        Find best ARIMA order using AIC

        Args:
            data: Time series data

        Returns:
            Best (p, d, q) order
        """
        best_aic = np.inf
        best_order = (1, 1, 1)

        # Grid search over parameter space
        for p in range(self.p_range[0], self.p_range[1] + 1):
            for d in range(self.d_range[0], self.d_range[1] + 1):
                for q in range(self.q_range[0], self.q_range[1] + 1):
                    try:
                        model = ARIMA(data, order=(p, d, q))
                        fitted = model.fit()
                        aic = fitted.aic

                        if aic < best_aic:
                            best_aic = aic
                            best_order = (p, d, q)
                    except:
                        continue

        return best_order

    def fit(self, data: pd.Series) -> 'ARIMAForecaster':
        """
        Fit ARIMA model to time series data

        Args:
            data: Time series data (pandas Series with datetime index)

        Returns:
            Self
        """
        # Find best order if not specified
        if self.best_order is None:
            self.best_order = self.find_best_order(data)

        # Fit model with best order
        self.model = ARIMA(data, order=self.best_order)
        self.fitted_model = self.model.fit()

        return self

    def forecast(self, steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate forecast

        Args:
            steps: Number of steps ahead to forecast

        Returns:
            Tuple of (forecast, lower_bound, upper_bound)
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before forecasting")

        # Get forecast
        forecast_result = self.fitted_model.get_forecast(steps=steps)

        forecast = forecast_result.predicted_mean.values
        conf_int = forecast_result.conf_int(alpha=0.2)  # 80% confidence interval

        lower_bound = conf_int.iloc[:, 0].values
        upper_bound = conf_int.iloc[:, 1].values

        return forecast, lower_bound, upper_bound

    def get_model_summary(self) -> dict:
        """Get model summary statistics"""
        if self.fitted_model is None:
            return {}

        return {
            'order': self.best_order,
            'aic': self.fitted_model.aic,
            'bic': self.fitted_model.bic,
            'model_type': 'ARIMA'
        }


class CategoryARIMAForecaster:
    """
    Apply ARIMA forecasting to each category separately
    """

    def __init__(self):
        """Initialize category-based ARIMA forecaster"""
        self.category_models = {}
        self.category_data = {}

    def prepare_category_data(self,
                             transactions_df: pd.DataFrame,
                             category: str,
                             frequency: str = 'W') -> pd.Series:
        """
        Prepare time series data for a specific category

        Args:
            transactions_df: DataFrame with transactions
            category: Category to prepare
            frequency: Resampling frequency ('D', 'W', 'M')

        Returns:
            Time series for category
        """
        # Filter by category
        cat_data = transactions_df[transactions_df['category'] == category].copy()

        if len(cat_data) == 0:
            return pd.Series(dtype=float)

        # Ensure date is datetime
        cat_data['date'] = pd.to_datetime(cat_data['date'])

        # Set date as index
        cat_data = cat_data.set_index('date')

        # Resample to desired frequency
        ts = cat_data['amount'].resample(frequency).sum()

        # Fill missing values
        ts = ts.fillna(0)

        return ts

    def fit_category(self,
                    transactions_df: pd.DataFrame,
                    category: str,
                    frequency: str = 'W') -> bool:
        """
        Fit ARIMA model for specific category

        Args:
            transactions_df: DataFrame with transactions
            category: Category to fit
            frequency: Time frequency

        Returns:
            True if successful
        """
        # Prepare data
        ts = self.prepare_category_data(transactions_df, category, frequency)

        if len(ts) < 10:  # Need minimum data
            return False

        # Fit ARIMA model
        try:
            forecaster = ARIMAForecaster()
            forecaster.fit(ts)

            self.category_models[category] = forecaster
            self.category_data[category] = ts

            return True
        except Exception as e:
            print(f"Failed to fit ARIMA for {category}: {e}")
            return False

    def fit_all_categories(self,
                          transactions_df: pd.DataFrame,
                          categories: List[str],
                          frequency: str = 'W') -> dict:
        """
        Fit ARIMA models for all categories

        Args:
            transactions_df: DataFrame with transactions
            categories: List of categories to fit
            frequency: Time frequency

        Returns:
            Dictionary with fit results
        """
        results = {}

        for category in categories:
            success = self.fit_category(transactions_df, category, frequency)
            results[category] = success

        return results

    def forecast_category(self,
                         category: str,
                         steps: int) -> Optional[dict]:
        """
        Forecast for specific category

        Args:
            category: Category to forecast
            steps: Steps ahead

        Returns:
            Dictionary with forecast, lower, upper bounds
        """
        if category not in self.category_models:
            return None

        forecaster = self.category_models[category]

        try:
            forecast, lower, upper = forecaster.forecast(steps)

            return {
                'forecast': forecast.tolist(),
                'lower_bound': lower.tolist(),
                'upper_bound': upper.tolist(),
                'category': category,
                'model_info': forecaster.get_model_summary()
            }
        except Exception as e:
            print(f"Forecast failed for {category}: {e}")
            return None

    def forecast_all_categories(self, steps: int) -> dict:
        """
        Generate forecasts for all fitted categories

        Args:
            steps: Steps ahead to forecast

        Returns:
            Dictionary of category forecasts
        """
        forecasts = {}

        for category in self.category_models.keys():
            forecast_result = self.forecast_category(category, steps)
            if forecast_result:
                forecasts[category] = forecast_result

        return forecasts


def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """
    Load transaction data from CSV

    Args:
        csv_path: Path to CSV file

    Returns:
        DataFrame with transactions
    """
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    return df


if __name__ == "__main__":
    # Example usage
    print("ARIMA Forecasting Model - Example Usage\n")

    # Load sample data
    df = load_and_prepare_data('data/transactions.csv')
    print(f"Loaded {len(df)} transactions")

    # Test category forecaster
    category_forecaster = CategoryARIMAForecaster()

    # Fit for revenue category
    print("\nFitting ARIMA for 'revenue' category...")
    success = category_forecaster.fit_category(df, 'revenue', frequency='W')

    if success:
        print("✓ Model fitted successfully")

        # Generate forecast
        forecast = category_forecaster.forecast_category('revenue', steps=13)

        if forecast:
            print(f"\n13-Week Revenue Forecast (ARIMA):")
            print(f"  Order: {forecast['model_info']['order']}")
            print(f"  AIC: {forecast['model_info']['aic']:.2f}")
            print(f"\n  Week 1: ${forecast['forecast'][0]:,.2f}")
            print(f"  Week 13: ${forecast['forecast'][-1]:,.2f}")
