"""
Generate Sample Transaction Data CSV
Creates realistic transaction data for forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.forecasting.models import CashFlowCategory, TransactionType


def generate_transactions_csv(num_weeks: int = 52, output_file: str = 'data/transactions.csv'):
    """Generate sample transaction data and save to CSV"""

    np.random.seed(42)

    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=num_weeks)

    transactions = []

    # Base weekly amounts for each category
    base_amounts = {
        # Inflows
        'revenue': 50000,
        'ar_collections': 0,  # Will be based on invoices
        'investment_income': 500,
        'other_income': 1000,

        # Outflows
        'cogs': 15000,
        'payroll': 30000,
        'rent': 8000,
        'marketing': 5000,
        'technology': 3000,
        'insurance': 1000,
        'utilities': 800,
        'professional_services': 2000,
        'travel': 1500,
        'office_supplies': 500,
        'other_expenses': 3000
    }

    # Growth rate and seasonality
    annual_growth_rate = 0.10

    transaction_id = 1

    for week in range(num_weeks):
        week_date = start_date + timedelta(weeks=week)

        # Apply growth
        growth_factor = 1 + (annual_growth_rate * (week / 52))

        # Seasonality (Q4 boost, Q1 dip)
        month = week_date.month
        if month in [10, 11, 12]:  # Q4
            seasonality = 1.15
        elif month in [1, 2, 3]:  # Q1
            seasonality = 0.90
        else:
            seasonality = 1.0

        # Generate transactions for each category
        for category, base_amount in base_amounts.items():
            if category == 'ar_collections':
                continue  # Skip for now

            # Determine transaction type
            if category in ['revenue', 'investment_income', 'other_income']:
                txn_type = 'inflow'
            else:
                txn_type = 'outflow'

            # Calculate amount with variations
            amount = base_amount * growth_factor * seasonality

            # Add randomness (less for fixed costs)
            if category in ['rent', 'insurance']:
                variance = 0.05  # 5% variance for fixed costs
            else:
                variance = 0.20  # 20% variance for variable costs

            amount *= np.random.uniform(1 - variance, 1 + variance)

            # Number of transactions per week for this category
            if category == 'revenue':
                num_txns = np.random.randint(3, 8)  # Multiple sales
            elif category == 'payroll':
                num_txns = 2  # Bi-weekly payroll
            elif category in ['rent', 'insurance']:
                num_txns = 1  # Monthly (spread across weeks)
                if week % 4 != 0:  # Only once per month
                    continue
            else:
                num_txns = np.random.randint(1, 3)

            # Create transactions
            for i in range(num_txns):
                txn_amount = amount / num_txns
                txn_date = week_date + timedelta(days=np.random.randint(0, 7))

                transactions.append({
                    'transaction_id': transaction_id,
                    'date': txn_date.strftime('%Y-%m-%d'),
                    'amount': round(txn_amount, 2),
                    'category': category,
                    'transaction_type': txn_type,
                    'description': f"{category.replace('_', ' ').title()}",
                    'customer': f"Customer_{np.random.randint(1, 50)}" if txn_type == 'inflow' else None,
                    'vendor': f"Vendor_{np.random.randint(1, 30)}" if txn_type == 'outflow' else None
                })

                transaction_id += 1

    # Create DataFrame
    df = pd.DataFrame(transactions)

    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)

    # Save to CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"✓ Generated {len(df)} transactions")
    print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"✓ Saved to: {output_path}")

    # Summary statistics
    print(f"\nSummary:")
    print(f"  Total Inflows:  ${df[df['transaction_type']=='inflow']['amount'].sum():,.2f}")
    print(f"  Total Outflows: ${df[df['transaction_type']=='outflow']['amount'].sum():,.2f}")
    print(f"  Net Cash Flow:  ${df[df['transaction_type']=='inflow']['amount'].sum() - df[df['transaction_type']=='outflow']['amount'].sum():,.2f}")

    print(f"\nTransactions by Category:")
    category_summary = df.groupby('category')['amount'].agg(['count', 'sum']).round(2)
    print(category_summary)

    return df


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  Generating Sample Transaction Data")
    print("="*70 + "\n")

    df = generate_transactions_csv(num_weeks=52)

    print("\n" + "="*70)
    print("  Sample data generation complete!")
    print("="*70 + "\n")
