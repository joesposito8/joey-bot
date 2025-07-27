"""
Tests for Google Sheet schema reader functionality.
"""

import pytest
from unittest.mock import Mock, patch
from common.config.sheet_schema_reader import SheetSchemaReader, SchemaValidationError, SheetAccessError
from common.config.models import SheetSchema, FieldConfig


class TestSheetSchemaReader:
    
    def test_parse_valid_sheet_schema(self, mock_google_sheets_client, valid_sheet_data):
        """Test parsing valid sheet schema returns correct SheetSchema."""
        # Mock sheets client to return valid data
        mock_google_sheets_client.get_sheet_data.return_value = valid_sheet_data
        
        reader = SheetSchemaReader(mock_google_sheets_client)
        
        result = reader.parse_sheet_schema("test_sheet_url")
        
        assert isinstance(result, SheetSchema)
        assert len(result.input_fields) == 3  # Idea_Overview, Deliverable, Motivation
        assert len(result.output_fields) == 2  # Novelty_Rating, Novelty_Rationale
        assert result.input_fields[0].name == "Idea_Overview"
        assert result.input_fields[0].description == "Brief desc"
    
    def test_missing_required_rows(self, mock_google_sheets_client):
        """Test sheet with insufficient rows raises error."""
        incomplete_data = [
            ["ID", "Time", "user input"],
            ["ID", "Time", "Brief desc"]
            # Missing row 3
        ]
        
        mock_google_sheets_client.get_sheet_data.return_value = incomplete_data
        reader = SheetSchemaReader(mock_google_sheets_client)
        
        with pytest.raises(SchemaValidationError, match="Sheet must have at least 3 rows"):
            reader.parse_sheet_schema("test_sheet_url")
    
    def test_invalid_field_type(self, mock_google_sheets_client):
        """Test invalid field type in row 1 raises error."""
        invalid_data = [
            ["ID", "Time", "invalid_type", "user input"],  # invalid_type not allowed
            ["ID", "Time", "Brief desc", "What will"],
            ["ID", "Time", "Idea_Overview", "Deliverable"]
        ]
        
        mock_google_sheets_client.get_sheet_data.return_value = invalid_data
        reader = SheetSchemaReader(mock_google_sheets_client)
        
        with pytest.raises(SchemaValidationError, match="Invalid field type"):
            reader.parse_sheet_schema("test_sheet_url")
    
    def test_empty_field_descriptions(self, mock_google_sheets_client):
        """Test empty descriptions use default values."""
        data_with_empty_desc = [
            ["ID", "Time", "user input", "bot output"],
            ["ID", "Time", "", ""],  # Empty descriptions
            ["ID", "Time", "Idea_Overview", "Result"]
        ]
        
        mock_google_sheets_client.get_sheet_data.return_value = data_with_empty_desc
        reader = SheetSchemaReader(mock_google_sheets_client)
        
        result = reader.parse_sheet_schema("test_sheet_url")
        
        # Should use default descriptions when empty
        assert "Idea_Overview" in result.input_fields[0].description
        assert "Result" in result.output_fields[0].description
    
    def test_duplicate_column_names(self, mock_google_sheets_client):
        """Test duplicate column names raise error."""
        duplicate_data = [
            ["ID", "Time", "user input", "user input"],
            ["ID", "Time", "Brief desc", "What will"],
            ["ID", "Time", "Idea_Overview", "Idea_Overview"]  # Duplicate name
        ]
        
        mock_google_sheets_client.get_sheet_data.return_value = duplicate_data
        reader = SheetSchemaReader(mock_google_sheets_client)
        
        with pytest.raises(SchemaValidationError, match="Duplicate column name"):
            reader.parse_sheet_schema("test_sheet_url")
    
    def test_mixed_input_output_ordering(self, mock_google_sheets_client):
        """Test fields not grouped by type are correctly separated."""
        mixed_data = [
            ["ID", "Time", "user input", "bot output", "user input", "bot output"],
            ["ID", "Time", "Brief desc", "How novel", "What will", "Detailed"],
            ["ID", "Time", "Idea_Overview", "Novelty_Rating", "Deliverable", "Analysis"]
        ]
        
        mock_google_sheets_client.get_sheet_data.return_value = mixed_data
        reader = SheetSchemaReader(mock_google_sheets_client)
        
        result = reader.parse_sheet_schema("test_sheet_url")
        
        # Should correctly separate input/output fields
        assert len(result.input_fields) == 2  # Idea_Overview, Deliverable
        assert len(result.output_fields) == 2  # Novelty_Rating, Analysis
        
        # Verify field names
        input_names = [field.name for field in result.input_fields]
        output_names = [field.name for field in result.output_fields]
        assert "Idea_Overview" in input_names
        assert "Deliverable" in input_names
        assert "Novelty_Rating" in output_names
        assert "Analysis" in output_names