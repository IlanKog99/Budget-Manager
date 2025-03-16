import os
from typing import Dict, Tuple, Optional

import budget
import calculations
import date_utils
import parser_utils as parser
import visualization

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"

def clear_screen() -> None:
    '''Clear the terminal screen for a fresh display.'''
    os.system("cls" if os.name == "nt" else "clear")

def display_welcome() -> None:
    '''Show a welcome message when starting the app.'''
    print(f"{PURPLE}{"=" * 50}")
    print(f"{PURPLE}           Monthly Budget Management App")
    print(f"{"=" * 50}{RESET}")
    print()

def display_main_menu() -> None:
    '''Display the main menu options.'''
    print(f"\n{PURPLE}===== Main Menu ====={RESET}\n")
    print("1. View Budget Data")
    print("2. Add or Update Data")
    print("3. Save and Exit")
    
    print("\nOr use one of the following commands:")
    print("  - 'view' - Go to View Budget Data menu")
    print("  - 'add' - Go to Add Data menu")
    print("  - 'add [+/-][amount] [month/year]' - Add data directly (e.g., add +3000 3/25 or add +3000 3.25)")
    print("  - 'bank [amount]' - Update bank balance (e.g., bank 12000)")
    print("  - 'graph' - View graphs")
    print("  - 'exit' - Save and exit")
    
    print(f"\n{PURPLE}>>>{RESET} ", end="")

def display_view_menu(current_view: str = "summary") -> None:
    '''Display the view menu options based on the current view.'''
    print(f"\n{PURPLE}===== View Options ====={RESET}\n")
    
    # Conditional display of menu options based on current view
    if current_view == "summary":
        print("1. View Monthly Records")
    else:  # records view
        print("1. View Budget Summary")
        
    print("2. View Graphs")
    print("3. Return to Main Menu")
    print("4. Save and Exit")
    
    print("\nOr use one of the following commands:")
    print("  - 'add' - Go to Add Data menu")
    print("  - 'add [+/-][amount] [month/year]' - Add data directly (e.g., add +3000 3/25 or add +3000 3.25)")
    print("  - 'bank [amount]' - Update bank balance (e.g., bank 12000)")
    print("  - 'view' - Return to View Budget Data menu")
    print("  - 'exit' - Save and exit")
    
    print(f"\n{PURPLE}>>>{RESET} ", end="")

def print_error(message: str) -> None:
    '''Print an error message in red.'''
    print(f"{RED}{message}{RESET}")

def print_success(message: str) -> None:
    '''Print a success message in green.'''
    print(f"{GREEN}{message}{RESET}")

def display_budget_summary(data: Dict) -> bool:
    '''Display budget summary information without monthly records.'''
    clear_screen()
    
    records = data.get("monthly_records", [])
    bank_balance = data.get("bank_balance", 0)
    
    print(f"\n{PURPLE}===== Budget Summary ====={RESET}\n")
    
    # Check if data exists
    if not records:
        print_error("No budget data available. Please add some data first.")
        return False
    
    # Check for salary and expense data
    if not calculations.has_salary_data(data):
        print_error("No salary data available. Please add income data first.")
        return False
    
    if not calculations.has_expense_data(data):
        print_error("No expense data available. Please add expense data first.")
        return False
    
    # Sort records for consistent display order
    sorted_records = calculations.sort_records_by_date(records)
    
    # Calculate total income and expenses
    total_income = sum(int(record.get("salary", "0")) for record in sorted_records)
    total_expenses = sum(int(record.get("expenses", "0")) for record in sorted_records)
    
    # Calculate total difference
    total_difference = total_income - total_expenses
    
    # Get predictions for next month based on average monthly income and expenses
    next_month = date_utils.get_current_next_month()
    expected_income, expected_expenses, expected_difference = calculations.predict_next_month(data)
    
    # Calculate expected total leftover (expected difference + current bank balance)
    expected_total_leftover = expected_difference + bank_balance
    
    # Display summary
    print(f"{ORANGE}Bank Balance: ${bank_balance:,.2f}{RESET}")
    print(f"{GREEN}Total Income: ${total_income:,.2f}{RESET}")
    print(f"{RED}Total Expenses: ${total_expenses:,.2f}{RESET}")
    print(f"{BLUE}Total Difference: ${total_difference:,.2f}{RESET}")
    
    print(f"\n{PURPLE}===== Next Month Prediction ====={RESET}")
    print(f"{BLUE}Month: {next_month}{RESET}")
    print(f"{GREEN}Expected Income: ${expected_income:,.2f}{RESET}")
    print(f"{RED}Expected Expenses: ${expected_expenses:,.2f}{RESET}")
    print(f"{BLUE}Expected Difference: ${expected_difference:,.2f}{RESET}")
    print(f"{ORANGE}Expected Total Leftover: ${expected_total_leftover:,.2f}{RESET}")
    
    return True

