"""
Sample Data Generator
Creates realistic transaction data for testing and demos
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import List
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.forecasting.models import (
    Transaction, TransactionType, CashFlowCategory, HistoricalData
)


class SampleDataGenerator:
    """Generates realistic sample transaction data"""

    def __init__(self, seed: int = 42):
        """
        Initialize generator

        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)
        np.random.seed(seed)

    def generate_transactions(self,
                             num_weeks: int = 52,
                             growth_rate: float = 0.10,
                             seasonality: bool = True) -> HistoricalData:
        """
        Generate realistic transaction history

        Args:
            num_weeks: Number of weeks of data to generate
            growth_rate: Annual growth rate (e.g., 0.10 = 10%)
            seasonality: Whether to include seasonal patterns

        Returns:
            HistoricalData object with generated transactions
        """
        transactions = []
        end_date = datetime.now() - timedelta(days=7)  # End one week ago
        start_date = end_date - timedelta(weeks=num_weeks)

        # Base amounts for each category (weekly)
        base_amounts = {
            # Inflows
            CashFlowCategory.REVENUE: 50000,
            CashFlowCategory.AR_COLLECTIONS: 0,  # Will handle separately
            CashFlowCategory.INVESTMENT_INCOME: 500,
            CashFlowCategory.OTHER_INCOME: 1000,

            # Outflows
            CashFlowCategory.COGS: 15000,
            CashFlowCategory.PAYROLL: 30000,
            CashFlowCategory.RENT: 8000,
            CashFlowCategory.MARKETING: 5000,
            CashFlowCategory.TECHNOLOGY: 3000,
            CashFlowCategory.INSURANCE: 1000,
            CashFlowCategory.UTILITIES: 800,
            CashFlowCategory.PROFESSIONAL_SERVICES: 2000,
            CashFlowCategory.TRAVEL: 1500,
            CashFlowCategory.OFFICE_SUPPLIES: 500,
            CashFlowCategory.OTHER_EXPENSES: 3000
        }

        # Generate transactions for each week
        for week in range(num_weeks):
            week_date = start_date + timedelta(weeks=week)

            # Apply growth over time
            growth_factor = 1 + (growth_rate * (week / 52))

            # Apply seasonality (optional)
            season_factor = 1.0
            if seasonality:
                # Q4 boost (weeks 40-52)
                week_of_year = week % 52
                if 40 <= week_of_year <= 52:
                    season_factor = 1.15
                # Q1 dip (weeks 1-13)
                elif 1 <= week_of_year <= 13:
                    season_factor = 0.90

            # Generate transactions for each category
            for category, base_amount in base_amounts.items():
                # Skip AR collections (handled separately)
                if category == CashFlowCategory.AR_COLLECTIONS:
                    continue

                # Determine transaction type
                if category in [CashFlowCategory.REVENUE, CashFlowCategory.INVESTMENT_INCOME,
                              CashFlowCategory.OTHER_INCOME]:
                    txn_type = TransactionType.INFLOW
                else:
                    txn_type = TransactionType.OUTFLOW

                # Calculate amount with growth, seasonality, and randomness
                amount = base_amount * growth_factor * season_factor

                # Add randomness (±20%)
                variance = 0.20
                amount *= random.uniform(1 - variance, 1 + variance)

                # Some categories are more regular (less variance)
                if category in [CashFlowCategory.RENT, CashFlowCategory.INSURANCE]:
                    amount = base_amount * growth_factor  # Fixed costs

                # Generate 1-3 transactions per week for this category
                num_txns = random.randint(1, 3) if category == CashFlowCategory.REVENUE else 1

                for _ in range(num_txns):
                    txn_amount = amount / num_txns
                    txn_date = week_date + timedelta(days=random.randint(0, 6))

                    transaction = Transaction(
                        date=txn_date,
                        amount=round(txn_amount, 2),
                        category=category,
                        transaction_type=txn_type,
                        description=f"{category.value.replace('_', ' ').title()}",
                        customer=f"Customer {random.randint(1, 50)}" if txn_type == TransactionType.INFLOW else None,
                        vendor=f"Vendor {random.randint(1, 30)}" if txn_type == TransactionType.OUTFLOW else None
                    )

                    transactions.append(transaction)

        # Sort transactions by date
        transactions.sort(key=lambda x: x.date)

        return HistoricalData(
            transactions=transactions,
            start_date=start_date,
            end_date=end_date,
            opening_balance=500000  # Starting with $500k
        )

    def create_scenario_data(self,
                            scenario_type: str,
                            num_weeks: int = 52) -> HistoricalData:
        """
        Create data for different scenarios

        Args:
            scenario_type: 'growth', 'stable', or 'declining'
            num_weeks: Number of weeks of data

        Returns:
            HistoricalData object
        """
        if scenario_type == 'growth':
            return self.generate_transactions(
                num_weeks=num_weeks,
                growth_rate=0.25,  # 25% growth
                seasonality=True
            )
        elif scenario_type == 'declining':
            return self.generate_transactions(
                num_weeks=num_weeks,
                growth_rate=-0.15,  # 15% decline
                seasonality=False
            )
        else:  # stable
            return self.generate_transactions(
                num_weeks=num_weeks,
                growth_rate=0.02,  # 2% growth
                seasonality=False
            )

    def generate_ar_aging(self, total_ar: float = 200000) -> dict:
        """
        Generate sample accounts receivable aging data

        Args:
            total_ar: Total AR balance

        Returns:
            Dictionary with aging buckets
        """
        # Typical distribution
        return {
            '0-30': total_ar * 0.50,    # 50% current
            '31-45': total_ar * 0.25,   # 25% 31-45 days
            '46-60': total_ar * 0.15,   # 15% 46-60 days
            '60+': total_ar * 0.10      # 10% over 60 days
        }
