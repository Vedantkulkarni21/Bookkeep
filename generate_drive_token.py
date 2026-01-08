from __future__ import print_function
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

def main():
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found in current folder")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
    )

    creds = flow.run_local_server(port=0)

    with open("oauth_token.json", "w") as token:
        token.write(creds.to_json())

    print("\n✅ New OAuth token created")
    print("📁 Saved as oauth_token.json")
    print("👉 Uploads will now go to THIS Google account")

if __name__ == "__main__":
    main()

