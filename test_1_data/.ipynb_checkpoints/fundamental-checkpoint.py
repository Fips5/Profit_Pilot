import yfinance as yf
import pandas as pd
import numpy as np
import re
from datetime import datetime
import os
import json


# key
def get_api_key(key_name: str, file_path: str = "api_keys.json") -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"API key file '{file_path}' not found.")

    with open(file_path, "r") as f:
        api_keys = json.load(f)
    if key_name not in api_keys:
        raise KeyError(f"API key for '{key_name}' not found in '{file_path}'.")

    return api_keys[key_name]

# Initialize Groq client dynamically (replace with your actual API key securely)
from groq import Groq
groq_client = Groq(api_key=get_api_key("groq"))

def get_financial_calendar(ticker):
    """
    Fetches the financial calendar for the given ticker.
    """
    stock = yf.Ticker(ticker)
    try:
        earnings_dates = stock.earnings_dates
        if earnings_dates is not None and not earnings_dates.empty:
            return earnings_dates.index
        else:
            return None
    except Exception as e:
        print(f"Error fetching financial calendar for {ticker}: {e}")
        return None

def get_financial_data(ticker):
    """
    Fetches quarterly financial data for the given ticker.
    """
    stock = yf.Ticker(ticker)
    try:
        quarterly_income_statement = stock.quarterly_financials.dropna(axis=1, how="all")
        quarterly_cash_flow_statement = stock.quarterly_cashflow.dropna(axis=1, how="all")
        return {
            "quarterly_income_statement": quarterly_income_statement,
            "quarterly_cash_flow_statement": quarterly_cash_flow_statement,
        }
    except Exception as e:
        print(f"Error fetching financial data for {ticker}: {e}")
        return None

def calculate_quarterly_changes(data):
    """
    Calculates percentage changes between quarters for the given data.
    """
    try:
        data = data.fillna(method='ffill').fillna(method='bfill')  # Fill missing values
        quarterly_changes = data.pct_change(axis='columns').dropna(axis=1, how='all')
        return quarterly_changes.apply(lambda col: col.map(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A"))
    except Exception as e:
        print(f"Error calculating quarterly changes: {e}")
        return pd.DataFrame()

def format_financial_statement_for_llm(statement_column):
    """
    Formats a financial statement column for analysis.
    """
    return "\n".join(f"{index}: {value:,.2f}" if isinstance(value, (int, float)) else f"{index}: {value}" for index, value in statement_column.items())

from datetime import datetime

def create_prompt_for_financial_analysis(current, previous, cash_flow_changes):
    """
    Creates an evaluation prompt for the LLM, with explicit instructions on providing the score.
    """
    current_year = datetime.now().year
    return f"""
Evaluate the following financial statements for the current year and the previous year.
Provide detailed insights on the following aspects:

a. **Revenue Growth**: Assess the growth in revenue from the previous year to the current year.
b. **Profitability**: Evaluate the company's profitability, considering net income and any changes in margins.
c. **Operating Efficiency**: Analyze the operating expenses and how efficiently the company is managing costs.
d. **Earnings Quality**: Consider the stability of earnings, the presence of any unusual items, and tax effects.
e. **Cash Flow Changes**: Review any significant changes in cash flow, both positive and negative, and their impact on the company's financial position.

At the end of your evaluation, provide an overall scoreon a scale of 0 to 10, with 10 being the best possible score and 0 being the worst. Please ensure that the score reflects your evaluation of the company's financial health based on the aspects above.

If any of the provided data (revenue, profitability, operating efficiency, earnings quality, or cash flow) is missing, consider that in your evaluation and adjust the score accordingly. If all statements are missing, the score should be 0.

explress the overall score in THIS SPECIFIC FASHON: "Overall Score: N/10"
Please present the overall score at the end of your analysis.

Current Year Income Statement ({current_year}):
{current}

Previous Year Income Statement:
{previous}

Quarterly Cash Flow Changes:
{cash_flow_changes}
"""


def evaluate_financial_statements_llm(current, previous, cash_flow_changes):
    """
    Uses LLM to evaluate financial statements and return a score.
    """
    prompt = create_prompt_for_financial_analysis(current, previous, cash_flow_changes)
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gemma2-9b-it",
            temperature=0.2,
            max_tokens=1000
        )
        #print(response)
        analysis = response.choices[0].message.content.strip()
        score = re.search(r"(\d+\.?\d*)", analysis)
        return float(score.group(1)) if score else None
    except Exception as e:
        print(f"Error during LLM evaluation: {e}")
        return None

def extract_score_from_analysis(analysis):
    """
    Extracts the overall score from the analysis prompt in the format "**Overall Score: 2/10**".
    """
    # Pattern for extracting scores in the format "Overall Score: 2/10"
    pattern = r"(?i)\*\*?Overall Score[:\s]*?(\d+)/(\d+)\*\*?"
    
    match = re.search(pattern, analysis)
    if match:
        # Extract the numerator and denominator
        score, max_score = int(match.group(1)), int(match.group(2))
        
        # Validate score range
        if 0 <= score <= max_score:
            return f"{score}/{max_score}"

    return None  # Return None if no valid score is found


def validate_score(score):
    """
    Validates if the extracted score is a valid numerical value and within acceptable bounds.
    """
    try:
        score = float(score)
        if 0 <= score <= 10:  # Assuming a valid score is between 0 and 10
            return score
    except ValueError:
        pass
    return None



def evaluate_financial_statements_llm(current, previous, cash_flow_changes):
    """
    Uses LLM to evaluate financial statements and return a score.
    """
    prompt = create_prompt_for_financial_analysis(current, previous, cash_flow_changes)
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gemma2-9b-it",
            temperature=0.2,
            max_tokens=1000
        )
        analysis = response.choices[0].message.content.strip()
        print("LLM Response:", analysis)  # For debugging
        score = extract_score_from_analysis(analysis)
        return score
    except Exception as e:
        print(f"Error during LLM evaluation: {e}")
        return None


def fundamental(symbol):
    """
    Evaluates the fundamental performance of a stock based on quarterly data.
    """
    try:
        print(f"Fetching financial data for {symbol}...")
        data = get_financial_data(symbol)
        if not data:
            return pd.DataFrame()

        income_statement = data['quarterly_income_statement']
        cash_flow_changes = calculate_quarterly_changes(data['quarterly_cash_flow_statement'])
        scores = []

        for i in range(income_statement.shape[1] - 1):
            current = format_financial_statement_for_llm(income_statement.iloc[:, i])
            previous = format_financial_statement_for_llm(income_statement.iloc[:, i + 1])

            score = evaluate_financial_statements_llm(current, previous, cash_flow_changes.to_string())
            scores.append((income_statement.columns[i], score))

        result = pd.DataFrame(scores, columns=["Quarter", "Score"])
        return result

    except Exception as e:
        print(f"Error evaluating fundamentals for {symbol}: {e}")
        return pd.DataFrame({'Quarter': [], 'Score': []})