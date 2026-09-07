import urllib.request
import json
from icalendar import Calendar, Event
from datetime import datetime
import pytz

def build_eala_calendar():
    cal = Calendar()
    cal.add('prodid', '-//Alex Eala Match Feed//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Alex Eala Matches')
    cal.add('x-wr-timezone', 'Asia/Manila')

    local_tz = pytz.timezone('Asia/Manila')

    # Fetch both past matches and upcoming matches
    endpoints = [
        "https://api.sofascore.com/api/v1/player/262580/events/last/0", # Recent past matches
        "https://api.sofascore.com/api/v1/player/262580/events/next/0"  # Upcoming matches
    ]

    all_events = []

    for url in endpoints:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                all_events.extend(data.get('events', []))
        except Exception as e:
            print(f"Failed to fetch endpoint {url}: {e}")

    for match in all_events:
        event = Event()
        
        tournament = match.get('tournament', {}).get('name', 'WTA Event')
        round_info = match.get('roundInfo', {}).get('name', 'Match')
        
        home_player = match.get('homeTeam', {}).get('name', '')
        away_player = match.get('awayTeam', {}).get('name', '')
        
        is_eala_home = 'Eala' in home_player
        opponent = away_player if is_eala_home else home_player
        
        # Extract score for completed matches
        status = match.get('status', {}).get('type', '')
        score_str = ""
        if status == 'finished':
            home_score = match.get('homeScore', {}).get('display', '')
            away_score = match.get('awayScore', {}).get('display', '')
            score_str = f" [Final: {home_score}-{away_score}]" if home_score != '' else ""

        title = f"[{round_info}] Alex Eala vs {opponent if opponent else 'TBA'}{score_str}"

        timestamp = match.get('startTimestamp')
        if timestamp:
            utc_dt = datetime.fromtimestamp(timestamp, pytz.utc)
            manila_dt = utc_dt.astimezone(local_tz)
        else:
            continue

        description = (
            f"Tournament: {tournament}\n"
            f"Round: {round_info}\n"
            f"Status: {status.capitalize()}\n"
            f"Timezone: Manila (UTC+8)\n"
            f"Automated via Sofascore API."
        )

        event.add('summary', title)
        event.add('dtstart', manila_dt)
        event.add('description', description)
        event.add('location', tournament)

        cal.add_component(event)

    with open('alex_eala.ics', 'wb') as f:
        f.write(cal.to_ical())
    
    print("alex_eala.ics updated with past and future matches.")

if __name__ == "__main__":
    build_eala_calendar()