def display_monthly_records(data: Dict) -> bool:
    '''Display monthly records.'''
    clear_screen()
    
    records = data.get("monthly_records", [])
    
    print(f"\n{PURPLE}===== Monthly Records ====={RESET}\n")
    
    # Check if data exists
    if not records:
        print_error("No budget data available. Please add some data first.")
        return False
    
    # Sort records for consistent display order
    sorted_records = calculations.sort_records_by_date(records)
    
    # Print header with column names
    print(f"{BLUE}{"Month":<10}{RESET} {GREEN}{"Income":<15}{RESET} {RED}{"Expenses":<15}{RESET} {ORANGE}{"Remaining":<15}{RESET}")
    print("-" * 55)
    
    for record in sorted_records:
        month = record.get("month", "N/A")
        income = int(record.get("salary", "0"))
        expenses = int(record.get("expenses", "0"))
        monthly_remaining = calculations.calculate_monthly_remaining(record)
        
        print(f"{BLUE}{month:<10}{RESET} {GREEN}${income:<14,.2f}{RESET} {RED}${expenses:<14,.2f}{RESET} {ORANGE}${monthly_remaining:<14,.2f}{RESET}")
    
    return True

def handle_view_data(data: Dict) -> Dict:
    '''Handle the view data menu option.'''
    # Display summary initially
    has_data = display_budget_summary(data)
    
    # If no data, redirect to add data menu
    if not has_data:
        # Determine which error message to show
        redirect_message: str
        if not data.get("monthly_records", []):
            redirect_message = "No budget data available. Please add some data first."
        elif not calculations.has_salary_data(data):
            redirect_message = "No salary data available. Please add income data first."
        elif not calculations.has_expense_data(data):
            redirect_message = "No expense data available. Please add expense data first."
        else:
            redirect_message = "Missing budget data. Please add required data first."
            
        # Clear screen, show error, and go directly to add data menu
        clear_screen()
        print_error(redirect_message)
        print()  # Empty line
        return handle_add_data(data, skip_clear=True)  # Skip the clear screen in handle_add_data
    
    error_message: Optional[str] = None
    success_message: Optional[str] = None
    current_view = "summary"  # Track current view (summary, records)
    
    while True:
        if error_message:
            clear_screen()
            print_error(error_message)
            print()  # Empty line
            error_message = None
            
            # Redisplay the current view
            if current_view == "summary":
                display_budget_summary(data)
            elif current_view == "records":
                display_monthly_records(data)
            
        if success_message:
            clear_screen()
            print_success(success_message)
            print()  # Empty line
            success_message = None
            
            # Redisplay the current view
            if current_view == "summary":
                display_budget_summary(data)
            elif current_view == "records":
                display_monthly_records(data)
            
        display_view_menu(current_view)
        user_input = input().strip()
        
        # Parse the command using the new parser module
        cmd = parser.parse_command(user_input)
        
        # Handle menu option commands (numeric inputs)
        if cmd["command"] == "menu_option":
            option = cmd["menu_option"]
            if option == 1:
                if current_view == "summary":
                    current_view = "records"
                    display_monthly_records(data)
                else:  # records view
                    current_view = "summary"
                    display_budget_summary(data)
            elif option == 2:
                clear_screen()
                handle_view_graphs(data)
                # Redisplay the current view after returning from graphs
                if current_view == "summary":
                    display_budget_summary(data)
                elif current_view == "records":
                    display_monthly_records(data)
            elif option == 3:
                clear_screen()
                return data
            elif option == 4:
                budget.save_data(data)
                print("\nData saved successfully!")
                print("\nThank you for using the Budget Management App. Goodbye!")
                exit(0)
            else:
                error_message = "Invalid choice. Please try again."
                continue
        # Handle text-based commands    
        elif cmd["error"] is not None:
            error_message = parser.get_error_message(cmd["error"])
            continue
        elif cmd["command"] == "menu":
            clear_screen()
            return data
        elif cmd["command"] == "exit":
            budget.save_data(data)
            print("\nData saved successfully!")
            print("\nThank you for using the Budget Management App. Goodbye!")
            exit(0)
        elif cmd["command"] == "view":
            # Already in view menu, just refresh the current view
            if current_view == "summary":
                display_budget_summary(data)
            elif current_view == "records":
                display_monthly_records(data)
            continue
        elif cmd["command"] == "graph":
            # Check if data exists before showing graphs
            if not data.get("monthly_records", []):
                error_message = "No budget data available. Please add some data first."
                continue
            elif not calculations.has_salary_data(data):
                error_message = "No salary data available. Please add income data first."
                continue
            elif not calculations.has_expense_data(data):
                error_message = "No expense data available. Please add expense data first."
                continue
            
            # If we have data, show the graphs
            clear_screen()
            handle_view_graphs(data)
            # Redisplay the current view after returning from graphs
            if current_view == "summary":
                display_budget_summary(data)
            elif current_view == "records":
                display_monthly_records(data)
        elif cmd["command"] == "bank":
            # For bank command, amount should not be None
            amount = cmd["amount"]
            try:
                if amount is None:
                    raise ValueError("Amount is required for bank balance update")
                data = budget.update_bank_balance(data, amount)
                # Auto-save after update
                budget.save_data(data)
                # Set success message for next iteration
                success_message = f"Bank balance updated to ${amount:,.2f}"
            except ValueError as e:
                error_message = f"Error updating bank balance: {str(e)}"
            continue
        elif cmd["command"] == "income":
            # For income command, both month and amount should not be None
            month = cmd["month"]
            amount = cmd["amount"]
            try:
                if month is None:
                    raise ValueError("Month is required for income records")
                if amount is None:
                    raise ValueError("Amount is required for income records")
                
                # Check if month already has income data
                existing_record = calculations.get_existing_data_for_month(data, month)
                if existing_record and "salary" in existing_record and int(existing_record.get("salary", "0")) > 0:
                    # Handle duplicate entry
                    data, success_message = handle_duplicate_month_entry(data, month, amount, True)
                else:
                    # No duplicate, proceed normally
                    data = budget.add_monthly_record(data, month, amount, True)
                    success_message = f"Income of ${amount:,.2f} added for {month}"
                
                # Auto-save after update
                budget.save_data(data)
            except ValueError as e:
                error_message = f"Error adding income: {str(e)}"
            continue
        elif cmd["command"] == "expense":
            # For expense command, both month and amount should not be None
            month = cmd["month"]
            amount = cmd["amount"]
            try:
                if month is None:
                    raise ValueError("Month is required for expense records")
                if amount is None:
                    raise ValueError("Amount is required for expense records")
                
                # Check if month already has expense data
                existing_record = calculations.get_existing_data_for_month(data, month)
                if existing_record and "expenses" in existing_record and int(existing_record.get("expenses", "0")) > 0:
                    # Handle duplicate entry
                    data, success_message = handle_duplicate_month_entry(data, month, amount, False)
                else:
                    # No duplicate, proceed normally
                    data = budget.add_monthly_record(data, month, amount, False)
                    success_message = f"Expense of ${amount:,.2f} added for {month}"
                
                # Auto-save after update
                budget.save_data(data)
            except ValueError as e:
                error_message = f"Error adding expense: {str(e)}"
            continue
        elif cmd["command"] == "add":
            # Just "add" command redirects to add data menu
            clear_screen()
            data = handle_add_data(data)
            # After returning, redisplay the current view
            if current_view == "summary":
                display_budget_summary(data)
            elif current_view == "records":
                display_monthly_records(data)
            continue
        else:
            error_message = "Invalid choice or command. Please try again."
            continue
    
    return data

