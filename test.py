import os
import requests

# Environment variables (Set these in GitHub Actions or manually)
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
KEY_VAULT_NAME = os.getenv("AZURE_KEY_VAULT_NAME")
SECRET_NAME = os.getenv("AZURE_SECRET_NAME")

# Azure OAuth2 Token URL
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"


def get_github_oidc_token():
    """Extracts the GitHub OIDC token dynamically"""
    request_token = os.getenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    request_url = os.getenv("ACTIONS_ID_TOKEN_REQUEST_URL")

    if not request_token or not request_url:
        print("GitHub OIDC token request details not found. Run in GitHub Actions.")
        exit(1)

    response = requests.get(
        f"{request_url}&audience=api://AzureADTokenExchange",
        headers={"Authorization": f"Bearer {request_token}"},
    )

    if response.status_code == 200:
        return response.json()["value"]
    else:
        print(f"Failed to get GitHub OIDC token: {response.text}")
        exit(1)


def get_azure_access_token(federated_token):
    """Exchanges the GitHub federated token for an Azure access token"""
    payload = {
        "client_id": CLIENT_ID,
        "grant_type": "client_credentials",  
        "client_assertion": federated_token,  
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "scope": "https://vault.azure.net/.default",
        "requested_token_use": "on_behalf_of"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get Azure access token: {response.text}")
        exit(1)


def get_key_vault_secret(access_token):
    """Fetches a secret from Azure Key Vault"""
    vault_url = f"https://{KEY_VAULT_NAME}.vault.azure.net/secrets/{SECRET_NAME}?api-version=7.3"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(vault_url, headers=headers)

    if response.status_code == 200:
        secret_value = response.json()["value"]
        print(f"Successfully fetched secret: {SECRET_NAME}")
        return secret_value
    else:
        print(f"Failed to fetch secret: {response.text}")
        exit(1)


if __name__ == "__main__":
    print("Fetching GitHub OIDC token...")
    github_oidc_token = get_github_oidc_token()

    print("Exchanging for Azure AD token...")
    azure_access_token = get_azure_access_token(github_oidc_token)

    print("Fetching secret from Azure Key Vault...")
    secret_value = get_key_vault_secret(azure_access_token)
    print(f"Secret Value: {secret_value}")
