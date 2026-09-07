import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz

# 1. Initialize Calendar
cal = Calendar()
cal.add('prodid', '-//Alex Eala WTA Schedule Feed//EN')
cal.add('version', '2.0')
cal.add('x-wr-calname', 'Alex Eala - Match Schedule')
cal.add('x-wr-timezone', 'Asia/Manila')

local_tz = pytz.timezone('Asia/Manila')

# 2. Match Schedule Data
matches = [
    {
        "tournament": "Singapore Tennis Open (WTA 500)",
        "round": "Round of 32",
        "opponent": "TBD",
        "surface": "Indoor Hard Court",
        "start_time_str": "2026-09-21 14:00",
        "broadcast": "TapGo / SPOTV"
    }
]

for match in matches:
    event = Event()
    
    title = f"[{match['round']}] Alex Eala vs {match['opponent']}"
    
    naive_dt = datetime.strptime(match['start_time_str'], "%Y-%m-%d %H:%M")
    localized_dt = local_tz.localize(naive_dt)
    
    description = (
        f"Tournament: {match['tournament']}\n"
        f"Surface: {match['surface']}\n"
        f"Broadcast: {match['broadcast']}\n"
        f"Updated via custom auto-scraper."
    )
    
    event.add('summary', title)
    event.add('dtstart', localized_dt)
    event.add('description', description)
    event.add('location', match['tournament'])
    
    cal.add_component(event)

# 3. Export to ICS File
with open('alex_eala.ics', 'wb') as f:
    f.write(cal.to_ical())

print("alex_eala.ics updated successfully.")
