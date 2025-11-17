"""
QuickBooks OAuth Callback Server
Handles the OAuth 2.0 authorization flow
"""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional, Callable
import threading


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""

    callback_code: Optional[str] = None
    callback_realm_id: Optional[str] = None
    callback_error: Optional[str] = None

    def do_GET(self):
        """Handle GET request from OAuth callback"""
        # Parse the URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Extract authorization code and realm ID
        if 'code' in query_params:
            OAuthCallbackHandler.callback_code = query_params['code'][0]
            OAuthCallbackHandler.callback_realm_id = query_params.get('realmId', [None])[0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Finly - QuickBooks Connected</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }
                    h1 {
                        color: #2e7d32;
                        margin-bottom: 20px;
                    }
                    .checkmark {
                        font-size: 72px;
                        color: #2e7d32;
                        margin-bottom: 20px;
                    }
                    p {
                        color: #666;
                        line-height: 1.6;
                    }
                    .company-id {
                        background: #f5f5f5;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 20px 0;
                        font-family: monospace;
                        font-size: 14px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="checkmark">✓</div>
                    <h1>Successfully Connected!</h1>
                    <p>Your QuickBooks account has been successfully connected to Finly.</p>
                    <div class="company-id">
                        Company ID: {realm_id}
                    </div>
                    <p>You can close this window and return to Finly.</p>
                </div>
            </body>
            </html>
            """.format(realm_id=OAuthCallbackHandler.callback_realm_id or 'N/A')

            self.wfile.write(html.encode())

        elif 'error' in query_params:
            OAuthCallbackHandler.callback_error = query_params['error'][0]

            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Finly - Connection Failed</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }
                    h1 {
                        color: #d32f2f;
                        margin-bottom: 20px;
                    }
                    .error-icon {
                        font-size: 72px;
                        color: #d32f2f;
                        margin-bottom: 20px;
                    }
                    p {
                        color: #666;
                        line-height: 1.6;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error-icon">✗</div>
                    <h1>Connection Failed</h1>
                    <p>There was an error connecting to QuickBooks:</p>
                    <p><strong>{error}</strong></p>
                    <p>Please try again.</p>
                </div>
            </body>
            </html>
            """.format(error=OAuthCallbackHandler.callback_error)

            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class QuickBooksOAuthServer:
    """OAuth callback server for QuickBooks authentication"""

    def __init__(self, port: int = 8000):
        """
        Initialize OAuth server

        Args:
            port: Port to run callback server on
        """
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None

    def start_auth_flow(self, auth_url: str) -> tuple[Optional[str], Optional[str]]:
        """
        Start OAuth authentication flow

        Args:
            auth_url: Authorization URL to open in browser

        Returns:
            Tuple of (authorization_code, realm_id)
        """
        # Reset callback data
        OAuthCallbackHandler.callback_code = None
        OAuthCallbackHandler.callback_realm_id = None
        OAuthCallbackHandler.callback_error = None

        # Start server
        self.server = HTTPServer(('localhost', self.port), OAuthCallbackHandler)
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Open browser
        print(f"\n{'='*60}")
        print("Opening browser for QuickBooks authentication...")
        print(f"{'='*60}\n")
        print(f"If the browser doesn't open automatically, visit:")
        print(f"\n{auth_url}\n")

        webbrowser.open(auth_url)

        # Wait for callback
        print("Waiting for authorization...")

        # Keep checking until we get a response
        import time
        timeout = 300  # 5 minutes
        elapsed = 0

        while elapsed < timeout:
            if OAuthCallbackHandler.callback_code or OAuthCallbackHandler.callback_error:
                break
            time.sleep(0.5)
            elapsed += 0.5

        # Stop server
        self.stop()

        if OAuthCallbackHandler.callback_error:
            raise Exception(f"OAuth error: {OAuthCallbackHandler.callback_error}")

        if not OAuthCallbackHandler.callback_code:
            raise Exception("Authorization timeout - no response received")

        return OAuthCallbackHandler.callback_code, OAuthCallbackHandler.callback_realm_id

    def _run_server(self):
        """Run the HTTP server"""
        self.server.serve_forever()

    def stop(self):
        """Stop the OAuth callback server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None


def authenticate_quickbooks(auth_instance) -> tuple[str, str]:
    """
    Helper function to authenticate with QuickBooks

    Args:
        auth_instance: QuickBooksAuth instance

    Returns:
        Tuple of (access_token, realm_id)
    """
    from .auth import QuickBooksAuth

    # Generate authorization URL
    auth_url = auth_instance.get_authorization_url()

    # Start OAuth server and get authorization code
    oauth_server = QuickBooksOAuthServer(port=8000)
    auth_code, realm_id = oauth_server.start_auth_flow(auth_url)

    print(f"\n✓ Authorization received!")
    print(f"  Company ID: {realm_id}")

    # Exchange code for tokens
    print("\nExchanging authorization code for access token...")
    tokens = auth_instance.exchange_code_for_tokens(auth_code)

    print(f"✓ Access token received!")
    print(f"\n{'='*60}")
    print("QuickBooks authentication successful!")
    print(f"{'='*60}\n")

    return tokens['access_token'], realm_id
