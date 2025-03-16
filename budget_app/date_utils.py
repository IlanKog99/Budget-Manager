import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

def parse_date_input(date_str: str) -> str:
    '''
    Turns a flexible date input into our standard MM/YY format.
    Works with all kinds of date formats which makes entering data a lot eaiser.
    
    Args:
        date_str: The date string entered by the user
    
    Returns:
        Date in MM/YY format
    
    Raises:
        ValueError: If the date can't be understood
    '''
    try:
        dt = parse(date_str, fuzzy=True, default=datetime.datetime(2000, 1, 1))
        return dt.strftime("%m/%y")
    except Exception as e:
        raise ValueError(f"Could not parse date input '{date_str}': {e}")

def parse_month(month_str: str) -> datetime.datetime:
    '''
    Converts a month string into a proper datetime object.
    Handles both our MM/YY format and others like 'January 2023' or 'Jan-23'.
    
    Args:
        month_str: Month string in MM/YY format or other format
        
    Returns:
        Datetime object for the month
        
    Raises:
        ValueError: If the month string is incomprehensable
    '''
    try:
        if '/' in month_str and len(month_str.split('/')) == 2:
            month, year = month_str.split('/')
            full_year = int(f"20{year}")
            return datetime.datetime(full_year, int(month), 1)
        else:
            dt = parse(month_str, fuzzy=True, default=datetime.datetime(2000, 1, 1))
            return dt.replace(day=1)
    except Exception as e:
        raise ValueError(f"Could not parse month '{month_str}': {e}")

def format_month(dt: datetime.datetime) -> str:
    '''
    Formats a datetime object back to our MM/YY format.
    Standarizes how dates are displayed thruout the application.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        Month in MM/YY format
    '''
    return dt.strftime("%m/%y")

def get_next_month_from_string(month_str: str) -> str:
    '''
    Figures out what month comes after the given month.
    Useful for predicting future months from your existing data.
    
    Args:
        month_str: Month string like "03/25"
        
    Returns:
        Next month in MM/YY format
        
    Raises:
        ValueError: If the month string is invalid
    '''
    dt = parse_month(month_str)
    next_month = dt + relativedelta(months=1)
    return format_month(next_month)

def get_current_next_month() -> str:
    '''
    Gets the month after the current month.
    Simple shortcut to get next month without needing to calculate it yourself.
    
    Returns:
        Next month in MM/YY format
    '''
    today = datetime.datetime.now()
    next_month = today + relativedelta(months=1)
    return format_month(next_month) 