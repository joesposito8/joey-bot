import os
import logging
from typing import Optional, Dict
from dataclasses import dataclass

import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI


@dataclass
class Information:
    columns: Dict[str, str]

    def __init__(self, data: Optional[Dict[str, str]] = None):
        if data is None:
            self.content = {column: "" for column in self.columns.keys()}
        else:
            for column in self.columns.keys():
                if column not in data:
                    raise ValueError(f"Missing {column} in data")
            self.content = {column: data[column] for column in self.columns.keys()}


def get_openai_client(api_key: Optional[str] = None) -> OpenAI:
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
    if not spreadsheet_id:
        raise ValueError("Spreadsheet ID is required")

    if client is None:
        client = get_google_sheets_client()

    try:
        return client.open_by_key(spreadsheet_id)
    except Exception as e:
        logging.error(f"Failed to open spreadsheet {spreadsheet_id}: {str(e)}")
        raise
