"""
Data Models for Cash Flow Forecasting
Core data structures used throughout the system
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
import pandas as pd


class TransactionType(Enum):
    """Transaction direction"""
    INFLOW = "inflow"
    OUTFLOW = "outflow"


class CashFlowCategory(Enum):
    """Cash flow categories"""
    # Inflows
    REVENUE = "revenue"
    AR_COLLECTIONS = "ar_collections"
    INVESTMENT_INCOME = "investment_income"
    OTHER_INCOME = "other_income"

    # Outflows
    COGS = "cogs"
    PAYROLL = "payroll"
    RENT = "rent"
    MARKETING = "marketing"
    TECHNOLOGY = "technology"
    AP_PAYMENTS = "ap_payments"
    INSURANCE = "insurance"
    UTILITIES = "utilities"
    PROFESSIONAL_SERVICES = "professional_services"
    TRAVEL = "travel"
    OFFICE_SUPPLIES = "office_supplies"
    OTHER_EXPENSES = "other_expenses"


@dataclass
class Transaction:
    """Individual transaction record"""
    date: datetime
    amount: float
    category: CashFlowCategory
    transaction_type: TransactionType
    description: str
    customer: Optional[str] = None
    vendor: Optional[str] = None
    invoice_id: Optional[str] = None
    bill_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'date': self.date.isoformat(),
            'amount': self.amount,
            'category': self.category.value,
            'transaction_type': self.transaction_type.value,
            'description': self.description,
            'customer': self.customer,
            'vendor': self.vendor,
            'invoice_id': self.invoice_id,
            'bill_id': self.bill_id
        }


@dataclass
class HistoricalData:
    """Collection of historical transactions"""
    transactions: List[Transaction]
    start_date: datetime
    end_date: datetime
    opening_balance: float

    def to_dataframe(self) -> pd.DataFrame:
        """Convert transactions to pandas DataFrame"""
        data = []
        for txn in self.transactions:
            data.append({
                'date': txn.date,
                'amount': txn.amount,
                'category': txn.category.value,
                'transaction_type': txn.transaction_type.value,
                'description': txn.description,
                'customer': txn.customer,
                'vendor': txn.vendor
            })
        return pd.DataFrame(data)

    def get_category_transactions(self, category: CashFlowCategory) -> List[Transaction]:
        """Get all transactions for a specific category"""
        return [txn for txn in self.transactions if txn.category == category]

    def get_transactions_by_type(self, txn_type: TransactionType) -> List[Transaction]:
        """Get all transactions of a specific type"""
        return [txn for txn in self.transactions if txn.transaction_type == txn_type]


@dataclass
class CategoryForecast:
    """Forecast for a single category"""
    category: CashFlowCategory
    weekly_predictions: List[float]
    confidence_interval: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    volatility: float


@dataclass
class ForecastPoint:
    """Single point in time forecast"""
    date: datetime
    predicted_balance: float
    confidence_lower: float
    confidence_upper: float
    predicted_inflows: float
    predicted_outflows: float
    net_cash_flow: float

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'date': self.date.isoformat(),
            'predicted_balance': round(self.predicted_balance, 2),
            'confidence_lower': round(self.confidence_lower, 2),
            'confidence_upper': round(self.confidence_upper, 2),
            'predicted_inflows': round(self.predicted_inflows, 2),
            'predicted_outflows': round(self.predicted_outflows, 2),
            'net_cash_flow': round(self.net_cash_flow, 2)
        }


@dataclass
class Forecast:
    """Complete cash flow forecast"""
    company_name: str
    forecast_date: datetime
    current_balance: float
    forecast_points: List[ForecastPoint]
    model_accuracy: Optional[float] = None

    def get_final_balance(self) -> float:
        """Get predicted balance at end of forecast period"""
        return self.forecast_points[-1].predicted_balance if self.forecast_points else self.current_balance

    def get_minimum_balance(self) -> float:
        """Get minimum predicted balance during forecast period"""
        if not self.forecast_points:
            return self.current_balance
        return min(point.predicted_balance for point in self.forecast_points)

    def get_weeks_until_zero(self) -> Optional[int]:
        """Get number of weeks until cash runs out (None if never)"""
        for i, point in enumerate(self.forecast_points):
            if point.predicted_balance <= 0:
                return i + 1
        return None

    def get_average_weekly_burn(self) -> float:
        """Calculate average weekly burn rate (negative means profit)"""
        if not self.forecast_points:
            return 0

        total_net = sum(point.net_cash_flow for point in self.forecast_points)
        return -total_net / len(self.forecast_points)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'company_name': self.company_name,
            'forecast_date': self.forecast_date.isoformat(),
            'current_balance': round(self.current_balance, 2),
            'final_balance': round(self.get_final_balance(), 2),
            'minimum_balance': round(self.get_minimum_balance(), 2),
            'weeks_until_zero': self.get_weeks_until_zero(),
            'average_weekly_burn': round(self.get_average_weekly_burn(), 2),
            'model_accuracy': round(self.model_accuracy, 2) if self.model_accuracy else None,
            'forecast_points': [point.to_dict() for point in self.forecast_points]
        }


@dataclass
class Scenario:
    """What-if scenario analysis"""
    scenario_name: str
    description: str
    adjustments: Dict[str, float]
    forecast: Forecast
    impact_vs_baseline: float

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'scenario_name': self.scenario_name,
            'description': self.description,
            'adjustments': self.adjustments,
            'impact_vs_baseline': round(self.impact_vs_baseline, 2),
            'forecast': self.forecast.to_dict()
        }
