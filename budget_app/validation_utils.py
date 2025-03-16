'''
Data Validation Utilities

This module handles validation and normalization of data to ensure consistent data types throughout the application.

The validation utilities provide:
1. Function to ensure financial values are valid integers
2. Functions to validate month format
3. Functions to normalize and validate budget data structure
'''

from typing import Dict, Any, Union, List
import re


def validate_and_normalize_record(record: Dict[str, Any]) -> Dict[str, int]:
    '''
    Clean up a monthly record by converting strings to numbers.
    Makes sure all data is consistent so calculatins work properly.
    
    Args:
        record: A monthly record that might have inconsistent data types
            
    Returns:
        The validated record with proper data types
        
    Raises:
        ValueError: If data can't be normalized properly
    '''
    normalized_record = record.copy()
    
    if "month" not in normalized_record:
        raise ValueError("Record is missing required 'month' field")
    
    try:
        if "salary" in normalized_record:
            normalized_record["salary"] = int(normalized_record["salary"])
        else:
            normalized_record["salary"] = 0
    except (ValueError, TypeError):
        raise ValueError(f"Invalid salary value in record for {normalized_record.get("month", "unknown")}")
    
    try:
        if "expenses" in normalized_record:
            normalized_record["expenses"] = int(normalized_record["expenses"])
        else:
            normalized_record["expenses"] = 0
    except (ValueError, TypeError):
        raise ValueError(f"Invalid expenses value in record for {normalized_record.get("month", "unknown")}")
    
    return normalized_record


def validate_and_normalize_data(data: Dict[str, Any]) -> Dict[str, Union[List[Dict[str, Any]], int]]:
    '''
    Validate and fix the entire budget data structure.
    Important to keep our data clean and usable for all of our functons.
    
    Args:
        data: The raw budget data that might have inconsistencies
        
    Returns:
        Cleaned up data with consistent types
        
    Raises:
        ValueError: If data is so badly structured it can't be fixed
    '''
    normalized_data = data.copy()
    
    if "monthly_records" not in normalized_data:
        normalized_data["monthly_records"] = []
    
    try:
        if "bank_balance" in normalized_data:
            normalized_data["bank_balance"] = int(normalized_data["bank_balance"])
        else:
            normalized_data["bank_balance"] = 0
    except (ValueError, TypeError):
        raise ValueError("Invalid bank balance value")
    
    normalized_records = []
    for record in normalized_data["monthly_records"]:
        try:
            normalized_record = validate_and_normalize_record(record)
            normalized_records.append(normalized_record)
        except ValueError as e:
            print(f"Warning: Skipped invalid record - {str(e)}")
    
    normalized_data["monthly_records"] = normalized_records
    
    return normalized_data


def ensure_valid_financial_input(value: Any) -> int:
    '''
    Make sure a financial value is a valid positive number.
    Helps prevent garbege data from creeping into our budget records.
    
    Args:
        value: The input to validate (could be string, float, or int)
        
    Returns:
        Clean integer value
        
    Raises:
        ValueError: If the value can't be converted to a positive integer
    '''
    try:
        if isinstance(value, str):
            value = value.replace(",", "").replace(" ", "")
        
        result = int(float(value))
        
        if result < 0:
            raise ValueError(f"Financial value cannot be negative: {value}")
            
        return result
    except (ValueError, TypeError):
        raise ValueError(f"Invalid financial value: {value}. Please provide a valid number.")


def ensure_valid_month_format(month: str) -> bool:
    '''
    Check if a month is in the standard MM/YY format.
    This is the strict version that enforces our internal format standrads.
    
    Args:
        month: The month string to validate
        
    Returns:
        True if it's valid, False otherwise
    '''
    pattern = r"^(0[1-9]|1[0-2])/\d{2}$"
    return bool(re.match(pattern, month))


def is_valid_month_format_lenient(month: str) -> bool:
    '''
    Check if a month is in any of the accepted input formats.
    More forgiving than the strict validator to allow users some flexibilty.
    
    Args:
        month: The month string to check
        
    Returns:
        True if valid in any acceptable format, False otherwise
    '''
    slash_pattern = r"^([1-9]|0[1-9]|1[0-2])/\d{2}$"
    dot_pattern = r"^([1-9]|0[1-9]|1[0-2])\.\d{2}$"
    
    return bool(re.match(slash_pattern, month) or re.match(dot_pattern, month)) 