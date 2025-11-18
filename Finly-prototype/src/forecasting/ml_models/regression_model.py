"""
Category-Based Regression Forecasting Model
Uses multiple regression with engineered features
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error


class CategoryRegressionForecaster:
    """
    Regression-based forecaster with feature engineering
    Captures trends, seasonality, and patterns
    """

    def __init__(self, model_type: str = 'ridge'):
        """
        Initialize regression forecaster

        Args:
            model_type: 'linear', 'ridge', or 'lasso'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_fitted = False

    def engineer_features(self,
                         ts_data: pd.Series,
                         lag_periods: List[int] = [1, 2, 3, 4]) -> pd.DataFrame:
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

        # Cyclical encoding for seasonality
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['week_sin'] = np.sin(2 * np.pi * df['week_of_year'] / 52)
        df['week_cos'] = np.cos(2 * np.pi * df['week_of_year'] / 52)

        # Trend (time index)
        df['time_index'] = np.arange(len(df))

        # Lag features
        for lag in lag_periods:
            df[f'lag_{lag}'] = ts_data.shift(lag)

        # Rolling statistics
        for window in [4, 8, 12]:  # 4, 8, 12 weeks
            df[f'rolling_mean_{window}'] = ts_data.rolling(window=window, min_periods=1).mean()
            df[f'rolling_std_{window}'] = ts_data.rolling(window=window, min_periods=1).std()

        # Moving averages
        df['ma_4'] = ts_data.rolling(window=4, min_periods=1).mean()
        df['ma_8'] = ts_data.rolling(window=8, min_periods=1).mean()

        # Growth rate
        df['growth_rate'] = ts_data.pct_change()

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

    def fit(self, ts_data: pd.Series) -> 'CategoryRegressionForecaster':
        """
        Fit regression model

        Args:
            ts_data: Time series data

        Returns:
            Self
        """
        # Engineer features
        features_df = self.engineer_features(ts_data)

        # Prepare training data
        X, y = self.prepare_train_data(features_df)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Select model
        if self.model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        elif self.model_type == 'lasso':
            self.model = Lasso(alpha=1.0)
        else:
            self.model = LinearRegression()

        # Fit model
        self.model.fit(X_scaled, y)
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

            # Scale
            last_features_scaled = self.scaler.transform(last_features)

            # Predict
            prediction = self.model.predict(last_features_scaled)[0]

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
        # Simple approach: use standard deviation of residuals
        features_df = self.engineer_features(ts_data)
        X, y = self.prepare_train_data(features_df)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        residuals = y - predictions
        std_error = np.std(residuals)

        # 80% confidence interval (1.28 std devs)
        lower_bound = forecasts - (1.28 * std_error)
        upper_bound = forecasts + (1.28 * std_error)

        # Ensure non-negative
        lower_bound = np.maximum(lower_bound, 0)

        return forecasts, lower_bound, upper_bound

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance (coefficients)"""
        if not self.is_fitted:
            return pd.DataFrame()

        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'coefficient': self.model.coef_
        })

        importance_df['abs_coefficient'] = importance_df['coefficient'].abs()
        importance_df = importance_df.sort_values('abs_coefficient', ascending=False)

        return importance_df

    def get_model_summary(self) -> dict:
        """Get model summary statistics"""
        if not self.is_fitted:
            return {}

        return {
            'model_type': f'Regression ({self.model_type})',
            'n_features': len(self.feature_names),
            'r2_score': getattr(self.model, 'score', lambda x, y: 0)(
                self.scaler.transform(self.model.coef_.reshape(1, -1)),
                [0]
            ) if hasattr(self.model, 'coef_') else 0
        }


class MultiCategoryRegressionForecaster:
    """
    Apply regression forecasting to multiple categories
    """

    def __init__(self, model_type: str = 'ridge'):
        """
        Initialize multi-category forecaster

        Args:
            model_type: Type of regression model
        """
        self.model_type = model_type
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
        Fit regression model for category

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
            forecaster = CategoryRegressionForecaster(model_type=self.model_type)
            forecaster.fit(ts)

            self.category_models[category] = forecaster
            self.category_data[category] = ts

            return True
        except Exception as e:
            print(f"Failed to fit regression for {category}: {e}")
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
    print("Category Regression Forecasting - Example Usage\n")

    # Load data
    df = pd.read_csv('data/transactions.csv')
    print(f"Loaded {len(df)} transactions")

    # Test regression forecaster
    multi_forecaster = MultiCategoryRegressionForecaster(model_type='ridge')

    print("\nFitting regression for 'revenue' category...")
    success = multi_forecaster.fit_category(df, 'revenue', frequency='W')

    if success:
        print("✓ Model fitted successfully")

        # Generate forecast
        forecast = multi_forecaster.forecast_category('revenue', steps=13)

        if forecast:
            print(f"\n13-Week Revenue Forecast (Regression):")
            print(f"  Model: {forecast['model_info']['model_type']}")
            print(f"\n  Week 1: ${forecast['forecast'][0]:,.2f}")
            print(f"  Week 13: ${forecast['forecast'][-1]:,.2f}")
