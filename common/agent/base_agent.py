"""
Base Agent class for database-centric LLM applications.
"""

import datetime
import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

import gspread
from openai import OpenAI


class SheetSchema:
    """Defines the input and output columns for an Agent's Google Sheet."""
    
    def __init__(self, input_columns: Dict[str, str], output_columns: Dict[str, str]):
        self.input_columns = input_columns
        self.output_columns = output_columns
        self.all_columns = {**input_columns, **output_columns}
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate that input data contains all required columns."""
        return all(key in data for key in self.input_columns.keys())
    
    def validate_output(self, data: Dict[str, Any]) -> bool:
        """Validate that output data contains all required columns."""
        return all(key in data for key in self.output_columns.keys())
    
    def get_header_row(self) -> List[str]:
        """Get the complete header row for the sheet."""
        return ["ID", "Timestamp"] + list(self.input_columns.keys()) + list(self.output_columns.keys())


class BaseAgent(ABC):
    """Base class for all database-centric Agents."""
    
    def __init__(self, spreadsheet_id: str, gc: gspread.Client, openai_client: OpenAI, schema: SheetSchema):
        self.spreadsheet_id = spreadsheet_id
        self.gc = gc
        self.openai_client = openai_client
        self.schema = schema
        self.spreadsheet = None
        self.worksheet = None
        
    def _initialize_sheet(self):
        """Initialize Google Sheets connection and worksheet."""
        if not self.spreadsheet:
            self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            self.worksheet = self.spreadsheet.get_worksheet(0)
    
    def create_record(self, user_input: Dict[str, Any]) -> str:
        """Create a new record with user input data."""
        if not self.schema.validate_input(user_input):
            missing_keys = set(self.schema.input_columns.keys()) - set(user_input.keys())
            raise ValueError(f"Missing required input fields: {missing_keys}")
        
        self._initialize_sheet()
        
        # Generate unique ID and timestamp
        record_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create row with ID, timestamp, input data, and empty output columns
        row_data = [record_id, timestamp]
        
        # Add input column values
        for column in self.schema.input_columns.keys():
            row_data.append(user_input.get(column, ""))
        
        # Add empty output columns
        for column in self.schema.output_columns.keys():
            row_data.append("")
        
        # Append to sheet
        self.worksheet.append_row(row_data)
        
        return record_id
    
    def update_record(self, record_id: str, output_data: Dict[str, Any]) -> bool:
        """Update a record with computed output data."""
        if not self.schema.validate_output(output_data):
            missing_keys = set(self.schema.output_columns.keys()) - set(output_data.keys())
            raise ValueError(f"Missing required output fields: {missing_keys}")
        
        self._initialize_sheet()
        
        # Find the row with matching ID
        try:
            cell = self.worksheet.find(record_id)
            row_number = cell.row
            
            # Calculate column positions for output data
            base_col = len(["ID", "Timestamp"]) + len(self.schema.input_columns) + 1
            
            # Update each output column
            updates = []
            for i, column in enumerate(self.schema.output_columns.keys()):
                col_number = base_col + i
                value = output_data.get(column, "")
                updates.append({
                    'range': f'{gspread.utils.rowcol_to_a1(row_number, col_number)}',
                    'values': [[value]]
                })
            
            # Batch update for efficiency
            self.worksheet.batch_update(updates)
            return True
            
        except gspread.CellNotFound:
            logging.error(f"Record ID {record_id} not found in sheet")
            return False
        except Exception as e:
            logging.error(f"Error updating record {record_id}: {str(e)}")
            return False
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a complete record by ID."""
        self._initialize_sheet()
        
        try:
            cell = self.worksheet.find(record_id)
            row_number = cell.row
            row_data = self.worksheet.row_values(row_number)
            
            # Map row data to schema
            record = {}
            headers = self.schema.get_header_row()
            
            for i, header in enumerate(headers):
                if i < len(row_data):
                    record[header] = row_data[i]
                else:
                    record[header] = ""
            
            return record
            
        except gspread.CellNotFound:
            logging.error(f"Record ID {record_id} not found in sheet")
            return None
        except Exception as e:
            logging.error(f"Error retrieving record {record_id}: {str(e)}")
            return None
    
    @abstractmethod
    def get_budget_options(self, user_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return available budget options for this agent type."""
        pass
    
    @abstractmethod
    def execute_workflow(self, record_id: str, user_input: Dict[str, Any], budget_tier: str) -> Dict[str, Any]:
        """Execute the agent's workflow and return output data."""
        pass
    
    def process_request(self, user_input: Dict[str, Any], budget_tier: str) -> Dict[str, Any]:
        """Complete workflow: create record, execute, update, return result."""
        try:
            # Create record with user input
            record_id = self.create_record(user_input)
            
            # Execute workflow to compute output
            output_data = self.execute_workflow(record_id, user_input, budget_tier)
            
            # Update record with computed data
            success = self.update_record(record_id, output_data)
            
            if not success:
                raise Exception("Failed to update record with computed output")
            
            # Return complete record
            complete_record = self.get_record(record_id)
            if not complete_record:
                raise Exception("Failed to retrieve updated record")
            
            return complete_record
            
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            raise