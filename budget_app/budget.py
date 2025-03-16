import json
import os
from typing import Dict, Any

import date_utils
import calculations
import validation_utils as validation

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data.json')
DEFAULT_DATA = {
    "monthly_records": [],
    "bank_balance": 0
}

def load_data() -> Dict[str, Any]:
    '''
    Load budget data from the JSON file, handling any potential issues.
    Takes care of missing files or corrupted data so the app doesn't crash on startup.
    
    Returns:
        Dictionary containing budget data with monthly records and bank balance
    '''
    try:
        if not os.path.exists(DATA_FILE):
            return DEFAULT_DATA.copy()
        
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            
            if "monthly_records" not in data:
                print("Warning: Data file is missing required fields. Using default structure.")
                return DEFAULT_DATA.copy()
            
            if "current_balance" in data and "bank_balance" not in data:
                data["bank_balance"] = data["current_balance"]
                del data["current_balance"]
            elif "bank_balance" not in data:
                data["bank_balance"] = 0
            
            try:
                normalized_data = validation.validate_and_normalize_data(data)
                return normalized_data
            except ValueError as e:
                print(f"Warning: Data normalization error - {str(e)}. Using partially normalized data.")
                return data
    except json.JSONDecodeError:
        print("Warning: Data file is corrupted. Creating a new one.")
        return DEFAULT_DATA.copy()
    except Exception as e:
        print(f"Error loading data: {e}")
        return DEFAULT_DATA.copy()

def save_data(data: Dict[str, Any]) -> bool:
    '''
    Save the budget data to the JSON file.
    Makes sure our data doesn't disappear when we close the app, even accidently.
    
    Args:
        data: Budget data with monthly records and bank balance
        
    Returns:
        True if successfully saved, False if something went wrong
    '''
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        save_data = data.copy()
        save_data["monthly_records"] = [record.copy() for record in data.get("monthly_records", [])]
        
        for record in save_data["monthly_records"]:
            record["salary"] = str(record["salary"])
            record["expenses"] = str(record["expenses"])
        
        with open(DATA_FILE, 'w') as file:
            json.dump(save_data, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def add_monthly_record(data: Dict[str, Any], month: str, amount: int, is_salary: bool) -> Dict[str, Any]:
    '''
    Add or update a monthly income/expense record.
    Handles the complicted logic of updating existing records vs creating new ones.
    
    Args:
        data: Budget data with all records
        month: Month in MM/YY format (e.g. "03/25")
        amount: The money amount (income or expense)
        is_salary: Whether this is income (True) or expense (False)
        
    Returns:
        Updated budget data dictionary
    
    Raises:
        ValueError: If input values are invalid
    '''
    try:
        amount = validation.ensure_valid_financial_input(amount)
        
        if not validation.ensure_valid_month_format(month):
            raise ValueError(f"Invalid month format: {month}. Expected MM/YY format.")
            
    except ValueError as e:
        raise ValueError(f"Invalid input for {'income' if is_salary else 'expense'} record: {str(e)}")
        
    for record in data["monthly_records"]:
        if record["month"] == month:
            if is_salary:
                record["salary"] = amount
            else:
                record["expenses"] = amount
            return data
    
    new_record = {
        "month": month,
        "salary": amount if is_salary else 0,
        "expenses": amount if not is_salary else 0
    }
    
    data["monthly_records"].append(new_record)
    
    data["monthly_records"] = calculations.sort_records_by_date(data["monthly_records"])
    
    return data

def update_bank_balance(data: Dict[str, Any], balance: int) -> Dict[str, Any]:
    '''
    Update the current bank balance amount.
    Simple but essental function to keep track of your actual money situation.
    
    Args:
        data: Budget data dictionary
        balance: New bank balance value
        
    Returns:
        Updated budget data with new balance
        
    Raises:
        ValueError: If balance is invalid
    '''
    try:
        balance = validation.ensure_valid_financial_input(balance)
    except ValueError as e:
        raise ValueError(f"Invalid bank balance: {str(e)}")
        
    data["bank_balance"] = balance
    return data

calculate_monthly_remaining = calculations.calculate_monthly_remaining
calculate_averages = calculations.calculate_averages
predict_next_month = calculations.predict_next_month
sort_records_by_date = calculations.sort_records_by_date
has_salary_data = calculations.has_salary_data
has_expense_data = calculations.has_expense_data

get_next_month = date_utils.get_current_next_month 