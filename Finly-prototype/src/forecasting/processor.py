"""
Data Processing Utilities
Handles data validation, cleaning, and aggregation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple
from .models import (
    HistoricalData, Transaction, TransactionType, CashFlowCategory
)


class DataProcessor:
    """Processes and validates transaction data"""

    def validate_data(self, historical_data: HistoricalData) -> Tuple[bool, List[str]]:
        """
        Validate historical data quality

        Args:
            historical_data: HistoricalData object to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check if we have enough data
        if len(historical_data.transactions) < 10:
            issues.append("Insufficient data: Need at least 10 transactions")

        # Check date range
        date_range = (historical_data.end_date - historical_data.start_date).days
        if date_range < 30:
            issues.append("Insufficient date range: Need at least 30 days of history")

        # Check for negative amounts
        negative_amounts = [txn for txn in historical_data.transactions if txn.amount < 0]
        if negative_amounts:
            issues.append(f"Found {len(negative_amounts)} transactions with negative amounts")

        # Check for missing dates
        missing_dates = [txn for txn in historical_data.transactions if txn.date is None]
        if missing_dates:
            issues.append(f"Found {len(missing_dates)} transactions with missing dates")

        # Check date consistency
        out_of_range = [
            txn for txn in historical_data.transactions
            if txn.date < historical_data.start_date or txn.date > historical_data.end_date
        ]
        if out_of_range:
            issues.append(f"Found {len(out_of_range)} transactions outside date range")

        return len(issues) == 0, issues

    def clean_data(self, historical_data: HistoricalData) -> HistoricalData:
        """
        Clean and prepare data for analysis

        Args:
            historical_data: Raw historical data

        Returns:
            Cleaned HistoricalData object
        """
        cleaned_transactions = []

        for txn in historical_data.transactions:
            # Skip invalid transactions
            if txn.amount < 0:
                continue
            if txn.date is None:
                continue
            if txn.date < historical_data.start_date or txn.date > historical_data.end_date:
                continue

            cleaned_transactions.append(txn)

        return HistoricalData(
            transactions=cleaned_transactions,
            start_date=historical_data.start_date,
            end_date=historical_data.end_date,
            opening_balance=historical_data.opening_balance
        )

    def aggregate_by_category(self,
                             historical_data: HistoricalData,
                             frequency: str = 'W') -> pd.DataFrame:
        """
        Aggregate transactions by category and time period

        Args:
            historical_data: Historical transaction data
            frequency: Pandas frequency string ('W'=weekly, 'M'=monthly, 'D'=daily)

        Returns:
            DataFrame with aggregated data
        """
        df = historical_data.to_dataframe()

        if df.empty:
            return pd.DataFrame(columns=['date', 'category', 'amount', 'transaction_type'])

        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # Group by category and time period
        grouped = df.groupby([
            pd.Grouper(freq=frequency),
            'category',
            'transaction_type'
        ])['amount'].sum().reset_index()

        return grouped

    def get_category_stats(self,
                          historical_data: HistoricalData,
                          category: CashFlowCategory) -> dict:
        """
        Calculate statistics for a specific category

        Args:
            historical_data: Historical transaction data
            category: Category to analyze

        Returns:
            Dictionary with statistics
        """
        transactions = historical_data.get_category_transactions(category)

        if not transactions:
            return {
                'count': 0,
                'total': 0,
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0
            }

        amounts = [txn.amount for txn in transactions]

        return {
            'count': len(amounts),
            'total': sum(amounts),
            'mean': np.mean(amounts),
            'median': np.median(amounts),
            'std': np.std(amounts),
            'min': min(amounts),
            'max': max(amounts)
        }

    def detect_seasonality(self,
                          historical_data: HistoricalData,
                          category: CashFlowCategory) -> bool:
        """
        Detect if a category shows seasonal patterns

        Args:
            historical_data: Historical transaction data
            category: Category to analyze

        Returns:
            True if seasonality detected
        """
        df = self.aggregate_by_category(historical_data, 'W')
        cat_df = df[df['category'] == category.value]

        if len(cat_df) < 8:  # Need at least 8 weeks
            return False

        # Simple seasonality detection: compare variance of week-to-week changes
        amounts = cat_df['amount'].values
        weekly_changes = np.diff(amounts)

        # If changes are relatively consistent, might have seasonality
        change_std = np.std(weekly_changes)
        amount_mean = np.mean(amounts)

        # High variability suggests seasonality
        cv = change_std / amount_mean if amount_mean > 0 else 0
        return cv > 0.3

    def split_train_test(self,
                        historical_data: HistoricalData,
                        test_weeks: int = 4) -> Tuple[HistoricalData, HistoricalData]:
        """
        Split data into training and testing sets

        Args:
            historical_data: Full historical data
            test_weeks: Number of weeks to reserve for testing

        Returns:
            Tuple of (training_data, testing_data)
        """
        split_date = historical_data.end_date - timedelta(weeks=test_weeks)

        train_transactions = [
            txn for txn in historical_data.transactions
            if txn.date <= split_date
        ]

        test_transactions = [
            txn for txn in historical_data.transactions
            if txn.date > split_date
        ]

        train_data = HistoricalData(
            transactions=train_transactions,
            start_date=historical_data.start_date,
            end_date=split_date,
            opening_balance=historical_data.opening_balance
        )

        test_data = HistoricalData(
            transactions=test_transactions,
            start_date=split_date + timedelta(days=1),
            end_date=historical_data.end_date,
            opening_balance=historical_data.opening_balance  # Should calculate actual balance at split
        )

        return train_data, test_data
