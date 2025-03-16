'''
Budget Calculations Module

This module provides functions for performing calculations on budget data,
including sorting, filtering, and predicting future values.
'''

from typing import Dict, List, Tuple, Any

def sort_records_by_date(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    Sort monthly records by date from oldest to newest.
    Keeps your budget data nicely orginized so everything shows up in chronological order.
    
    Args:
        records: List of monthly records with month field in MM/YY format
        
    Returns:
        Sorted list of the same records
    '''
    def get_date_key(record: Dict[str, Any]) -> Tuple[int, int]:
        '''Extract year and month as integers for sorting.'''
        month = record.get("month", "00/00")
        try:
            month_num, year = map(int, month.split("/"))
            return (year, month_num)
        except (ValueError, AttributeError):
            return (0, 0)
    
    return sorted(records, key=get_date_key)

def get_existing_data_for_month(data: Dict[str, Any], month: str) -> Dict[str, Any]:
    '''
    Find data for a specific month if it exists.
    Useful when adding new records to avoid accidentaly creating duplicates.
    
    Args:
        data: Budget data dictionary
        month: Month string in MM/YY format to look for
        
    Returns:
        The monthly record dictionary or empty dict if not found
    '''
    if not isinstance(data, dict) or "monthly_records" not in data:
        return {}
    
    month = month.strip() if month else ""
    
    for record in data.get("monthly_records", []):
        if record.get("month", "").strip() == month:
            return record
    return {}

def calculate_monthly_remaining(record: Dict[str, Any]) -> int:
    '''
    Calculate how much money is left after expenses.
    The most importent calculation for any budget - income minus expenses.
    
    Args:
        record: Single monthly record with salary and expenses
        
    Returns:
        Remaining amount (can be negative if you spent more than you earned)
    '''
    try:
        income = int(record.get("salary", "0"))
    except (ValueError, TypeError):
        income = 0
        
    try:
        expenses = int(record.get("expenses", "0"))
    except (ValueError, TypeError):
        expenses = 0
        
    return income - expenses

def calculate_averages(data: Dict[str, Any]) -> Tuple[float, float]:
    '''
    Calculate average monthly income and expenses.
    Helps you understand your typical spending patterns over time.
    
    Args:
        data: Budget data dictionary with monthly records
        
    Returns:
        A tuple with (average income, average expenes)
    '''
    records = data.get("monthly_records", [])
    if not records:
        return (0.0, 0.0)
    
    total_income = 0
    total_expenses = 0
    
    for record in records:
        try:
            total_income += int(record.get("salary", "0"))
        except (ValueError, TypeError):
            pass
            
        try:
            total_expenses += int(record.get("expenses", "0"))
        except (ValueError, TypeError):
            pass
    
    return (total_income / len(records), total_expenses / len(records))

def predict_next_month(data: Dict[str, Any]) -> Tuple[int, int, int]:
    '''
    Predict next month's finances based on past data.
    Uses your financial history to help you plan for upcomming expenses and income.
    
    Args:
        data: Budget data dictionary with monthly records
        
    Returns:
        Tuple with predicted income, expenses, and net difference
    '''
    avg_income, avg_expenses = calculate_averages(data)
    predicted_income = int(avg_income)
    predicted_expenses = int(avg_expenses)
    predicted_difference = predicted_income - predicted_expenses
    
    return (predicted_income, predicted_expenses, predicted_difference)

def has_salary_data(data: Dict[str, Any]) -> bool:
    '''
    Check if any income data has been entered yet.
    Helps determine if there's enough information to make resonable predictions.
    
    Args:
        data: Budget data dictionary
        
    Returns:
        True if at least one record has income, False otherwise
    '''
    if not isinstance(data, dict) or "monthly_records" not in data:
        return False
        
    try:
        return any(int(record.get("salary", "0")) > 0 
                for record in data.get("monthly_records", []))
    except (ValueError, TypeError):
        return False

def has_expense_data(data: Dict[str, Any]) -> bool:
    '''
    Check if any expense data has been entered yet.
    Important for determining if we can show meaningfull budget reports and graphs.
    
    Args:
        data: Budget data dictionary
        
    Returns:
        True if at least one record has expenses, False otherwise
    '''
    if not isinstance(data, dict) or "monthly_records" not in data:
        return False
        
    try:
        return any(int(record.get("expenses", "0")) > 0 
                for record in data.get("monthly_records", []))
    except (ValueError, TypeError):
        return False 