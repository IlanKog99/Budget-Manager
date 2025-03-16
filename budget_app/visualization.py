import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import Dict, Optional

import date_utils
import calculations

def create_history_graph(data: Dict, save_path: Optional[str] = None) -> None:
    '''
    Make a line graph showing income and expenses history over time. 
    Includes a prediction for the next month to give you a sneak peek at what's comming.
    
    Args:
        data: Budget data dictionary with all the records
        save_path: Where to save the graph file, shows on screen if not specified
    '''
    records = data.get("monthly_records", [])
    
    if not records:
        print("No data available to generate graph.")
        return
    
    months = [record["month"] for record in records]
    incomes = [int(record.get("salary", "0")) for record in records]
    expenses = [int(record.get("expenses", "0")) for record in records]
    
    next_month = date_utils.get_next_month_from_string(months[-1]) if months else "Next"
    
    expected_income, expected_expenses, _ = calculations.predict_next_month(data)
    
    months.append(next_month)
    incomes.append(int(expected_income))
    expenses.append(int(expected_expenses))
    
    plt.figure(figsize=(10, 6))
    ax = plt.subplot(111)
    
    ax.plot(months, incomes, 'g-', label='Income', marker='o', linewidth=2)
    ax.plot(months, expenses, 'r-', label='Expenses', marker='o', linewidth=2)
    
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount')
    ax.set_title('Monthly Income and Expenses')
    
    formatter = ticker.FuncFormatter(lambda x, pos: f"${x:,.0f}")
    ax.yaxis.set_major_formatter(formatter)
    
    max_value = max(max(incomes), max(expenses)) if incomes and expenses else 0
    ax.set_ylim(0, max_value * 1.1 + 10000)
    
    ax.legend()
    
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def create_total_comparison_graph(data: Dict, save_path: Optional[str] = None) -> None:
    '''
    Create a bar graph comparing total income vs expenses.
    Shows the big picture so you can see how your finanical health looks overall.
    
    Args:
        data: Budget data dictionary 
        save_path: Where to save the graph file, shows on screen if not specified
    '''
    records = data.get("monthly_records", [])
    
    if not records:
        print("No data available to generate graph.")
        return
    
    total_income = sum(int(record.get("salary", "0")) for record in records)
    total_expenses = sum(int(record.get("expenses", "0")) for record in records)
    
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111)
    
    categories = ['Income', 'Expenses']
    values = [total_income, total_expenses]
    colors = ['green', 'red']
    
    bars = ax.bar(categories, values, color=colors, width=0.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'${height:,.0f}', ha='center', va='bottom')
    
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Amount')
    ax.set_title('Total Income vs Expenses')
    
    formatter = ticker.FuncFormatter(lambda x, pos: f"${x:,.0f}")
    ax.yaxis.set_major_formatter(formatter)
    
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def show_visualizations(data: Dict) -> None:
    '''
    Display both types of visualizations and wait for user input to continue.
    Makes it eaiser to view multiple graphs in one go.
    
    Args:
        data: Budget data dictionary with all the records
    '''
    plt.ion()
    
    print("\nGenerating visualizations...")
    create_history_graph(data)
    create_total_comparison_graph(data)
    
    print("Press Enter to continue...")
    input()
    
    plt.close('all')
    plt.ioff() 