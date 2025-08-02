"""
Google Sheet schema reader for dynamic agent configuration.
"""

from .models import SheetSchema, FieldConfig


from ..errors import SchemaError as SchemaValidationError
from ..errors import ConfigurationError as SheetAccessError


class SheetSchemaReader:
    """Reads agent configuration schema from Google Sheets rows 1-3."""
    
    def __init__(self, sheets_client):
        self.sheets_client = sheets_client
    
    def parse_sheet_schema(self, sheet_url: str) -> SheetSchema:
        """
        Parse Google Sheet rows 1-3 to extract agent schema.
        
        Expected format:
        Row 1: Field types ("user input" or "bot output")
        Row 2: Field descriptions 
        Row 3: Column names
        
        Args:
            sheet_url: URL of Google Sheet to parse
            
        Returns:
            SheetSchema with input and output fields
            
        Raises:
            SchemaValidationError: If sheet format is invalid
            SheetAccessError: If sheet cannot be accessed
        """
        try:
            # Extract sheet ID from URL
            sheet_id = self._extract_sheet_id(sheet_url)
            
            # Open the spreadsheet using gspread
            spreadsheet = self.sheets_client.open_by_key(sheet_id)
            worksheet = spreadsheet.get_worksheet(0)  # Get first worksheet
            
            # Get first 3 rows of data
            sheet_data = worksheet.get_values("A1:Z3")  # Get reasonable range
            
        except Exception as e:
            raise SheetAccessError(f"Cannot access sheet at {sheet_url}: {str(e)}")
        
        # Validate we have at least 3 rows
        if len(sheet_data) < 3:
            raise SchemaValidationError("Sheet must have at least 3 rows for schema definition")
        
        row1, row2, row3 = sheet_data[0], sheet_data[1], sheet_data[2]
        
        # Ensure all rows have same length by padding with empty strings
        max_length = max(len(row1), len(row2), len(row3))
        row1.extend([''] * (max_length - len(row1)))
        row2.extend([''] * (max_length - len(row2)))
        row3.extend([''] * (max_length - len(row3)))
        
        input_fields = []
        output_fields = []
        column_names_seen = set()
        
        # Skip first 2 columns (ID, Time) 
        for i in range(2, len(row1)):
            # Skip empty columns
            if not row3[i].strip():
                continue
                
            field_type = row1[i].strip().lower()
            description = row2[i].strip()
            column_name = row3[i].strip().replace(' ', '_')
            
            # Require descriptions for all columns except ID, Time, and Research_Plan (system columns)
            if not description and column_name.lower() not in ['id', 'time', 'research_plan']:
                raise SchemaValidationError(f"Empty description for field '{column_name}' in column {i+1}. All fields except ID, Time, and Research_Plan must have descriptions.")
            
            # Handle system columns (ID, Time, Research_Plan) - they don't need User/Bot field types
            if column_name.lower() in ['id', 'time', 'research_plan']:
                field_type = "system"  # Special type for system-managed columns
            else:
                # Normalize and validate field type for regular columns (case insensitive)
                if field_type == "user":
                    field_type = "user input"
                elif field_type == "bot":
                    field_type = "bot output"
                else:
                    raise SchemaValidationError(f"Invalid field type '{row1[i].strip()}' in column {i+1}. Must be 'User' or 'Bot'")
            
            # Check for duplicate column names
            if column_name in column_names_seen:
                raise SchemaValidationError(f"Duplicate column name '{column_name}' found")
            column_names_seen.add(column_name)
            
            field_config = FieldConfig(
                name=column_name,
                type=field_type,
                description=description,
                column_index=i
            )
            
            # Only add user input and bot output fields to schema (exclude system fields)
            if field_type == "user input":
                input_fields.append(field_config)
            elif field_type == "bot output":
                output_fields.append(field_config)
            # Skip system fields - they're not part of the input/output schema
        
        return SheetSchema(input_fields=input_fields, output_fields=output_fields)
    
    def _extract_sheet_id(self, sheet_url: str) -> str:
        """Extract Google Sheet ID from URL."""
        import re
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not match:
            raise SchemaValidationError(f"Invalid Google Sheets URL: {sheet_url}")
        return match.group(1)
