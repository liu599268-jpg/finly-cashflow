"""
XGBoost Machine Learning Forecasting Model
Uses gradient boosting with engineered features
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


class XGBoostForecaster:
    """
    XGBoost-based forecaster with feature engineering
    Captures non-linear patterns and interactions
    """

    def __init__(self,
                 n_estimators: int = 100,
                 max_depth: int = 5,
                 learning_rate: float = 0.1):
        """
        Initialize XGBoost forecaster

        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate (eta)
        """
        if not HAS_XGBOOST:
            raise ImportError("xgboost is required for XGBoost forecasting")

        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.model = None
        self.feature_names = []
        self.is_fitted = False

    def engineer_features(self,
                         ts_data: pd.Series,
                         lag_periods: List[int] = [1, 2, 3, 4, 8, 12]) -> pd.DataFrame:
        """
        Create features from time series

        Args:
            ts_data: Time series data
            lag_periods: Periods to use for lag features

        Returns:
            DataFrame with engineered features
        """
        df = pd.DataFrame(index=ts_data.index)

        # Original value
        df['value'] = ts_data.values

        # Time-based features
        df['week_of_year'] = ts_data.index.isocalendar().week
        df['month'] = ts_data.index.month
        df['quarter'] = ts_data.index.quarter
        df['day_of_week'] = ts_data.index.dayofweek
        df['day_of_month'] = ts_data.index.day
        df['is_month_start'] = ts_data.index.is_month_start.astype(int)
        df['is_month_end'] = ts_data.index.is_month_end.astype(int)
        df['is_quarter_start'] = ts_data.index.is_quarter_start.astype(int)
        df['is_quarter_end'] = ts_data.index.is_quarter_end.astype(int)

        # Cyclical encoding for seasonality
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['week_sin'] = np.sin(2 * np.pi * df['week_of_year'] / 52)
        df['week_cos'] = np.cos(2 * np.pi * df['week_of_year'] / 52)
        df['quarter_sin'] = np.sin(2 * np.pi * df['quarter'] / 4)
        df['quarter_cos'] = np.cos(2 * np.pi * df['quarter'] / 4)

        # Trend (time index)
        df['time_index'] = np.arange(len(df))

        # Lag features
        for lag in lag_periods:
            df[f'lag_{lag}'] = ts_data.shift(lag)

        # Rolling statistics (multiple windows)
        for window in [4, 8, 12, 16]:  # 4, 8, 12, 16 weeks
            df[f'rolling_mean_{window}'] = ts_data.rolling(window=window, min_periods=1).mean()
            df[f'rolling_std_{window}'] = ts_data.rolling(window=window, min_periods=1).std()
            df[f'rolling_min_{window}'] = ts_data.rolling(window=window, min_periods=1).min()
            df[f'rolling_max_{window}'] = ts_data.rolling(window=window, min_periods=1).max()

        # Exponentially weighted moving averages
        df['ewm_4'] = ts_data.ewm(span=4, adjust=False).mean()
        df['ewm_8'] = ts_data.ewm(span=8, adjust=False).mean()
        df['ewm_12'] = ts_data.ewm(span=12, adjust=False).mean()

        # Growth and momentum features
        df['growth_rate'] = ts_data.pct_change()
        df['growth_rate_4'] = ts_data.pct_change(periods=4)
        df['acceleration'] = df['growth_rate'].diff()

        # Differencing features
        df['diff_1'] = ts_data.diff()
        df['diff_4'] = ts_data.diff(periods=4)

        # Fill NaN values
        df = df.fillna(method='bfill').fillna(0)

        return df

    def prepare_train_data(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from features

        Args:
            features_df: DataFrame with features

        Returns:
            X (features) and y (target) arrays
        """
        # Target is the value column
        y = features_df['value'].values

        # Features are everything except value
        X = features_df.drop('value', axis=1).values

        # Store feature names
        self.feature_names = [col for col in features_df.columns if col != 'value']

        return X, y

    def fit(self, ts_data: pd.Series) -> 'XGBoostForecaster':
        """
        Fit XGBoost model

        Args:
            ts_data: Time series data

        Returns:
            Self
        """
        # Engineer features
        features_df = self.engineer_features(ts_data)

        # Prepare training data
        X, y = self.prepare_train_data(features_df)

        # Initialize and fit XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            objective='reg:squarederror',
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X, y)
        self.is_fitted = True

        return self

    def forecast(self,
                ts_data: pd.Series,
                steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate forecast

        Args:
            ts_data: Historical time series data
            steps: Number of steps ahead

        Returns:
            Tuple of (forecast, lower_bound, upper_bound)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before forecasting")

        forecasts = []
        extended_data = ts_data.copy()

        # Iteratively forecast each step
        for step in range(steps):
            # Engineer features for current data
            features_df = self.engineer_features(extended_data)

            # Get last row features
            last_features = features_df.iloc[-1:].drop('value', axis=1).values

            # Predict
            prediction = self.model.predict(last_features)[0]

            # Ensure non-negative
            prediction = max(0, prediction)

            forecasts.append(prediction)

            # Add prediction to extended data for next iteration
            next_date = extended_data.index[-1] + timedelta(weeks=1)
            extended_data = pd.concat([
                extended_data,
                pd.Series([prediction], index=[next_date])
            ])

        forecasts = np.array(forecasts)

        # Calculate prediction intervals based on historical error
        features_df = self.engineer_features(ts_data)
        X, y = self.prepare_train_data(features_df)
        predictions = self.model.predict(X)
        residuals = y - predictions
        std_error = np.std(residuals)

        # 80% confidence interval (1.28 std devs)
        lower_bound = forecasts - (1.28 * std_error)
        upper_bound = forecasts + (1.28 * std_error)

        # Ensure non-negative
        lower_bound = np.maximum(lower_bound, 0)

        return forecasts, lower_bound, upper_bound

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from XGBoost"""
        if not self.is_fitted:
            return pd.DataFrame()

        importance = self.model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        })

        importance_df = importance_df.sort_values('importance', ascending=False)

        return importance_df

    def get_model_summary(self) -> dict:
        """Get model summary statistics"""
        if not self.is_fitted:
            return {}

        return {
            'model_type': 'XGBoost',
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'n_features': len(self.feature_names)
        }


class MultiCategoryXGBoostForecaster:
    """
    Apply XGBoost forecasting to multiple categories
    """

    def __init__(self,
                 n_estimators: int = 100,
                 max_depth: int = 5,
                 learning_rate: float = 0.1):
        """
        Initialize multi-category forecaster

        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.category_models = {}
        self.category_data = {}

    def prepare_category_data(self,
                             transactions_df: pd.DataFrame,
                             category: str,
                             frequency: str = 'W') -> pd.Series:
        """
        Prepare time series data for category

        Args:
            transactions_df: Transaction DataFrame
            category: Category name
            frequency: Resampling frequency

        Returns:
            Time series for category
        """
        # Filter by category
        cat_data = transactions_df[transactions_df['category'] == category].copy()

        if len(cat_data) == 0:
            return pd.Series(dtype=float)

        # Ensure datetime
        cat_data['date'] = pd.to_datetime(cat_data['date'])

        # Set index
        cat_data = cat_data.set_index('date')

        # Resample
        ts = cat_data['amount'].resample(frequency).sum()

        # Fill missing
        ts = ts.fillna(0)

        return ts

    def fit_category(self,
                    transactions_df: pd.DataFrame,
                    category: str,
                    frequency: str = 'W') -> bool:
        """
        Fit XGBoost model for category

        Args:
            transactions_df: Transaction DataFrame
            category: Category name
            frequency: Time frequency

        Returns:
            True if successful
        """
        # Prepare data
        ts = self.prepare_category_data(transactions_df, category, frequency)

        if len(ts) < 12:  # Need minimum data
            return False

        try:
            # Fit model
            forecaster = XGBoostForecaster(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate
            )
            forecaster.fit(ts)

            self.category_models[category] = forecaster
            self.category_data[category] = ts

            return True
        except Exception as e:
            print(f"Failed to fit XGBoost for {category}: {e}")
            return False

    def fit_all_categories(self,
                          transactions_df: pd.DataFrame,
                          categories: List[str],
                          frequency: str = 'W') -> Dict[str, bool]:
        """
        Fit models for all categories

        Args:
            transactions_df: Transaction DataFrame
            categories: List of categories
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
            category: Category name
            steps: Steps ahead

        Returns:
            Forecast dictionary
        """
        if category not in self.category_models:
            return None

        forecaster = self.category_models[category]
        ts_data = self.category_data[category]

        try:
            forecast, lower, upper = forecaster.forecast(ts_data, steps)

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
        Generate forecasts for all categories

        Args:
            steps: Steps ahead

        Returns:
            Dictionary of forecasts
        """
        forecasts = {}

        for category in self.category_models.keys():
            forecast_result = self.forecast_category(category, steps)
            if forecast_result:
                forecasts[category] = forecast_result

        return forecasts


if __name__ == "__main__":
    # Example usage
    print("XGBoost Forecasting - Example Usage\n")

    # Load data
    df = pd.read_csv('data/transactions.csv')
    print(f"Loaded {len(df)} transactions")

    # Test XGBoost forecaster
    multi_forecaster = MultiCategoryXGBoostForecaster(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1
    )

    print("\nFitting XGBoost for 'revenue' category...")
    success = multi_forecaster.fit_category(df, 'revenue', frequency='W')

    if success:
        print("✓ Model fitted successfully")

        # Generate forecast
        forecast = multi_forecaster.forecast_category('revenue', steps=13)

        if forecast:
            print(f"\n13-Week Revenue Forecast (XGBoost):")
            print(f"  Model: {forecast['model_info']['model_type']}")
            print(f"  Estimators: {forecast['model_info']['n_estimators']}")
            print(f"\n  Week 1: ${forecast['forecast'][0]:,.2f}")
            print(f"  Week 13: ${forecast['forecast'][-1]:,.2f}")
