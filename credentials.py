""" Management of GCP credentials"""
import os
import google.auth
from google.oauth2 import service_account

# Flag for specifying that we are in a GAE instance
GAE = os.environ.get('GAE_INSTANCE') is not None
# Flag for the presence of service account credentials
GAC = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is not None


def fetch() -> tuple:
    """ Returns the active GCP project ID and credentials.

        This function first establishes whether or not it is running on a GAE
        instance, if so the default authentication is used. If not, the
        environmental variable GOOGLE_APPLICATION_CREDENTIALS is analysed for
        relevant credentials.

        Returns:
            (tuple): A tuple of (credentials, gcp project ID)
    """
    if GAE:    # If in GAE, use default authentication
        return google.auth.default()
    elif GAC:  # Otherwise, look for service account credentials
        creds = service_account.Credentials.from_service_account_file(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        )
        return creds, creds.project_id
    else:
        msg = "Cannot find appropriate credentials, is GOOGLE_APPLICATION_CREDENTIALS set?"
        raise RuntimeError(msg)


def project_id() -> str:
    """ Returns the ID of the GCP project used for accessing BigQuery."""
    CREDENTIALS, PROJECT_ID = fetch()
    return PROJECT_ID
