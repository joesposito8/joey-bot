import os
import logging
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI


def get_openai_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Initialize and return an OpenAI client.

    Args:
        api_key: Optional API key. If not provided, will use OPENAI_API_KEY environment variable.

    Returns:
        OpenAI client instance

    Raises:
        ValueError: If no API key is provided and OPENAI_API_KEY environment variable is not set
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
        )

    return OpenAI(api_key=api_key)


def get_google_sheets_client(
    key_path: Optional[str] = None, scopes: Optional[list] = None
) -> gspread.Client:
    """
    Initialize and return a Google Sheets client.

    Args:
        key_path: Optional path to service account key file. If not provided, will use GOOGLE_SHEETS_KEY_PATH environment variable.
        scopes: Optional list of Google API scopes. Defaults to spreadsheets scope.

    Returns:
        gspread client instance

    Raises:
        ValueError: If no key path is provided and GOOGLE_SHEETS_KEY_PATH environment variable is not set
    """
    if key_path is None:
        key_path = os.getenv("GOOGLE_SHEETS_KEY_PATH")

    if not key_path:
        raise ValueError(
            "Google Sheets service account key path is required. Set GOOGLE_SHEETS_KEY_PATH environment variable or pass key_path parameter."
        )

    if scopes is None:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    try:
        creds = Credentials.from_service_account_file(key_path, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        logging.error(f"Failed to initialize Google Sheets client: {str(e)}")
        raise


def get_spreadsheet(
    spreadsheet_id: str, client: Optional[gspread.Client] = None
) -> gspread.Spreadsheet:
    """
    Get a Google Spreadsheet by ID.

    Args:
        spreadsheet_id: The ID of the spreadsheet to open
        client: Optional gspread client. If not provided, will create one using default settings.

    Returns:
        gspread Spreadsheet instance

    Raises:
        ValueError: If spreadsheet_id is empty
        Exception: If spreadsheet cannot be opened
    """
    if not spreadsheet_id:
        raise ValueError("Spreadsheet ID is required")

    if client is None:
        client = get_google_sheets_client()

    try:
        return client.open_by_key(spreadsheet_id)
    except Exception as e:
        logging.error(f"Failed to open spreadsheet {spreadsheet_id}: {str(e)}")
        raise
