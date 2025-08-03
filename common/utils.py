import os
import re
import json
import logging
from typing import List, Optional, Dict
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


def clean_json_response(text: str) -> str:
    """Clean JSON response by removing markdown formatting.

    Args:
        text: Raw response text that may contain JSON wrapped in markdown

    Returns:
        Cleaned JSON string ready for parsing
    """
    cleaned = text.strip()

    # Remove ```json and ``` markers
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    elif cleaned.startswith('```'):
        cleaned = cleaned[3:]

    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]

    return cleaned.strip()


def extract_json_from_text(text: str, expected_output: Information) -> dict | None:
    # Strategy 1: Look for JSON wrapped in ```json ... ``` blocks
    json_block_pattern = r'```json\s*(\{.*?\})\s*```'
    json_block_match = re.search(json_block_pattern, text, re.DOTALL | re.IGNORECASE)
    if json_block_match:
        try:
            parsed = json.loads(json_block_match.group(1))
            return parsed
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 2: Look for JSON wrapped in ``` ... ``` blocks (without json specifier)
    block_pattern = r'```\s*(\{.*?\})\s*```'
    block_match = re.search(block_pattern, text, re.DOTALL)
    if block_match:
        try:
            parsed = json.loads(block_match.group(1))
            return parsed
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 3: Handle escaped JSON strings (like the example you provided)
    # Look for patterns like ```json\n{...}\n``` or similar escaped formats
    escaped_json_pattern = r'```json\\n\s*(\{.*?\})\s*\\n```'
    escaped_match = re.search(escaped_json_pattern, text, re.DOTALL | re.IGNORECASE)
    if escaped_match:
        try:
            # The captured group contains the escaped JSON, so we need to unescape it
            escaped_json = escaped_match.group(1)
            # Unescape common escape sequences
            unescaped_json = (
                escaped_json.replace('\\n', '\n')
                .replace('\\"', '"')
                .replace('\\t', '\t')
            )
            parsed = json.loads(unescaped_json)
            return parsed
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 4: Look for any JSON object in the text (improved pattern)
    # This pattern is more flexible and handles nested objects better
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    json_matches = re.findall(json_pattern, text, re.DOTALL)

    # Try each potential JSON match, starting with the longest (most complete)
    for json_str in sorted(json_matches, key=len, reverse=True):
        try:
            # Clean up common issues
            cleaned_json = json_str.strip()
            # Remove any trailing commas before closing braces
            cleaned_json = re.sub(r',(\s*[}\]])', r'\1', cleaned_json)
            # Try to unescape if it looks like escaped JSON
            if '\\n' in cleaned_json or '\\"' in cleaned_json:
                cleaned_json = (
                    cleaned_json.replace('\\n', '\n')
                    .replace('\\"', '"')
                    .replace('\\t', '\t')
                )
            parsed = json.loads(cleaned_json)
            return parsed
        except (json.JSONDecodeError, ValueError):
            continue

    # Strategy 5: Try to extract key-value pairs and construct a dict
    try:
        # Look for patterns like "Key": value or Key: value
        kv_pattern = r'"?([A-Za-z_][A-Za-z0-9_]*)"?\s*:\s*"?([^",\n\r}]+)"?'
        kv_matches = re.findall(kv_pattern, text)
        if kv_matches:
            result = {}
            for key, value in kv_matches:
                # Clean up the value
                value = value.strip().strip('"\'')
                # Try to convert numeric values
                try:
                    if '.' in value:
                        result[key] = float(value)
                    else:
                        result[key] = int(value)
                except ValueError:
                    result[key] = value
            if result:
                return result
    except Exception:
        pass

    return None
