from __future__ import print_function
import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # localhost only

from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/drive"]
REDIRECT_URI = "http://localhost:8000/auth/google/callback"

def main():
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found")
        return

    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    print("\n🔐 Open this URL in your browser:\n")
    print(auth_url)

    print("\n👉 After clicking Allow, COPY the FULL URL from browser")
    redirect_response = input("\n🔁 Paste FULL redirect URL here:\n")

    flow.fetch_token(authorization_response=redirect_response)
    creds = flow.credentials

    with open("oauth_token.json", "w") as token:
        token.write(creds.to_json())

    print("\n✅ New OAuth token created")
    print("📁 Saved as oauth_token.json")

if __name__ == "__main__":
    main()