def handle_view_graphs(data: Dict) -> None:
    '''Show all available graphs without displaying a menu.'''
    clear_screen()
    print(f"\n{PURPLE}===== Viewing Budget Graphs ====={RESET}\n")
    
    # Check if data exists first
    if not data.get("monthly_records", []):
        print_error("No budget data available. Please add some data first.")
        input("\nPress Enter to continue...")
        return
    
    if not calculations.has_salary_data(data):
        print_error("No salary data available. Please add income data first.")
        input("\nPress Enter to continue...")
        return
    
    if not calculations.has_expense_data(data):
        print_error("No expense data available. Please add expense data first.")
        input("\nPress Enter to continue...")
        return
    
    print("Showing all available graphs. Close graph windows or press Enter to continue.\n")
    # Show both graphs using the function that shows all visualizations
    visualization.show_visualizations(data)
    clear_screen()
    return

def handle_add_data(data: Dict, skip_clear: bool = False) -> Dict:
    '''Handle the add data menu option.'''
    if not skip_clear:
        clear_screen()
    
    error_message = None
    success_message = None
    
    while True:
        if error_message:
            clear_screen()
            print_error(error_message)
            print()  # Empty line
            error_message = None
        
        if success_message:
            clear_screen()
            print_success(success_message)
            print()  # Empty line
            success_message = None
            
        print(f"\n{PURPLE}===== Add or Update Data ====={RESET}\n")
        print("Enter data in one of the following formats:")
        print("  - Income: +[amount] [month/year] (e.g., +3000 3/25 or +3000 3.25)")
        print("  - Expense: -[amount] [month/year] (e.g., -2500 2/25 or -2500 2.25)")
        print("  - Bank Balance: bank [amount] (e.g., bank 12000)")
        print("\nOr enter:")
        print("  - Empty input / 'menu' / 'return' - Return to main menu")
        print("  - 'view' - Go to View Budget Data menu")
        print("  - 'graph' - View graphs")
        print("  - 'exit' - Save and exit")
        
        print(f"\n{PURPLE}>>>{RESET} ", end="")
        user_input = input().strip()
        
        # Parse the command using the new parser module
        cmd = parser.parse_command(user_input)
        
        if cmd["error"] is not None:
            error_message = parser.get_error_message(cmd["error"])
            continue
        elif cmd["command"] == "menu":
            clear_screen()
            return data
        elif cmd["command"] == "exit":
            budget.save_data(data)
            print("\nData saved successfully!")
            print("\nThank you for using the Budget Management App. Goodbye!")
            exit(0)
        elif cmd["command"] == "graph":
            # Check if data exists before showing graphs (no_data error)
            if not data.get("monthly_records", []):
                error_message = "No budget data available. Please add some data first."
                continue
            elif not calculations.has_salary_data(data):
                error_message = "No salary data available. Please add income data first."
                continue
            elif not calculations.has_expense_data(data):
                error_message = "No expense data available. Please add expense data first."
                continue
            
            # If we have data, show the graphs
            clear_screen()
            handle_view_graphs(data)
        elif cmd["command"] == "bank":
            # For bank command, amount should not be None
            amount = cmd["amount"]
            try:
                if amount is None:
                    raise ValueError("Amount is required for bank balance update")
                data = budget.update_bank_balance(data, amount)
                # Auto-save after update
                budget.save_data(data)
                # Set success message for next iteration
                success_message = f"Bank balance updated to ${amount:,.2f}"
            except ValueError as e:
                error_message = f"Error updating bank balance: {str(e)}"
            continue
        elif cmd["command"] == "income":
            # For income command, both month and amount should not be None
            month = cmd["month"]
            amount = cmd["amount"]
            try:
                if month is None:
                    raise ValueError("Month is required for income records")
                if amount is None:
                    raise ValueError("Amount is required for income records")
                
                # Check if month already has income data
                existing_record = calculations.get_existing_data_for_month(data, month)
                if existing_record and "salary" in existing_record and int(existing_record.get("salary", "0")) > 0:
                    # Handle duplicate entry
                    data, success_message = handle_duplicate_month_entry(data, month, amount, True)
                else:
                    # No duplicate, proceed normally
                    data = budget.add_monthly_record(data, month, amount, True)
                    success_message = f"Income of ${amount:,.2f} added for {month}"
                
                # Auto-save after update
                budget.save_data(data)
            except ValueError as e:
                error_message = f"Error adding income: {str(e)}"
            continue
        elif cmd["command"] == "expense":
            # For expense command, both month and amount should not be None
            month = cmd["month"]
            amount = cmd["amount"]
            try:
                if month is None:
                    raise ValueError("Month is required for expense records")
                if amount is None:
                    raise ValueError("Amount is required for expense records")
                
                # Check if month already has expense data
                existing_record = calculations.get_existing_data_for_month(data, month)
                if existing_record and "expenses" in existing_record and int(existing_record.get("expenses", "0")) > 0:
                    # Handle duplicate entry
                    data, success_message = handle_duplicate_month_entry(data, month, amount, False)
                else:
                    # No duplicate, proceed normally
                    data = budget.add_monthly_record(data, month, amount, False)
                    success_message = f"Expense of ${amount:,.2f} added for {month}"
                
                # Auto-save after update
                budget.save_data(data)
            except ValueError as e:
                error_message = f"Error adding expense: {str(e)}"
            continue
        elif cmd["command"] == "view":
            # Redirect to view data menu
            clear_screen()
            data = handle_view_data(data)
            # After returning, stay in add data menu
            clear_screen()
            continue
    
    return data

