# Time is Due Reminder - TIDR

This program creates a json file that includes the next day that BiWeekly time is due at the University of Vermont. 

File Result: ./tidr.json

Contents:

<code>{"time_is_due_date": "6/28/2021", "todays_date": "6/26/2021"}</code>

## Getting it working

To get it working, I did the following on [UVM silk](https://go.uvm.edu/silk):

<code>/usr/local/bin/python38 -m pip install --user tabula.py requests</code>

Then run it:

<code>/usr/local/bin/python38 ./tidr.py</code>

It runs midnight daily via cron:

<code>0 0 * * * /usr/local/bin/python38 ./tidr.py</code>
