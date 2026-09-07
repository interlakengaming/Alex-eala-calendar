import urllib.request
import json
from icalendar import Calendar, Event
from datetime import datetime
import pytz

def build_eala_calendar():
    # 1. Initialize Calendar Meta
    cal = Calendar()
    cal.add('prodid', '-//Alex Eala Match Feed//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Alex Eala Matches')
    cal.add('x-wr-timezone', 'Asia/Manila')

    local_tz = pytz.timezone('Asia/Manila')

    # 2. Fetch schedule data from a public endpoint
    # Using Sofascore's open endpoint structure for player searches
    url = "https://api.sofascore.com/api/v1/player/262580/events/next/0"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            events = data.get('events', [])
    except Exception as e:
        print(f"Failed to fetch live API data: {e}")
        events = []

    # 3. Process matches into iCal format
    for match in events:
        event = Event()
        
        tournament = match.get('tournament', {}).get('name', 'WTA Event')
        round_info = match.get('roundInfo', {}).get('name', 'Main Draw')
        
        home_player = match.get('homeTeam', {}).get('name', '')
        away_player = match.get('awayTeam', {}).get('name', '')
        
        opponent = away_player if 'Eala' in home_player else home_player
        title = f"[{round_info}] Alex Eala vs {opponent if opponent else 'TBA'}"

        # Start Time Parsing (UTC Unix Timestamp)
        timestamp = match.get('startTimestamp')
        if timestamp:
            utc_dt = datetime.fromtimestamp(timestamp, pytz.utc)
            manila_dt = utc_dt.astimezone(local_tz)
        else:
            continue

        description = (
            f"Tournament: {tournament}\n"
            f"Round: {round_info}\n"
            f"Timezone: Manila (UTC+8)\n"
            f"Automated via Sofascore API."
        )

        event.add('summary', title)
        event.add('dtstart', manila_dt)
        event.add('description', description)
        event.add('location', tournament)

        cal.add_component(event)

    # 4. Save output to file
    with open('alex_eala.ics', 'wb') as f:
        f.write(cal.to_ical())
    
    print("alex_eala.ics synced successfully.")

if __name__ == "__main__":
    build_eala_calendar()
