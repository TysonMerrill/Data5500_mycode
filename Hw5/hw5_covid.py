import requests
import json
from datetime import datetime

#List of state codes pulled from someones github
state_codes = [
    "ak", "al", "ar", "az", "ca", "co", "ct", "de", "fl", "ga", "hi", "ia",
    "id", "il", "in", "ks", "ky", "la", "ma", "md", "me", "mi", "mn", "mo",
    "ms", "mt", "nc", "nd", "ne", "nh", "nj", "nm", "nv", "ny", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "va", "vt", "wa", "wi",
    "wv", "wy"]

# Function to fetch and process COVID data for each state
def analyze_state(state_code):
    url = f"https://api.covidtracking.com/v1/states/{state_code}/daily.json"
    req = requests.get(url)

    # Parse JSON response
    data = req.json()

    # Save the raw JSON data to a file
    with open(f"/home/ubuntu/Data5500_mycode/Hw5/{state_code}.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    # Variables
    daily_increase = []
    dates_with_no_cases = []
    monthly_cases = {}
    highest_case = 0
    highest_case_date = ''

    # Loop through JSON data to find dates and cases
    for entry in data:
        date = entry['date']
        new_cases = entry['positiveIncrease']

        # Track monthly cases with proper month-year format
        month_year = datetime.strptime(str(date), '%Y%m%d').strftime('%Y-%m')  # Formatting the dates
        if month_year not in monthly_cases:
            monthly_cases[month_year] = 0
        monthly_cases[month_year] += new_cases

        # Tracking daily increases from above variable
        daily_increase.append(new_cases)

        # Find date with the highest number of new cases
        if new_cases > highest_case:
            highest_case = new_cases
            highest_case_date = date

        # Find dates with no cases
        if new_cases == 0:
            dates_with_no_cases.append(date)


    # Calculate average of new daily confirmed cases
    average_new_cases = sum(daily_increase) / len(daily_increase) if daily_increase else 0

    # Find month with highest and lowest cases
    max_month = max(monthly_cases, key=monthly_cases.get)
    min_month = min(monthly_cases, key=monthly_cases.get)

    # Find the most recent date with no new cases (if any)
    most_recent_no_cases_date = dates_with_no_cases[-1] if dates_with_no_cases else None

    #Find the monthly cases (not required)
    print("Monthly Cases (Summed for each Month-Year):")
    for month, total_cases in monthly_cases.items():
        print(f"{month}: {total_cases}")

    # Output the results
    print(f"\nCovid confirmed cases statistics for {state_code.upper()}:")
    print(f"Average number of new daily confirmed cases: {average_new_cases}")
    print(f"Date with the highest new number of covid cases: {highest_case_date}")
    print(f"Most recent date with no new covid cases: {most_recent_no_cases_date}")
    print(f"Month and Year with the highest new number of covid cases: {max_month}")
    print(f"Month and Year with the lowest new number of covid cases: {min_month}")

# Main function to process multiple states
def main():
    for state_code in state_codes:
        analyze_state(state_code)

if __name__ == "__main__":
    main()