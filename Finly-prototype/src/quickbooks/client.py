"""
QuickBooks API Client
Retrieves transaction data from QuickBooks Online
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .auth import QuickBooksAuth


class QuickBooksClient:
    """Client for interacting with QuickBooks Online API"""

    def __init__(self,
                 auth: Optional[QuickBooksAuth] = None,
                 company_id: Optional[str] = None):
        """
        Initialize QuickBooks client

        Args:
            auth: QuickBooksAuth instance
            company_id: QuickBooks company/realm ID
        """
        self.auth = auth or QuickBooksAuth()
        self.company_id = company_id
        self.base_url = f"{self.auth.base_url}/v3/company"

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        return {
            'Authorization': f'Bearer {self.auth.get_access_token()}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to QuickBooks API

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response JSON
        """
        url = f"{self.base_url}/{self.company_id}/{endpoint}"

        response = requests.get(
            url,
            headers=self._get_headers(),
            params=params
        )

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

        return response.json()

    def get_company_info(self) -> Dict:
        """Get company information"""
        return self._make_request('companyinfo/1')

    def get_transactions(self,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        days: int = 365) -> List[Dict]:
        """
        Get all transactions within date range

        Args:
            start_date: Start date (defaults to days ago)
            end_date: End date (defaults to today)
            days: Number of days to look back if start_date not provided

        Returns:
            List of transaction dictionaries
        """
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(days=days))

        # Get different transaction types
        invoices = self.get_invoices(start_date, end_date)
        payments = self.get_payments(start_date, end_date)
        bills = self.get_bills(start_date, end_date)
        bill_payments = self.get_bill_payments(start_date, end_date)
        expenses = self.get_expenses(start_date, end_date)

        # Combine all transactions
        all_transactions = []
        all_transactions.extend(invoices)
        all_transactions.extend(payments)
        all_transactions.extend(bills)
        all_transactions.extend(bill_payments)
        all_transactions.extend(expenses)

        # Sort by date
        all_transactions.sort(key=lambda x: x.get('TxnDate', ''))

        return all_transactions

    def get_invoices(self,
                    start_date: datetime,
                    end_date: datetime) -> List[Dict]:
        """Get invoices within date range"""
        query = f"""
            SELECT * FROM Invoice
            WHERE TxnDate >= '{start_date.strftime('%Y-%m-%d')}'
            AND TxnDate <= '{end_date.strftime('%Y-%m-%d')}'
            ORDERBY TxnDate
        """

        result = self._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Invoice', [])

    def get_payments(self,
                    start_date: datetime,
                    end_date: datetime) -> List[Dict]:
        """Get payments within date range"""
        query = f"""
            SELECT * FROM Payment
            WHERE TxnDate >= '{start_date.strftime('%Y-%m-%d')}'
            AND TxnDate <= '{end_date.strftime('%Y-%m-%d')}'
            ORDERBY TxnDate
        """

        result = self._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Payment', [])

    def get_bills(self,
                 start_date: datetime,
                 end_date: datetime) -> List[Dict]:
        """Get bills within date range"""
        query = f"""
            SELECT * FROM Bill
            WHERE TxnDate >= '{start_date.strftime('%Y-%m-%d')}'
            AND TxnDate <= '{end_date.strftime('%Y-%m-%d')}'
            ORDERBY TxnDate
        """

        result = self._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Bill', [])

    def get_bill_payments(self,
                         start_date: datetime,
                         end_date: datetime) -> List[Dict]:
        """Get bill payments within date range"""
        query = f"""
            SELECT * FROM BillPayment
            WHERE TxnDate >= '{start_date.strftime('%Y-%m-%d')}'
            AND TxnDate <= '{end_date.strftime('%Y-%m-%d')}'
            ORDERBY TxnDate
        """

        result = self._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('BillPayment', [])

    def get_expenses(self,
                    start_date: datetime,
                    end_date: datetime) -> List[Dict]:
        """Get expenses within date range"""
        query = f"""
            SELECT * FROM Purchase
            WHERE TxnDate >= '{start_date.strftime('%Y-%m-%d')}'
            AND TxnDate <= '{end_date.strftime('%Y-%m-%d')}'
            AND PaymentType = 'Cash'
            ORDERBY TxnDate
        """

        result = self._make_request('query', params={'query': query})
        return result.get('QueryResponse', {}).get('Purchase', [])

    def get_accounts_receivable(self) -> Dict:
        """Get current accounts receivable balance and aging"""
        # Get AR aging report
        query = "SELECT * FROM Invoice WHERE Balance > '0'"
        result = self._make_request('query', params={'query': query})

        invoices = result.get('QueryResponse', {}).get('Invoice', [])

        # Calculate aging buckets
        today = datetime.now()
        aging = {
            '0-30': 0,
            '31-45': 0,
            '46-60': 0,
            '60+': 0
        }

        total_ar = 0

        for invoice in invoices:
            balance = float(invoice.get('Balance', 0))
            total_ar += balance

            due_date = datetime.strptime(invoice['DueDate'], '%Y-%m-%d')
            days_past_due = (today - due_date).days

            if days_past_due <= 30:
                aging['0-30'] += balance
            elif days_past_due <= 45:
                aging['31-45'] += balance
            elif days_past_due <= 60:
                aging['46-60'] += balance
            else:
                aging['60+'] += balance

        return {
            'total_balance': total_ar,
            'aging': aging
        }

    def get_accounts_payable(self) -> float:
        """Get current accounts payable balance"""
        query = "SELECT * FROM Bill WHERE Balance > '0'"
        result = self._make_request('query', params={'query': query})

        bills = result.get('QueryResponse', {}).get('Bill', [])
        total_ap = sum(float(bill.get('Balance', 0)) for bill in bills)

        return total_ap

    def get_cash_balance(self) -> float:
        """Get current cash/bank account balances"""
        query = """
            SELECT * FROM Account
            WHERE AccountType = 'Bank'
            AND Active = true
        """

        result = self._make_request('query', params={'query': query})
        accounts = result.get('QueryResponse', {}).get('Account', [])

        total_cash = sum(
            float(account.get('CurrentBalance', 0))
            for account in accounts
        )

        return total_cash

    def test_connection(self) -> bool:
        """Test if connection to QuickBooks is working"""
        try:
            self.get_company_info()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
