"""
TikTok OAuth flow — run this locally to get your access token.
Usage: python scripts/tiktok_auth.py
"""
import base64
import getpass
import hashlib
import json
import os
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_KEY = "awat3e9t4m1losh8"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "video.upload,video.publish"

token_result = {}

def _pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


def exchange_code(code: str, client_secret: str, code_verifier: str) -> dict:
    payload = urllib.parse.urlencode({
        "client_key": CLIENT_KEY,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }).encode()
    req = urllib.request.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def make_handler(client_secret, code_verifier):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if "code" not in params:
                self._respond(400, "<h2>Missing code parameter</h2>")
                return

            code = params["code"][0]
            print(f"\n  Code received. Exchanging for token...")

            try:
                result = exchange_code(code, client_secret, code_verifier)
                access_token = result.get("data", {}).get("access_token") or result.get("access_token")
                refresh_token = result.get("data", {}).get("refresh_token") or result.get("refresh_token")
                expires_in = result.get("data", {}).get("expires_in") or result.get("expires_in")

                token_result["access_token"] = access_token
                token_result["refresh_token"] = refresh_token

                print("\n" + "="*60)
                print("✓ ACCESS TOKEN (add to GitHub secrets as TIKTOK_ACCESS_TOKEN):")
                print(f"\n  {access_token}\n")
                if refresh_token:
                    print(f"REFRESH TOKEN (save this to re-auth later):\n  {refresh_token}\n")
                if expires_in:
                    print(f"Expires in: {expires_in} seconds ({int(expires_in)//3600}h)")
                print("="*60)

                self._respond(200, "<h2>✓ Token captured! Check your terminal.</h2><p>You can close this tab.</p>")
            except Exception as e:
                print(f"\n  Token exchange failed: {e}")
                self._respond(500, f"<h2>Error: {e}</h2>")

            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def _respond(self, code, html):
            body = html.encode()
            self.send_response(code)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    return Handler


def main():
    print("TikTok OAuth — Pupper")
    print("="*60)
    client_secret = getpass.getpass("Enter your TikTok Client Secret: ")

    code_verifier, code_challenge = _pkce_pair()

    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/?"
        + urllib.parse.urlencode({
            "client_key": CLIENT_KEY,
            "scope": SCOPES,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "state": "pupper_auth",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        })
    )

    print(f"\n  Starting server on http://localhost:8080 ...")
    server = HTTPServer(("localhost", 8080), make_handler(client_secret, code_verifier))

    print(f"  Opening TikTok auth in browser...")
    webbrowser.open(auth_url)
    print("  Authorize in the browser, then come back here.\n")

    server.serve_forever()


if __name__ == "__main__":
    main()
