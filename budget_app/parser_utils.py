'''
Command Parser Utilities

This module handles parsing of user input commands for the budget application.
It converts text-based input into structured command objects.

Extending the command parser:
To add a new command, follow these steps:
1. Add a new regex pattern to recognize the command format
2. Process the captured groups to extract parameters
3. Add your new command to the result object with appropriate fields
4. If needed, add new error codes to the get_error_message function
'''

import re
from typing import Dict, Any
import validation_utils as validation

# Command result type definitions
CommandResult = Dict[str, Any]


def validate_month_format(month: str) -> bool:
    '''
    Check if the month format is one of the supported formats.
    We allow several vatiations to make it easier to enter data.
    
    Args:
        month: Month string to check
        
    Returns:
        True if valid format, False if invalid
    '''
    return validation.is_valid_month_format_lenient(month)


def normalize_month_format(month: str) -> str:
    '''
    Convert various month formats to the standard MM/YY format.
    Handles inputs like 3/25, 03/25, 3.25, or 03.25 and makes them consistent.
    
    Args:
        month: Month string in any supported format
        
    Returns:
        Month in standard MM/YY format
    '''
    if '.' in month:
        parts = month.split('.')
        month_part = parts[0]
        year_part = parts[1]
        month = f"{month_part}/{year_part}"
    else:
        parts = month.split('/')
        month_part = parts[0]
        year_part = parts[1]
        
    if len(month_part) == 1:
        return f"0{month_part}/{year_part}"
    
    return f"{month_part}/{year_part}"


def parse_command(user_input: str) -> CommandResult:
    '''
    Turn user text input into structured command objects.
    Interprets what the user is trying to do based on the text they type.
    
    Args:
        user_input: Raw text entered by the user
        
    Returns:
        A dictionary with parsed command information like:
        - command: The recognized command type
        - amount: Financial amount if applicable
        - month: Month in MM/YY format if applicable
        - error: Error code if something went wrong
        - menu_option: Menu option number if applicable
    '''
    result: CommandResult = {
        "command": None,
        "amount": None,
        "month": None,
        "error": None,
        "menu_option": None
    }
    
    user_input = ' '.join(user_input.split()).strip()
    
    if not user_input:
        result["command"] = "menu"
        return result
    
    if re.match(r'^\d+$', user_input):
        result["command"] = "menu_option"
        result["menu_option"] = int(user_input)
        return result
        
    add_match = re.match(r'^add\s+(.+)$', user_input, re.IGNORECASE)
    if add_match:
        add_content = add_match.group(1)
        nested_result = parse_command(add_content)
        
        if nested_result["command"] is None or nested_result["error"] is not None:
            result["command"] = None
            result["error"] = "invalid_command"
            return result
            
        return nested_result
    
    bank_match = re.match(r'^bank\s+(.+)$', user_input, re.IGNORECASE)
    if bank_match:
        amount_str = bank_match.group(1).strip()
        try:
            amount = validation.ensure_valid_financial_input(amount_str)
            result["command"] = "bank"
            result["amount"] = amount
            return result
        except ValueError:
            result["command"] = None
            result["error"] = "invalid_amount"
            return result
    
    if re.match(r'^bank\b', user_input, re.IGNORECASE):
        result["command"] = None
        result["error"] = "invalid_command"
        return result
    
    update_match = re.match(r'^([+\-])\s*(\d+)\s+([0-9]+[/\.]\d{2})$', user_input)
    if update_match:
        sign = update_match.group(1)
        amount_str = update_match.group(2).strip()
        month = update_match.group(3).strip()
        
        try:
            amount = validation.ensure_valid_financial_input(amount_str)
        except ValueError:
            result["command"] = None
            result["error"] = "invalid_amount"
            return result
        
        if not validate_month_format(month):
            result["command"] = None
            result["error"] = "invalid_date"
            return result
        
        month = normalize_month_format(month)
        
        if sign == '+':
            result["command"] = "income"
            result["amount"] = amount
            result["month"] = month
        else:
            result["command"] = "expense"
            result["amount"] = amount
            result["month"] = month
            
        return result
    
    if (re.match(r'^[+\-]\s*\d+$', user_input) or 
        re.match(r'^[+\-][^\d].*$', user_input) or 
        re.match(r'^[+\-].*\d+/\d+$', user_input)):
        result["command"] = None
        result["error"] = "invalid_command"
        return result
    
    if user_input.lower() in ['', 'save', 'return', 'menu', 'main']:
        result["command"] = "menu"
        return result
    
    if user_input.lower() == 'exit':
        result["command"] = "exit"
        return result
    
    if user_input.lower() == 'graph':
        result["command"] = "graph"
        return result
    
    if user_input.lower() == 'view':
        result["command"] = "view"
        return result
    
    if user_input.lower() == 'add':
        result["command"] = "add"
        return result
    
    result["command"] = None
    result["error"] = "invalid_command"
    return result


def get_error_message(error_code: str) -> str:
    '''
    Convert error codes into friendly messages the user can understand.
    Helps make the application more useable by providing helpfull feedback.
    
    Args:
        error_code: The error code from the command parser
        
    Returns:
        User-friendly error message explaining what went wrong
    '''
    error_messages = {
        "invalid_command": "Invalid command format. Please use one of the valid commands or menu options.",
        "invalid_date": "Invalid date format. Month must be between 1-12 and year should be in YY format (e.g., 3/25 or 3.25).",
        "invalid_amount": "Invalid amount format. Please enter a valid number (e.g., 1000).",
    }
    
    return error_messages.get(error_code, "An unknown error occurred.") 