def handle_duplicate_month_entry(data: Dict, month: str, amount: int, is_income: bool) -> Tuple[Dict, str]:
    '''Handle situation where user tries to add data to a month that already has data.'''
    existing_record = calculations.get_existing_data_for_month(data, month)
    
    # Determine what kind of data exists and what we"re trying to add
    entry_type = "income" if is_income else "expense"
    field_name = "salary" if is_income else "expenses"
    existing_value = int(existing_record.get(field_name, "0"))
    
    # Show existing data
    clear_screen()
    print(f"\n{PURPLE}===== Duplicate Entry Detected ====={RESET}\n")
    print(f"The month {month} already has {entry_type} data:")
    
    if "salary" in existing_record:
        print(f"Existing Income: ${int(existing_record.get("salary", "0")):,.2f}")
    
    if "expenses" in existing_record:
        print(f"Existing Expenses: ${int(existing_record.get("expenses", "0")):,.2f}")
    
    print(f"\nNew {entry_type.capitalize()}: ${amount:,.2f}")
    
    # Show options
    print("\nChoose an option:")
    print("1. Add - Combine new amount with existing amount")
    print(f"   Result: ${(existing_value + amount):,.2f}")
    print("2. Overwrite - Replace existing amount with new amount")
    print(f"   Result: ${amount:,.2f}")
    print("3. Cancel - Keep existing data unchanged")
    
    # Get user choice
    print(f"\n{PURPLE}>>>{RESET} ", end="")
    choice = input().strip()
    
    # Handle choice
    if choice == "1":  # Add
        combined_amount = existing_value + amount
        data = budget.add_monthly_record(data, month, combined_amount, is_income)
        return data, f"{entry_type.capitalize()} updated to ${combined_amount:,.2f} for {month} (combined)"
    elif choice == "2":  # Overwrite
        data = budget.add_monthly_record(data, month, amount, is_income)
        return data, f"{entry_type.capitalize()} updated to ${amount:,.2f} for {month} (overwritten)"
    else:  # Cancel or invalid input
        return data, f"Operation cancelled. Existing data for {month} remains unchanged."

