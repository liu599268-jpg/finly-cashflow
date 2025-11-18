"""
QuickBooks Data Fetcher
Enhanced functions for fetching specific data from QuickBooks
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from .client import QuickBooksClient


class QuickBooksDataFetcher:
    """
    Enhanced data fetching with additional methods for specific use cases
    """

    def __init__(self, client: QuickBooksClient):
        """
        Initialize data fetcher

        Args:
            client: QuickBooksClient instance
        """
        self.client = client

    def get_all_invoices(self,
                        status: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get all invoices with optional filtering

        Args:
            status: Filter by status ('Paid', 'Unpaid', 'Pending', etc.)
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of invoice dictionaries
        """
        # Build query
        conditions = []

        if start_date:
            conditions.append(f"TxnDate >= '{start_date.strftime('%Y-%m-%d')}'")
        if end_date:
            conditions.append(f"TxnDate <= '{end_date.strftime('%Y-%m-%d')}'")

        where_clause = " AND ".join(conditions) if conditions else ""

        # Build full query
        if where_clause:
            query = f"SELECT * FROM Invoice WHERE {where_clause} ORDERBY TxnDate DESC"
        else:
            query = "SELECT * FROM Invoice ORDERBY TxnDate DESC"

        # Execute query
        result = self.client._make_request('query', params={'query': query})
        invoices = result.get('QueryResponse', {}).get('Invoice', [])

        # Filter by status if specified
        if status:
            invoices = [inv for inv in invoices if inv.get('Status') == status]

        return invoices

    def get_invoice_details(self, invoice_id: str) -> Dict:
        """
        Get detailed information for a specific invoice

        Args:
            invoice_id: QuickBooks invoice ID

        Returns:
            Invoice details dictionary
        """
        return self.client._make_request(f'invoice/{invoice_id}')

    def get_outstanding_invoices(self) -> List[Dict]:
        """
        Get all invoices with outstanding balances

        Returns:
            List of unpaid invoices
        """
        query = "SELECT * FROM Invoice WHERE Balance > '0' ORDERBY DueDate"
        result = self.client._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Invoice', [])

    def get_overdue_invoices(self) -> List[Dict]:
        """
        Get invoices that are past due

        Returns:
            List of overdue invoices
        """
        today = datetime.now().strftime('%Y-%m-%d')
        query = f"SELECT * FROM Invoice WHERE Balance > '0' AND DueDate < '{today}' ORDERBY DueDate"
        result = self.client._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Invoice', [])

    def get_customer_balance(self, customer_id: str) -> float:
        """
        Get total outstanding balance for a customer

        Args:
            customer_id: QuickBooks customer ID

        Returns:
            Total balance
        """
        query = f"SELECT * FROM Invoice WHERE CustomerRef = '{customer_id}' AND Balance > '0'"
        result = self.client._make_request('query', params={'query': query})
        invoices = result.get('QueryResponse', {}).get('Invoice', [])

        total_balance = sum(float(inv.get('Balance', 0)) for inv in invoices)
        return total_balance

    def get_revenue_summary(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """
        Get revenue summary for a date range

        Args:
            start_date: Start date (defaults to 30 days ago)
            end_date: End date (defaults to today)

        Returns:
            Dictionary with revenue metrics
        """
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(days=30))

        # Get invoices
        invoices = self.get_all_invoices(start_date=start_date, end_date=end_date)

        # Get payments
        payments = self.client.get_payments(start_date, end_date)

        total_invoiced = sum(float(inv.get('TotalAmt', 0)) for inv in invoices)
        total_collected = sum(float(pmt.get('TotalAmt', 0)) for pmt in payments)

        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_invoiced': total_invoiced,
            'total_collected': total_collected,
            'invoice_count': len(invoices),
            'payment_count': len(payments),
            'collection_rate': (total_collected / total_invoiced * 100) if total_invoiced > 0 else 0
        }

    def get_expense_summary(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """
        Get expense summary for a date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with expense metrics
        """
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(days=30))

        # Get bills
        bills = self.client.get_bills(start_date, end_date)

        # Get expenses
        expenses = self.client.get_expenses(start_date, end_date)

        total_bills = sum(float(bill.get('TotalAmt', 0)) for bill in bills)
        total_expenses = sum(float(exp.get('TotalAmt', 0)) for exp in expenses)

        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_bills': total_bills,
            'total_expenses': total_expenses,
            'total_outflows': total_bills + total_expenses,
            'bill_count': len(bills),
            'expense_count': len(expenses)
        }

    def get_account_balances_detailed(self) -> Dict[str, List[Dict]]:
        """
        Get detailed balances for all account types

        Returns:
            Dictionary with account balances by type
        """
        # Get all accounts
        query = "SELECT * FROM Account WHERE Active = true"
        result = self.client._make_request('query', params={'query': query})
        accounts = result.get('QueryResponse', {}).get('Account', [])

        # Group by account type
        balances = {
            'bank': [],
            'accounts_receivable': [],
            'accounts_payable': [],
            'other_current_assets': [],
            'fixed_assets': [],
            'other_assets': [],
            'credit_card': [],
            'current_liabilities': [],
            'long_term_liabilities': [],
            'equity': []
        }

        for account in accounts:
            account_type = account.get('AccountType', '').lower().replace(' ', '_')
            balance_info = {
                'id': account.get('Id'),
                'name': account.get('Name'),
                'account_type': account.get('AccountType'),
                'account_sub_type': account.get('AccountSubType'),
                'current_balance': float(account.get('CurrentBalance', 0)),
                'currency': account.get('CurrencyRef', {}).get('value', 'USD')
            }

            if account_type in balances:
                balances[account_type].append(balance_info)
            elif 'bank' in account_type:
                balances['bank'].append(balance_info)
            elif 'receivable' in account_type:
                balances['accounts_receivable'].append(balance_info)
            elif 'payable' in account_type:
                balances['accounts_payable'].append(balance_info)

        return balances

    def get_cash_flow_summary(self,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict:
        """
        Get comprehensive cash flow summary

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with cash flow metrics
        """
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(days=30))

        # Get revenue and expense summaries
        revenue = self.get_revenue_summary(start_date, end_date)
        expenses = self.get_expense_summary(start_date, end_date)

        # Get current cash balance
        cash_balance = self.client.get_cash_balance()

        # Calculate net cash flow
        net_cash_flow = revenue['total_collected'] - expenses['total_outflows']

        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'current_cash_balance': cash_balance,
            'total_inflows': revenue['total_collected'],
            'total_outflows': expenses['total_outflows'],
            'net_cash_flow': net_cash_flow,
            'revenue_summary': revenue,
            'expense_summary': expenses
        }

    def get_customers(self, active_only: bool = True) -> List[Dict]:
        """
        Get all customers

        Args:
            active_only: Only return active customers

        Returns:
            List of customer dictionaries
        """
        if active_only:
            query = "SELECT * FROM Customer WHERE Active = true"
        else:
            query = "SELECT * FROM Customer"

        result = self.client._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Customer', [])

    def get_vendors(self, active_only: bool = True) -> List[Dict]:
        """
        Get all vendors

        Args:
            active_only: Only return active vendors

        Returns:
            List of vendor dictionaries
        """
        if active_only:
            query = "SELECT * FROM Vendor WHERE Active = true"
        else:
            query = "SELECT * FROM Vendor"

        result = self.client._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Vendor', [])

    def get_items(self) -> List[Dict]:
        """
        Get all items/products/services

        Returns:
            List of item dictionaries
        """
        query = "SELECT * FROM Item WHERE Active = true"
        result = self.client._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Item', [])

    def get_profit_and_loss(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """
        Get Profit & Loss report

        Args:
            start_date: Report start date
            end_date: Report end date

        Returns:
            P&L report data
        """
        end_date = end_date or datetime.now()
        start_date = start_date or datetime(end_date.year, 1, 1)  # Start of year

        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }

        result = self.client._make_request('reports/ProfitAndLoss', params=params)
        return result

    def get_balance_sheet(self, as_of_date: Optional[datetime] = None) -> Dict:
        """
        Get Balance Sheet report

        Args:
            as_of_date: Date for balance sheet (defaults to today)

        Returns:
            Balance sheet data
        """
        as_of_date = as_of_date or datetime.now()

        params = {
            'date': as_of_date.strftime('%Y-%m-%d')
        }

        result = self.client._make_request('reports/BalanceSheet', params=params)
        return result

    def get_transaction_count_by_type(self,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict[str, int]:
        """
        Get count of transactions by type

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with transaction counts
        """
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(days=365))

        counts = {}

        # Count invoices
        invoices = self.get_all_invoices(start_date=start_date, end_date=end_date)
        counts['invoices'] = len(invoices)

        # Count payments
        payments = self.client.get_payments(start_date, end_date)
        counts['payments'] = len(payments)

        # Count bills
        bills = self.client.get_bills(start_date, end_date)
        counts['bills'] = len(bills)

        # Count expenses
        expenses = self.client.get_expenses(start_date, end_date)
        counts['expenses'] = len(expenses)

        counts['total'] = sum(counts.values())

        return counts
