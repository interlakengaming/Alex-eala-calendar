import json
import urllib.request
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz

# Cloudscraper bypasses Cloudflare anti-bot checks on GitHub servers
try:
    import cloudscraper
    scraper = cloudscraper.create_scraper()
except Exception:
    scraper = None

def build_eala_calendar():
    cal = Calendar()
    cal.add('prodid', '-//Alex Eala Match Feed//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Alex Eala Matches')
    cal.add('x-wr-timezone', 'Asia/Manila')

    # Baseline match history & upcoming tournaments (Fallback if API is unreachable)
    baseline_matches = [
        {
            "tournament": "US Open 2026",
            "round": "Round of 32",
            "opponent": "Iva Jovic",
            "status": "Finished",
            "score": " [Final: 1-2 (5-7, 6-3, 5-7)]",
            "start_utc": datetime(2026, 9, 5, 23, 15, tzinfo=pytz.utc),
            "location": "Arthur Ashe Stadium, Flushing Meadows, NY"
        },
        {
            "tournament": "US Open 2026",
            "round": "Round of 64",
            "opponent": "Oleksandra Oliynykova",
            "status": "Finished",
            "score": " [Final: 2-0 (6-1, 6-4)]",
            "start_utc": datetime(2026, 9, 3, 18, 50, tzinfo=pytz.utc),
            "location": "Louis Armstrong Stadium, Flushing Meadows, NY"
        },
        {
            "tournament": "US Open 2026",
            "round": "Round of 128",
            "opponent": "Mary Stoiana",
            "status": "Finished",
            "score": " [Final: 2-0 (6-1, 6-2)]",
            "start_utc": datetime(2026, 9, 2, 1, 50, tzinfo=pytz.utc),
            "location": "Louis Armstrong Stadium, Flushing Meadows, NY"
        },
        {
            "tournament": "Mubadala DC Open 2026",
            "round": "Finals",
            "opponent": "Jessica Pegula",
            "status": "Finished",
            "score": " [Final: 2-1 (4-6, 6-4, 6-0)]",
            "start_utc": datetime(2026, 8, 2, 19, 0, tzinfo=pytz.utc),
            "location": "Rock Creek Park Tennis Center, Washington DC"
        },
        {
            "tournament": "Wimbledon 2026",
            "round": "Round of 16",
            "opponent": "Jasmine Paolini",
            "status": "Finished",
            "score": " [Final: 1-2 (6-4, 4-6, 3-6)]",
            "start_utc": datetime(2026, 7, 6, 12, 35, tzinfo=pytz.utc),
            "location": "All England Lawn Tennis Club, London"
        },
        {
            "tournament": "Singapore Tennis Open (WTA 500)",
            "round": "Round of 32",
            "opponent": "TBA",
            "status": "Upcoming",
            "score": "",
            "start_utc": datetime(2026, 9, 21, 6, 0, tzinfo=pytz.utc),
            "location": "OCBC Arena, Singapore"
        },
        {
            "tournament": "2026 Asian Games",
            "round": "Main Draw",
            "opponent": "TBA",
            "status": "Upcoming",
            "score": "",
            "start_utc": datetime(2026, 9, 27, 2, 0, tzinfo=pytz.utc),
            "location": "Aichi-Nagoya, Japan"
        }
    ]

    # Sofascore endpoints: past pages (0, 1, 2, 3) + future page (0)
    endpoints = [
        "https://api.sofascore.com/api/v1/player/327924/events/last/0",
        "https://api.sofascore.com/api/v1/player/327924/events/last/1",
        "https://api.sofascore.com/api/v1/player/327924/events/last/2",
        "https://api.sofascore.com/api/v1/player/327924/events/last/3",
        "https://api.sofascore.com/api/v1/player/327924/events/next/0"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Accept': '*/*',
        'Referer': 'https://www.sofascore.com/'
    }

    fetched_events = []
    for url in endpoints:
        try:
            if scraper:
                res = scraper.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    fetched_events.extend(data.get('events', []))
            else:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    fetched_events.extend(data.get('events', []))
        except Exception as e:
            print(f"API endpoint fetch error: {e}")

    processed_matches = []
    seen_ids = set()

    if fetched_events:
        for match in fetched_events:
            match_id = match.get('id')
            if match_id in seen_ids:
                continue
            seen_ids.add(match_id)

            tournament = match.get('tournament', {}).get('name', 'WTA Event')
            round_info = match.get('roundInfo', {}).get('name', 'Match')
            home_player = match.get('homeTeam', {}).get('name', '')
            away_player = match.get('awayTeam', {}).get('name', '')
            opponent = away_player if 'Eala' in home_player else home_player
            
            status = match.get('status', {}).get('type', '')
            score_str = ""
            if status == 'finished':
                home_score = match.get('homeScore', {})
                away_score = match.get('awayScore', {})
                sets = [f"{home_score.get(f'period{i}')}-{away_score.get(f'period{i}')}" 
                        for i in range(1, 6) if f'period{i}' in home_score and f'period{i}' in away_score]
                set_b = ", ".join(sets)
                h_d, a_d = home_score.get('display', ''), away_score.get('display', '')
                score_str = f" [Final: {h_d}-{a_d} ({set_b})]" if set_b else f" [Final: {h_d}-{a_d}]"

            timestamp = match.get('startTimestamp')
            if timestamp:
                utc_dt = datetime.fromtimestamp(timestamp, pytz.utc)
                processed_matches.append({
                    "tournament": tournament,
                    "round": round_info,
                    "opponent": opponent if opponent else "TBA",
                    "status": status.capitalize(),
                    "score": score_str,
                    "start_utc": utc_dt,
                    "location": tournament
                })

    final_matches = processed_matches if processed_matches else baseline_matches

    for item in final_matches:
        event = Event()
        title = f"[{item['round']}] Alex Eala vs {item['opponent']}{item['score']}"
        
        event.add('summary', title)
        event.add('dtstart', item['start_utc'])
        event.add('dtend', item['start_utc'] + timedelta(hours=2))
        event.add('description', f"Tournament: {item['tournament']}\nRound: {item['round']}\nStatus: {item['status']}")
        event.add('location', item['location'])
        
        cal.add_component(event)

    with open('alex_eala.ics', 'wb') as f:
        f.write(cal.to_ical())
    
    print(f"alex_eala.ics updated successfully with {len(final_matches)} match(es).")

if __name__ == "__main__":
    build_eala_calendar()
