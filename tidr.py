from datetime import date

# Global Variables
debug = False
today = date.today()


def get_scheds():
    # Returns a list of valid Schedule URLs
    #####

    # Payroll has two URL paths. This makes me cry.
    paths = ["https://www.uvm.edu/sites/default/files/Division-of-Finance/payroll/fy",
             "https://www.uvm.edu/sites/default/files/Division-of-Finance-Administration/payroll/fy"]
    year = abs(today.year) % 100
    pdf_name = "payrollschedule.pdf"

    scheds = []

    # Go thru URLs and return a list of all the valid ones
    for path in paths:
        count = 0
        while count <= 2:
            url = path+str(year+count)+pdf_name
            if check_valid(url):
                scheds.append(url)
            count += 1
    return scheds


def check_valid(schedule):
    # Check if the schedule exists
    #####
    import requests

    if requests.get(schedule).ok:
        if debug:
            print("Found: " + schedule)
        return True
    else:
        if debug:
            print("Skipping invalid schedule: " + schedule)
        return False


def make_sched_friendly(payroll_sched):
    # Make the schedule friendly
    # By default, the payroll schedule isn't well formatted because of 2-width headers, etc.
    #####
    import tabula

    # Tabula Area Values. Required to ensure proper values are read from the pdf
    y1 = 85  # top
    x1 = 50  # left
    y2 = 650 + y1  # height + top
    x2 = 490 + x1  # width + left

    # This method temporarily downloads the payroll schedule with specified options, placing it into a dataframe
    table = tabula.read_pdf(
        payroll_sched,
        pages=1,
        area=[y1, x1, y2, x2]
    )

    # Dictionary of the pretty dataframe columns names
    col_dict = {
        "Pay Day": "Pay_DOW",
        "Bi-\rWeekly\rPayroll": "Pay_Date",
        "Web Time Entries\rDue by 12 Noon": "Bi-Weekly_Payroll_ID",
        "Temp &\rKronos\rPayroll\rForms Due": "Web_Time_Entries_Due_DOW",
        "Semi-\rMonthly\rPayroll": "Web_Time_Entries_Due_Date",
        "All Payroll &\rBenefits Forms\rDue**": "Temp_&_Kronos_Payroll_Forms_Due",
        "Date Posted\rto\rPeopleSoft": "Semi-Monthly_Payroll",
        "Unnamed: 0": "All_Payroll_&_Benefits_Forms_Due",
        "Unnamed: 1": "Date_Posted_to_PeopleSoft"
    }

    # Return the table with columns renamed by the dict
    return table[0].rename(col_dict, axis="columns")


def date_to_string(date):
    # Stringify the date
    return str(date.month) + "/" + str(date.day) + "/" + str(date.year)


def time_distance(start, end):
    time_distance = (start-end).days
    if debug:
        print(str(time_distance))
    return time_distance


def get_dates(friendly_table):
    # Returns the next Time is Due Date
    #####
    import re
    import datetime

    # Bi-Weekly Payroll is in the form of BW02, etc.
    regex = re.compile("BW\d\d")
    wtidd = "Web_Time_Entries_Due_Date"
    bwpid = "Bi-Weekly_Payroll_ID"
    dates = []

    # Break out if column doesn't exist
    if wtidd not in friendly_table:
        return

    # Work thru the friendly table, finding valid dates
    for i in range(friendly_table.index.stop):
        if str(friendly_table.at[i, wtidd]).lower() == "nan":
            continue
        submit_by = datetime.datetime.strptime(
            str(friendly_table.at[i, wtidd]), "%m/%d/%y").date()

        # Ensure it's a BW## entry, and we're between 1 and 3 days away from submit_by date
        if regex.match(friendly_table.at[i, bwpid]) is not None and 0 <= time_distance(submit_by, today) <= 14:
            dates.append(submit_by)
    return dates


def check_valid_date(dates):
    # Checks if the date is valid, then returns it
    #####
    for date in dates:
        if date is None:
            continue
        if debug:
            print("\nNext Time is Due Date: " + date_to_string(date))
        return date


def write_json(today, best_date):
    # Writes the input a specified json file
    #####
    import os
    import json

    d = str(time_distance(best_date, today))
    bd = date_to_string(best_date)
    t = date_to_string(today)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    tid = {"time_is_due_date": bd, "todays_date": t, "days_until_due": d}

    with open(dir_path + "/tidr.json", "w") as outfile:
        if debug:
            print('\nOutput: \n    "{time_is_due_date": ' +
                  '"' + bd + '": "todays_date": "'+t+'", days_until_due":'+d+'"}')
        json.dump(tid, outfile)


def main():
    # Get all schedules, makes em friendly, checks for valid dates, then compares the dates
    # Get schedules
    scheds = get_scheds()

    for sched in scheds:
        # Make em friendly
        friendly = make_sched_friendly(sched)

        # get all valid dates
        dates = get_dates(friendly)

        if dates is None:
            continue

        # Compare the dates, choose the best one
        best_date = check_valid_date(dates)

        if best_date:
            # Write to the json
            if debug:
                print("\nUsing " + sched)
            write_json(today, best_date)
            return 1
    raise ValueError("No valid schedule found")


if __name__ == "__main__":
    main()
