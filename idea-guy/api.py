import os
from dotenv import load_dotenv

import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

load_dotenv()


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    os.getenv("GOOGLE_SHEETS_KEY_PATH"), scopes=SCOPES
)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gc = gspread.authorize(creds)
