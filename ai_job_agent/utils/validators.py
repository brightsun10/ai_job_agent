"""Data validation utilities for the AI job agent."""

import re
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlparse
import json


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        """Initialize validation error.
        
        Args:
            message (str): Error message
            field (str, optional): Field name that failed validation
            value: Value that failed validation
        """
        super().__init__(message)
        self.field = field
        self.value = value
        self.message = message
    
    def __str__(self):
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class DataValidator:
    """Comprehensive data validation utility."""
    
    def __init__(self, strict_mode: bool = False):
        """Initialize validator.
        
        Args:
            strict_mode (bool): If True, raises exceptions on validation failure
        """
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
        self.validation_rules = {}
    
    def _log_validation_error(self, field: str, value: Any, message: str):
        """Log validation error."""
        self.logger.warning(f"Validation failed for {field}='{value}': {message}")
    
    def _handle_validation_error(self, field: str, value: Any, message: str) -> bool:
        """Handle validation error based on strict mode."""
        self._log_validation_error(field, value, message)
        if self.strict_mode:
            raise ValidationError(message, field, value)
        return False
    
    def validate_email(self, email: str, field: str = "email") -> bool:
        """Validate email address format.
        
        Args:
            email (str): Email to validate
            field (str): Field name for error reporting
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(email, str):
            return self._handle_validation_error(field, email, "Email must be a string")
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return self._handle_validation_error(field, email, "Invalid email format")
        
        return True
    
    def validate_url(self, url: str, field: str = "url", 
                    allowed_schemes: Optional[List[str]] = None) -> bool:
        """Validate URL format.
        
        Args:
            url (str): URL to validate
            field (str): Field name for error reporting
            allowed_schemes (list, optional): Allowed URL schemes
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(url, str):
            return self._handle_validation_error(field, url, "URL must be a string")
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return self._handle_validation_error(field, url, "Invalid URL format")
            
            if allowed_schemes and parsed.scheme not in allowed_schemes:
                return self._handle_validation_error(
                    field, url, f"URL scheme must be one of: {allowed_schemes}"
                )
            
            return True
        except Exception as e:
            return self._handle_validation_error(field, url, f"URL parsing error: {e}")
    
    def validate_phone(self, phone: str, field: str = "phone", 
                      country_code: Optional[str] = None) -> bool:
        """Validate phone number format.
        
        Args:
            phone (str): Phone number to validate
            field (str): Field name for error reporting
            country_code (str, optional): Expected country code
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(phone, str):
            return self._handle_validation_error(field, phone, "Phone must be a string")
        
        # Remove common separators
        cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Basic validation - digits only, reasonable length
        if not cleaned_phone.isdigit():
            return self._handle_validation_error(field, phone, "Phone must contain only digits")
        
        if len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
            return self._handle_validation_error(field, phone, "Phone number length invalid")
        
        return True
    
    def validate_date(self, date_value: Union[str, date, datetime], 
                     field: str = "date", 
                     date_format: str = "%Y-%m-%d") -> bool:
        """Validate date value.
        
        Args:
            date_value: Date to validate
            field (str): Field name for error reporting
            date_format (str): Expected date format for string inputs
            
        Returns:
            bool: True if valid, False otherwise
        """
        if isinstance(date_value, (date, datetime)):
            return True
        
        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, date_format)
                return True
            except ValueError as e:
                return self._handle_validation_error(
                    field, date_value, f"Invalid date format, expected {date_format}"
                )
        
        return self._handle_validation_error(
            field, date_value, "Date must be string, date, or datetime object"
        )
    
    def validate_range(self, value: Union[int, float], field: str, 
                      min_val: Optional[Union[int, float]] = None,
                      max_val: Optional[Union[int, float]] = None) -> bool:
        """Validate numeric value within range.
        
        Args:
            value: Numeric value to validate
            field (str): Field name for error reporting
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(value, (int, float)):
            return self._handle_validation_error(field, value, "Value must be numeric")
        
        if min_val is not None and value < min_val:
            return self._handle_validation_error(
                field, value, f"Value must be >= {min_val}"
            )
        
        if max_val is not None and value > max_val:
            return self._handle_validation_error(
                field, value, f"Value must be <= {max_val}"
            )
        
        return True
    
    def validate_length(self, value: str, field: str,
                       min_length: Optional[int] = None,
                       max_length: Optional[int] = None) -> bool:
        """Validate string length.
        
        Args:
            value (str): String to validate
            field (str): Field name for error reporting
            min_length (int, optional): Minimum length
            max_length (int, optional): Maximum length
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(value, str):
            return self._handle_validation_error(field, value, "Value must be a string")
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            return self._handle_validation_error(
                field, value, f"Length must be >= {min_length} characters"
            )
        
        if max_length is not None and length > max_length:
            return self._handle_validation_error(
                field, value, f"Length must be <= {max_length} characters"
            )
        
        return True
    
    def validate_choice(self, value: Any, field: str, choices: List[Any]) -> bool:
        """Validate value is in allowed choices.
        
        Args:
            value: Value to validate
            field (str): Field name for error reporting
            choices (list): List of allowed values
            
        Returns:
            bool: True if valid, False otherwise
        """
        if value not in choices:
            return self._handle_validation_error(
                field, value, f"Value must be one of: {choices}"
            )
        
        return True
    
    def validate_regex(self, value: str, field: str, pattern: str, 
                      description: str = "pattern") -> bool:
        """Validate string against regex pattern.
        
        Args:
            value (str): String to validate
            field (str): Field name for error reporting
            pattern (str): Regex pattern
            description (str): Description of pattern for error messages
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(value, str):
            return self._handle_validation_error(field, value, "Value must be a string")
        
        try:
            if not re.match(pattern, value):
                return self._handle_validation_error(
                    field, value, f"Value must match {description}"
                )
            return True
        except re.error as e:
            return self._handle_validation_error(
                field, value, f"Invalid regex pattern: {e}"
            )
    
    def validate_file_path(self, path: Union[str, Path], field: str = "path",
                          must_exist: bool = False, 
                          allowed_extensions: Optional[List[str]] = None) -> bool:
        """Validate file path.
        
        Args:
            path: Path to validate
            field (str): Field name for error reporting
            must_exist (bool): Whether file must exist
            allowed_extensions (list, optional): Allowed file extensions
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            path_obj = Path(path)
            
            if must_exist and not path_obj.exists():
                return self._handle_validation_error(
                    field, path, "File does not exist"
                )
            
            if allowed_extensions:
                if path_obj.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                    return self._handle_validation_error(
                        field, path, f"File extension must be one of: {allowed_extensions}"
                    )
            
            return True
        except Exception as e:
            return self._handle_validation_error(
                field, path, f"Invalid path: {e}"
            )
    
    def validate_json(self, value: str, field: str = "json") -> bool:
        """Validate JSON string.
        
        Args:
            value (str): JSON string to validate
            field (str): Field name for error reporting
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(value, str):
            return self._handle_validation_error(field, value, "JSON must be a string")
        
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError as e:
            return self._handle_validation_error(
                field, value, f"Invalid JSON: {e}"
            )
    
    def validate_dict(self, data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> bool:
        """Validate dictionary against schema.
        
        Args:
            data (dict): Data to validate
            schema (dict): Validation schema
            
        Returns:
            bool: True if all validations pass, False otherwise
        """
        if not isinstance(data, dict):
            if self.strict_mode:
                raise ValidationError("Data must be a dictionary")
            return False
        
        all_valid = True
        
        for field, rules in schema.items():
            value = data.get(field)
            
            # Check required fields
            if rules.get('required', False) and value is None:
                self._handle_validation_error(field, value, "Field is required")
                all_valid = False
                continue
            
            # Skip validation if field is optional and not provided
            if value is None:
                continue
            
            # Apply validation rules
            for rule_name, rule_params in rules.items():
                if rule_name == 'required':
                    continue
                
                method_name = f"validate_{rule_name}"
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    if isinstance(rule_params, dict):
                        if not method(value, field, **rule_params):
                            all_valid = False
                    else:
                        if not method(value, field, rule_params):
                            all_valid = False
        
        return all_valid


# Convenience functions
def validate_email(email: str) -> bool:
    """Quick email validation."""
    return DataValidator().validate_email(email)


def validate_url(url: str) -> bool:
    """Quick URL validation."""
    return DataValidator().validate_url(url)


def validate_phone(phone: str) -> bool:
    """Quick phone validation."""
    return DataValidator().validate_phone(phone)


def is_valid_json(json_str: str) -> bool:
    """Quick JSON validation."""
    return DataValidator().validate_json(json_str)


def create_validator(strict_mode: bool = False) -> DataValidator:
    """Create a new validator instance.
    
    Args:
        strict_mode (bool): Whether to raise exceptions on validation failure
        
    Returns:
        DataValidator: Configured validator instance
    """
    return DataValidator(strict_mode=strict_mode)
