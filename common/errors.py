"""Universal error types for joey-bot."""

class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

class AnalysisError(Exception):
    """Raised when analysis execution fails."""
    pass

class SchemaError(ValidationError):
    """Raised when schema validation fails."""
    pass

class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass