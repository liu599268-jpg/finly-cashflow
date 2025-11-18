"""
QuickBooks OAuth 2.0 Authentication
Handles secure authentication with QuickBooks Online API
"""

import os
import json
from typing import Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path


class QuickBooksAuth:
    """Manages QuickBooks OAuth 2.0 authentication"""

    def __init__(self,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 redirect_uri: Optional[str] = None,
                 environment: str = 'sandbox'):
        """
        Initialize QuickBooks authentication

        Args:
            client_id: QuickBooks app client ID
            client_secret: QuickBooks app client secret
            redirect_uri: OAuth redirect URI
            environment: 'sandbox' or 'production'
        """
        self.client_id = client_id or os.getenv('QB_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('QB_CLIENT_SECRET')
        self.redirect_uri = redirect_uri or os.getenv('QB_REDIRECT_URI', 'http://localhost:8000/callback')
        self.environment = environment

        # API endpoints
        self.base_url = self._get_base_url()
        self.auth_url = "https://appcenter.intuit.com/connect/oauth2"
        self.token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

        # Token storage
        self.token_file = Path.home() / '.finly' / 'qb_tokens.json'
        self.token_file.parent.mkdir(exist_ok=True)

    def _get_base_url(self) -> str:
        """Get base URL based on environment"""
        if self.environment == 'production':
            return "https://quickbooks.api.intuit.com"
        return "https://sandbox-quickbooks.api.intuit.com"

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate OAuth authorization URL

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL for user to visit
        """
        state = state or self._generate_state()

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'com.intuit.quickbooks.accounting',
            'state': state
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    def _generate_state(self) -> str:
        """Generate random state for CSRF protection"""
        import secrets
        return secrets.token_urlsafe(32)

    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, str]:
        """
        Exchange authorization code for access and refresh tokens

        Args:
            authorization_code: Code received from OAuth callback

        Returns:
            Dictionary with access_token and refresh_token
        """
        import requests
        from requests.auth import HTTPBasicAuth

        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(
            self.token_url,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            data=data,
            headers={'Accept': 'application/json'}
        )

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        tokens = response.json()

        # Add expiry timestamp
        tokens['expires_at'] = (
            datetime.now() + timedelta(seconds=tokens['expires_in'])
        ).isoformat()

        # Save tokens
        self._save_tokens(tokens)

        return tokens

    def get_access_token(self) -> str:
        """
        Get valid access token (refreshes if expired)

        Returns:
            Valid access token
        """
        tokens = self._load_tokens()

        if not tokens:
            raise Exception("No tokens found. Please authenticate first.")

        # Check if token is expired
        if self._is_token_expired(tokens):
            tokens = self.refresh_access_token(tokens['refresh_token'])

        return tokens['access_token']

    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Current refresh token

        Returns:
            New tokens
        """
        import requests
        from requests.auth import HTTPBasicAuth

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        response = requests.post(
            self.token_url,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            data=data,
            headers={'Accept': 'application/json'}
        )

        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        tokens = response.json()
        tokens['expires_at'] = (
            datetime.now() + timedelta(seconds=tokens['expires_in'])
        ).isoformat()

        self._save_tokens(tokens)

        return tokens

    def _save_tokens(self, tokens: Dict[str, str]):
        """Save tokens to secure storage"""
        with open(self.token_file, 'w') as f:
            json.dump(tokens, f, indent=2)

        # Set restrictive permissions
        os.chmod(self.token_file, 0o600)

    def _load_tokens(self) -> Optional[Dict[str, str]]:
        """Load tokens from storage"""
        if not self.token_file.exists():
            return None

        with open(self.token_file, 'r') as f:
            return json.load(f)

    def _is_token_expired(self, tokens: Dict[str, str]) -> bool:
        """Check if access token is expired"""
        if 'expires_at' not in tokens:
            return True

        expiry = datetime.fromisoformat(tokens['expires_at'])
        # Add 5 minute buffer
        return datetime.now() >= (expiry - timedelta(minutes=5))

    def revoke_tokens(self):
        """Revoke and delete stored tokens"""
        tokens = self._load_tokens()

        if tokens:
            import requests
            from requests.auth import HTTPBasicAuth

            # Revoke refresh token
            requests.post(
                'https://developer.api.intuit.com/v2/oauth2/tokens/revoke',
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                data={'token': tokens['refresh_token']},
                headers={'Accept': 'application/json'}
            )

        # Delete token file
        if self.token_file.exists():
            self.token_file.unlink()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        tokens = self._load_tokens()
        return tokens is not None and not self._is_token_expired(tokens)
