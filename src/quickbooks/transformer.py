"""
QuickBooks Data Transformer
Converts QuickBooks transaction format to Finly internal format
"""

from datetime import datetime
from typing import List, Dict
from enum import Enum


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


# QuickBooks to Finly category mapping
QB_CATEGORY_MAP = {
    # Revenue mappings
    'Sales': CashFlowCategory.REVENUE,
    'Income': CashFlowCategory.REVENUE,
    'Service Income': CashFlowCategory.REVENUE,
    'Product Income': CashFlowCategory.REVENUE,

    # Expense mappings
    'Cost of Goods Sold': CashFlowCategory.COGS,
    'Payroll Expenses': CashFlowCategory.PAYROLL,
    'Salaries': CashFlowCategory.PAYROLL,
    'Wages': CashFlowCategory.PAYROLL,
    'Rent': CashFlowCategory.RENT,
    'Rent Expense': CashFlowCategory.RENT,
    'Marketing': CashFlowCategory.MARKETING,
    'Advertising': CashFlowCategory.MARKETING,
    'Technology': CashFlowCategory.TECHNOLOGY,
    'Software': CashFlowCategory.TECHNOLOGY,
    'SaaS': CashFlowCategory.TECHNOLOGY,
    'Insurance': CashFlowCategory.INSURANCE,
    'Utilities': CashFlowCategory.UTILITIES,
    'Professional Services': CashFlowCategory.PROFESSIONAL_SERVICES,
    'Legal': CashFlowCategory.PROFESSIONAL_SERVICES,
    'Accounting': CashFlowCategory.PROFESSIONAL_SERVICES,
    'Travel': CashFlowCategory.TRAVEL,
    'Office Supplies': CashFlowCategory.OFFICE_SUPPLIES,
}


