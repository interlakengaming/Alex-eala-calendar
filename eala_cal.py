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

    # Official Sofascore ID for Alex Eala: 327924
    endpoints = [
        "https://api.sofascore.com/api/v1/player/327924/events/last/0", # Recent past matches
        "https://api.sofascore.com/api/v1/player/327924/events/next/0"  # Upcoming matches
    ]

    all_events = []
    for url in endpoints:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                all_events.extend(data.get('events', []))
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    for match in all_events:
        event = Event()
        
        tournament = match.get('tournament', {}).get('name', 'WTA Event')
        round_info = match.get('roundInfo', {}).get('name', 'Match')
        
        home_player = match.get('homeTeam', {}).get('name', '')
        away_player = match.get('awayTeam', {}).get('name', '')
        
        is_eala_home = 'Eala' in home_player
        opponent = away_player if is_eala_home else home_player
        
        # Parse set-by-set breakdown
        status = match.get('status', {}).get('type', '')
        score_str = ""
        set_details = ""
        
        if status == 'finished':
            home_score = match.get('homeScore', {})
            away_score = match.get('awayScore', {})
            
            # Extract individual set scores (period1, period2, period3)
            sets = []
            for i in range(1, 6):
                p_key = f'period{i}'
                if p_key in home_score and p_key in away_score:
                    sets.append(f"{home_score[p_key]}-{away_score[p_key]}")
            
            set_breakdown = ", ".join(sets)
            h_disp = home_score.get('display', '')
            a_disp = away_score.get('display', '')
            
            if set_breakdown:
                score_str = f" [Final: {h_disp}-{a_disp} ({set_breakdown})]"
                set_details = f"Set Breakdown: {set_breakdown}\n"

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
            f"{set_details}"
            f"Timezone: Manila (UTC+8)"
        )

        event.add('summary', title)
        event.add('dtstart', manila_dt)
        event.add('description', description)
        event.add('location', tournament)

        cal.add_component(event)

    with open('alex_eala.ics', 'wb') as f:
        f.write(cal.to_ical())
    
    print("alex_eala.ics updated successfully with set scores.")

if __name__ == "__main__":
    build_eala_calendar()
