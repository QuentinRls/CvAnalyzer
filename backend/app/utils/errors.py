class CVExtractionError(Exception):
    """Raised when CV content cannot be extracted or is invalid"""
    pass


class LLMExtractionError(Exception):
    """Raised when LLM fails to extract structured data"""
    pass


class ValidationError(Exception):
    """Raised when data validation fails"""
    pass