class QuickBooksTransformer:
    """Transforms QuickBooks data to Finly format"""

    def __init__(self, custom_category_map: Dict[str, CashFlowCategory] = None):
        """
        Initialize transformer

        Args:
            custom_category_map: Optional custom category mappings
        """
        self.category_map = QB_CATEGORY_MAP.copy()
        if custom_category_map:
            self.category_map.update(custom_category_map)

    def transform_transactions(self, qb_transactions: List[Dict]) -> List[Dict]:
        """
        Transform list of QuickBooks transactions

        Args:
            qb_transactions: List of QuickBooks transaction dicts

        Returns:
            List of Finly transaction dicts
        """
        finly_transactions = []

        for qb_txn in qb_transactions:
            # Determine transaction type from QuickBooks object
            txn_type = self._get_transaction_type(qb_txn)

            if txn_type == 'Invoice':
                finly_transactions.extend(self._transform_invoice(qb_txn))
            elif txn_type == 'Payment':
                finly_transactions.extend(self._transform_payment(qb_txn))
            elif txn_type == 'Bill':
                finly_transactions.extend(self._transform_bill(qb_txn))
            elif txn_type == 'BillPayment':
                finly_transactions.extend(self._transform_bill_payment(qb_txn))
            elif txn_type == 'Purchase':
                finly_transactions.extend(self._transform_expense(qb_txn))

        return finly_transactions

    def _get_transaction_type(self, qb_txn: Dict) -> str:
        """Determine QuickBooks transaction type"""
        # QuickBooks transactions have a type indicator
        for key in ['Invoice', 'Payment', 'Bill', 'BillPayment', 'Purchase']:
            if key in str(type(qb_txn)) or qb_txn.get('domain') == key:
                return key

        # Fallback: check which fields are present
        if 'CustomerRef' in qb_txn and 'TotalAmt' in qb_txn:
            if qb_txn.get('Balance', 0) > 0:
                return 'Invoice'
            else:
                return 'Payment'
        elif 'VendorRef' in qb_txn:
            return 'Bill'

        return 'Unknown'

    def _transform_invoice(self, invoice: Dict) -> List[Dict]:
        """Transform QuickBooks invoice"""
        return [{
            'date': self._parse_date(invoice.get('TxnDate')),
            'amount': float(invoice.get('TotalAmt', 0)),
            'category': CashFlowCategory.REVENUE.value,
            'transaction_type': TransactionType.INFLOW.value,
            'description': f"Invoice #{invoice.get('DocNumber', 'N/A')}",
            'customer': invoice.get('CustomerRef', {}).get('name'),
            'vendor': None,
            'reference_id': invoice.get('Id'),
            'reference_type': 'invoice'
        }]

    def _transform_payment(self, payment: Dict) -> List[Dict]:
        """Transform QuickBooks payment"""
        return [{
            'date': self._parse_date(payment.get('TxnDate')),
            'amount': float(payment.get('TotalAmt', 0)),
            'category': CashFlowCategory.AR_COLLECTIONS.value,
            'transaction_type': TransactionType.INFLOW.value,
            'description': 'Payment received',
            'customer': payment.get('CustomerRef', {}).get('name'),
            'vendor': None,
            'reference_id': payment.get('Id'),
            'reference_type': 'payment'
        }]

    def _transform_bill(self, bill: Dict) -> List[Dict]:
        """Transform QuickBooks bill"""
        transactions = []

        # Process line items to categorize expenses
        for line in bill.get('Line', []):
            if line.get('DetailType') == 'AccountBasedExpenseLineDetail':
                detail = line.get('AccountBasedExpenseLineDetail', {})
                amount = float(line.get('Amount', 0))
                account_name = detail.get('AccountRef', {}).get('name', '')

                # Map to category
                category = self._map_category(account_name)

                transactions.append({
                    'date': self._parse_date(bill.get('TxnDate')),
                    'amount': amount,
                    'category': category.value,
                    'transaction_type': TransactionType.OUTFLOW.value,
                    'description': f"{account_name}",
                    'customer': None,
                    'vendor': bill.get('VendorRef', {}).get('name'),
                    'reference_id': bill.get('Id'),
                    'reference_type': 'bill'
                })

        # If no line items, create single transaction
        if not transactions:
            transactions.append({
                'date': self._parse_date(bill.get('TxnDate')),
                'amount': float(bill.get('TotalAmt', 0)),
                'category': CashFlowCategory.OTHER_EXPENSES.value,
                'transaction_type': TransactionType.OUTFLOW.value,
                'description': 'Bill payment',
                'customer': None,
                'vendor': bill.get('VendorRef', {}).get('name'),
                'reference_id': bill.get('Id'),
                'reference_type': 'bill'
            })

        return transactions

    def _transform_bill_payment(self, bill_payment: Dict) -> List[Dict]:
        """Transform QuickBooks bill payment"""
        return [{
            'date': self._parse_date(bill_payment.get('TxnDate')),
            'amount': float(bill_payment.get('TotalAmt', 0)),
            'category': CashFlowCategory.AP_PAYMENTS.value,
            'transaction_type': TransactionType.OUTFLOW.value,
            'description': 'Bill payment',
            'customer': None,
            'vendor': bill_payment.get('VendorRef', {}).get('name'),
            'reference_id': bill_payment.get('Id'),
            'reference_type': 'bill_payment'
        }]

    def _transform_expense(self, expense: Dict) -> List[Dict]:
        """Transform QuickBooks expense/purchase"""
        transactions = []

        # Process line items
        for line in expense.get('Line', []):
            if line.get('DetailType') == 'AccountBasedExpenseLineDetail':
                detail = line.get('AccountBasedExpenseLineDetail', {})
                amount = float(line.get('Amount', 0))
                account_name = detail.get('AccountRef', {}).get('name', '')

                category = self._map_category(account_name)

                transactions.append({
                    'date': self._parse_date(expense.get('TxnDate')),
                    'amount': amount,
                    'category': category.value,
                    'transaction_type': TransactionType.OUTFLOW.value,
                    'description': f"{account_name}",
                    'customer': None,
                    'vendor': expense.get('EntityRef', {}).get('name'),
                    'reference_id': expense.get('Id'),
                    'reference_type': 'expense'
                })

        if not transactions:
            transactions.append({
                'date': self._parse_date(expense.get('TxnDate')),
                'amount': float(expense.get('TotalAmt', 0)),
                'category': CashFlowCategory.OTHER_EXPENSES.value,
                'transaction_type': TransactionType.OUTFLOW.value,
                'description': 'Expense',
                'customer': None,
                'vendor': expense.get('EntityRef', {}).get('name'),
                'reference_id': expense.get('Id'),
                'reference_type': 'expense'
            })

        return transactions

    def _map_category(self, qb_category: str) -> CashFlowCategory:
        """Map QuickBooks category to Finly category"""
        # Try exact match
        if qb_category in self.category_map:
            return self.category_map[qb_category]

        # Try partial match
        qb_lower = qb_category.lower()
        for qb_key, finly_category in self.category_map.items():
            if qb_key.lower() in qb_lower or qb_lower in qb_key.lower():
                return finly_category

        # Default to other expenses
        return CashFlowCategory.OTHER_EXPENSES

    def _parse_date(self, date_str: str) -> str:
        """Parse QuickBooks date string"""
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.isoformat()
        except:
            return datetime.now().isoformat()

    def get_historical_summary(self, transactions: List[Dict]) -> Dict:
        """
        Generate summary statistics from historical transactions

        Args:
            transactions: List of Finly transactions

        Returns:
            Dictionary with summary statistics
        """
        if not transactions:
            return {
                'total_transactions': 0,
                'total_inflows': 0,
                'total_outflows': 0,
                'net_cash_flow': 0,
                'date_range': None
            }

        inflows = [t for t in transactions if t['transaction_type'] == TransactionType.INFLOW.value]
        outflows = [t for t in transactions if t['transaction_type'] == TransactionType.OUTFLOW.value]

        total_inflows = sum(t['amount'] for t in inflows)
        total_outflows = sum(t['amount'] for t in outflows)

        dates = [datetime.fromisoformat(t['date']) for t in transactions]

        return {
            'total_transactions': len(transactions),
            'total_inflows': total_inflows,
            'total_outflows': total_outflows,
            'net_cash_flow': total_inflows - total_outflows,
            'date_range': {
                'start': min(dates).isoformat(),
                'end': max(dates).isoformat(),
                'days': (max(dates) - min(dates)).days
            },
            'categories': self._summarize_by_category(transactions)
        }

    def _summarize_by_category(self, transactions: List[Dict]) -> Dict:
        """Summarize transactions by category"""
        summary = {}

        for txn in transactions:
            category = txn['category']
            if category not in summary:
                summary[category] = {
                    'count': 0,
                    'total': 0
                }

            summary[category]['count'] += 1
            summary[category]['total'] += txn['amount']

        return summary
