
"""
Category-Based Forecasting
Predicts each cash flow category separately using appropriate methods
"""

import numpy as np
import pandas as pd
from typing import List, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from .models import (
    HistoricalData, CategoryForecast, CashFlowCategory
)
from .processor import DataProcessor


class CategoryPredictor:
    """Forecasts individual cash flow categories"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.models = {}
        
    def predict_category(self, historical_data: HistoricalData,
                        category: CashFlowCategory,
                        weeks_ahead: int = 13) -> CategoryForecast:
        """
        Predict future values for a specific category
        
        Args:
            historical_data: Historical transaction data
            category: Category to predict
            weeks_ahead: Number of weeks to forecast
            
        Returns:
            CategoryForecast object with predictions
        """
        # Get aggregated data for this category
        df = self.processor.aggregate_by_category(historical_data, 'W')
        cat_df = df[df['category'] == category.value].copy()
        
        if len(cat_df) < 4:
            # Insufficient data, use simple average
            return self._predict_simple_average(cat_df, category, weeks_ahead)
        
        # Choose prediction method based on category characteristics
        if self._is_fixed_category(category):
            return self._predict_fixed(cat_df, category, weeks_ahead)
        elif self._has_trend(cat_df):
            return self._predict_with_trend(cat_df, category, weeks_ahead)
        else:
            return self._predict_exponential_smoothing(cat_df, category, weeks_ahead)
    
    def _is_fixed_category(self, category: CashFlowCategory) -> bool:
        """Check if category typically has fixed costs"""
        fixed_categories = {
            CashFlowCategory.RENT,
            CashFlowCategory.INSURANCE
        }
        return category in fixed_categories
    
    def _has_trend(self, df: pd.DataFrame, threshold: float = 0.05) -> bool:
        """Check if data has significant trend"""
        if len(df) < 4:
            return False
        
        # Simple linear regression to detect trend
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['amount'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Check if slope is significant relative to mean
        slope = model.coef_[0]
        mean_value = y.mean()
        
        trend_pct = abs(slope / mean_value) if mean_value != 0 else 0
        return trend_pct > threshold
    
    def _predict_simple_average(self, df: pd.DataFrame, 
                                category: CashFlowCategory,
                                weeks_ahead: int) -> CategoryForecast:
        """Simple average prediction for categories with little data"""
        if len(df) == 0:
            avg = 0
            std = 0
        else:
            avg = df['amount'].mean()
            std = df['amount'].std()
        
        predictions = [avg] * weeks_ahead
        
        return CategoryForecast(
            category=category,
            weekly_predictions=predictions,
            confidence_interval=std,
            trend='stable',
            volatility=std / avg if avg != 0 else 0
        )
    
    def _predict_fixed(self, df: pd.DataFrame,
                      category: CashFlowCategory,
                      weeks_ahead: int) -> CategoryForecast:
        """Predict fixed costs (constant amount)"""
        # Use median for fixed costs (more robust to outliers)
        median_value = df['amount'].median()
        std = df['amount'].std()
        
        predictions = [median_value] * weeks_ahead
        
        return CategoryForecast(
            category=category,
            weekly_predictions=predictions,
            confidence_interval=std * 0.5,  # Lower uncertainty for fixed costs
            trend='stable',
            volatility=0.1  # Very low volatility
        )
    
    def _predict_with_trend(self, df: pd.DataFrame,
                           category: CashFlowCategory,
                           weeks_ahead: int) -> CategoryForecast:
        """Predict using linear regression for trending data"""
        # Prepare data
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['amount'].values
        
        # Fit linear model
        model = LinearRegression()
        model.fit(X, y)
        
        # Make predictions
        future_X = np.arange(len(df), len(df) + weeks_ahead).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        
        # Calculate confidence interval
        residuals = y - model.predict(X)
        std = np.std(residuals)
        
        # Determine trend direction
        slope = model.coef_[0]
        if slope > 0.01 * y.mean():
            trend = 'increasing'
        elif slope < -0.01 * y.mean():
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return CategoryForecast(
            category=category,
            weekly_predictions=predictions.tolist(),
            confidence_interval=std,
            trend=trend,
            volatility=std / y.mean() if y.mean() != 0 else 0
        )
    
    def _predict_exponential_smoothing(self, df: pd.DataFrame,
                                      category: CashFlowCategory,
                                      weeks_ahead: int) -> CategoryForecast:
        """Predict using exponential smoothing"""
        values = df['amount'].values
        
        try:
            # Try exponential smoothing with trend
            model = ExponentialSmoothing(
                values,
                trend='add',
                seasonal=None,
                damped_trend=True
            )
            fitted_model = model.fit()
            predictions = fitted_model.forecast(steps=weeks_ahead)
            
            # Ensure non-negative
            predictions = np.maximum(predictions, 0)
            
        except Exception as e:
            # Fallback to simple exponential smoothing
            alpha = 0.3
            predictions = []
            last_value = values[-1]
            
            for _ in range(weeks_ahead):
                predictions.append(last_value)
                last_value = alpha * last_value + (1 - alpha) * values.mean()
        
        # Calculate statistics
        std = np.std(values)
        mean = np.mean(values)
        
        # Determine trend
        if len(values) >= 4:
            recent_mean = np.mean(values[-4:])
            early_mean = np.mean(values[:4])
            if recent_mean > early_mean * 1.1:
                trend = 'increasing'
            elif recent_mean < early_mean * 0.9:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return CategoryForecast(
            category=category,
            weekly_predictions=predictions if isinstance(predictions, list) else predictions.tolist(),
            confidence_interval=std,
            trend=trend,
            volatility=std / mean if mean != 0 else 0
        )
    
    def predict_ar_collections(self, historical_data: HistoricalData,
                              current_ar_balance: float,
                              ar_aging: dict,
                              weeks_ahead: int = 13) -> CategoryForecast:
        """
        Specialized prediction for Accounts Receivable collections
        
        Args:
            historical_data: Historical transaction data
            current_ar_balance: Current AR balance
            ar_aging: Dict with aging buckets, e.g., {'0-30': 100000, '31-45': 50000}
            weeks_ahead: Number of weeks to forecast
            
        Returns:
            CategoryForecast for AR collections
        """
        # Standard collection patterns (can be learned from historical data)
        collection_patterns = {
            '0-30': {'week_1': 0.30, 'week_2': 0.40, 'week_3': 0.20, 'week_4': 0.10},
            '31-45': {'week_1': 0.20, 'week_2': 0.40, 'week_3': 0.30, 'week_4': 0.10},
            '46-60': {'week_1': 0.10, 'week_2': 0.30, 'week_3': 0.40, 'week_4': 0.20},
            '60+': {'week_1': 0.05, 'week_2': 0.15, 'week_3': 0.30, 'week_4': 0.30}
        }
        
        predictions = []
        
        # Project AR collections for each week
        for week in range(weeks_ahead):
            week_collection = 0
            
            # Collections from existing AR
            for bucket, balance in ar_aging.items():
                pattern = collection_patterns.get(bucket, {'week_1': 0.25})
                week_key = f'week_{min(week + 1, 4)}'
                collection_rate = pattern.get(week_key, 0.05)
                week_collection += balance * collection_rate
            
            # Add collections from new invoices (based on revenue forecast)
            # This is a simplification - in production, would integrate with revenue forecast
            new_invoice_collection = current_ar_balance * 0.05
            week_collection += new_invoice_collection
            
            predictions.append(week_collection)
        
        # Calculate confidence interval based on historical volatility
        std = np.std(predictions) * 0.3  # AR typically less volatile
        
        return CategoryForecast(
            category=CashFlowCategory.AR_COLLECTIONS,
            weekly_predictions=predictions,
            confidence_interval=std,
            trend='stable',
            volatility=0.15
        )


class EnsemblePredictor:
    """Combines multiple prediction methods for improved accuracy"""
    
    def __init__(self):
        self.category_predictor = CategoryPredictor()
    
    def predict_with_ensemble(self, historical_data: HistoricalData,
                             category: CashFlowCategory,
                             weeks_ahead: int = 13) -> CategoryForecast:
        """
        Use ensemble of methods and average predictions
        
        This improves robustness by combining:
        - Linear regression
        - Exponential smoothing
        - Historical average
        """
        # Get predictions from multiple methods
        predictions_list = []
        
        # Method 1: Category predictor (primary)
        forecast1 = self.category_predictor.predict_category(
            historical_data, category, weeks_ahead
        )
        predictions_list.append(forecast1.weekly_predictions)
        
        # Method 2: Simple moving average
        df = DataProcessor().aggregate_by_category(historical_data, 'W')
        cat_df = df[df['category'] == category.value]
        if len(cat_df) >= 4:
            ma = cat_df['amount'].tail(4).mean()
            predictions_list.append([ma] * weeks_ahead)
        
        # Average predictions
        ensemble_predictions = np.mean(predictions_list, axis=0).tolist()
        
        # Use confidence interval from primary forecast
        return CategoryForecast(
            category=category,
            weekly_predictions=ensemble_predictions,
            confidence_interval=forecast1.confidence_interval,
            trend=forecast1.trend,
            volatility=forecast1.volatility
        )