def main() -> None:
    '''Main program entry point.'''
    clear_screen()
    display_welcome()
    
    # Load data
    data = budget.load_data()
    error_message = None
    success_message = None
    
    while True:
        if error_message:
            clear_screen()
            print_error(error_message)
            print()  # Empty line
            error_message = None
            
        if success_message:
            clear_screen()
            print_success(success_message)
            print()  # Empty line
            success_message = None
        
        display_main_menu()
        user_input = input().strip()
        
        # Parse the command using the new parser module
        cmd = parser.parse_command(user_input)
        
        # Handle menu option commands (numeric inputs)
        if cmd["command"] == "menu_option":
            option = cmd["menu_option"]
            if option == 1:
                data = handle_view_data(data)
                continue
            elif option == 2:
                data = handle_add_data(data, skip_clear=False)
                continue
            elif option == 3:
                budget.save_data(data)
                print("\nData saved successfully!")
                print("\nThank you for using the Budget Management App. Goodbye!")
                break
            else:
                error_message = "Invalid choice. Please try again."
                continue
        # Handle command
        elif cmd["command"] == "add":
            data = handle_add_data(data, skip_clear=False)
            continue
        elif cmd["error"] is not None:
            error_message = parser.get_error_message(cmd["error"])
            continue  
        elif cmd["command"] == "bank":
            # For bank command, amount should not be None
            amount = cmd["amount"]
            try:
                if amount is None:
                    raise ValueError("Amount is required for bank balance update")
                data = budget.update_bank_balance(data, amount)
                # Auto-save after update
                budget.save_data(data)
                # Set success message for next iteration
                success_message = f"Bank balance updated to ${amount:,.2f}"
            except ValueError as e:
                error_message = f"Error updating bank balance: {str(e)}"
            continue
        elif cmd["command"] == "income":
            # For income command, both month and amount should not be None
            month = cmd["month"]
            amount = cmd["amount"]
            try:
                if month is None:
                    raise ValueError("Month is required for income records")
                if amount is None:
                    raise ValueError("Amount is required for income records")
                
                # Check if month already has income data
                existing_record = calculations.get_existing_data_for_month(data, month)
                if existing_record and "salary" in existing_record and int(existing_record.get("salary", "0")) > 0:
                    # Handle duplicate entry
                    data, success_message = handle_duplicate_month_entry(data, month, amount, True)
                else:
                    # No duplicate, proceed normally
                    data = budget.add_monthly_record(data, month, amount, True)
                    success_message = f"Income of ${amount:,.2f} added for {month}"
                
                # Auto-save after update
                budget.save_data(data)
            except ValueError as e:
                error_message = f"Error adding income: {str(e)}"
            continue
        elif cmd["command"] == "expense":
            # For expense command, both month and amount should not be None
            month = cmd["month"]
            amount = cmd["amount"]
            try:
                if month is None:
                    raise ValueError("Month is required for expense records")
                if amount is None:
                    raise ValueError("Amount is required for expense records")
                
                # Check if month already has expense data
                existing_record = calculations.get_existing_data_for_month(data, month)
                if existing_record and "expenses" in existing_record and int(existing_record.get("expenses", "0")) > 0:
                    # Handle duplicate entry
                    data, success_message = handle_duplicate_month_entry(data, month, amount, False)
                else:
                    # No duplicate, proceed normally
                    data = budget.add_monthly_record(data, month, amount, False)
                    success_message = f"Expense of ${amount:,.2f} added for {month}"
                
                # Auto-save after update
                budget.save_data(data)
            except ValueError as e:
                error_message = f"Error adding expense: {str(e)}"
            continue
        elif cmd["command"] == "exit":
            budget.save_data(data)
            print("\nData saved successfully!")
            print("\nThank you for using the Budget Management App. Goodbye!")
            break
        elif cmd["command"] == "graph":
            # Check if data exists before showing graphs (no_data error)
            redirect_message = None
            if not data.get("monthly_records", []):
                redirect_message = "No budget data available. Please add some data first."
            elif not calculations.has_salary_data(data):
                redirect_message = "No salary data available. Please add income data first."
            elif not calculations.has_expense_data(data):
                redirect_message = "No expense data available. Please add expense data first."
            
            # If data is missing, show error message and redirect to add data menu
            if redirect_message:
                clear_screen()
                print_error(redirect_message)
                print()  # Empty line
                data = handle_add_data(data, skip_clear=True)  # Skip clear screen in handle_add_data
                continue
            
            # If we have data, show the graphs
            clear_screen()
            handle_view_graphs(data)
        elif cmd["command"] == "view":
            # Redirect to view data menu
            clear_screen()
            data = handle_view_data(data)
            # After returning, stay in add data menu
            clear_screen()
            continue
        else:
            error_message = "Invalid choice or command format. Please try again."
            continue

if __name__ == "__main__":
    main() 