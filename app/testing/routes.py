from flask import render_template
from app.services.LeagueAPI import LeagueAPI
import json

from app.testing import bp


@bp.route('/testing', methods=['GET', 'POST'])
def index():
    # Define the URL and headers
    api = LeagueAPI("https://gql.poolplayers.com/graphql")

    # Query league divisions for a specific slug and session
    slug = "jacksonville"
    session = 134

    new_counts = new_object_counts(0, 0, 0, 0, 0)
    err_counts = new_object_counts(0, 0, 0, 0, 0)

    try:
        process_Divisions = True
        process_Sessions = True
        process_Venues = True
        process_Teams = True
        process_Schedules = True

        division_data = api.query_league_divisions(slug, session)

        league_id = division_data['data']['league']['id']
        current_session_id = division_data['data']['league']['currentSessionId']

        # Parse Divisions
        if process_Divisions:
            for d in division_data['data']['league']['divisions']:
                api.create_division_from_api_response(d)
                # format (8-Ball Open), id (390045), isMine (bool), name (Wildcat 8-Ball),
                # nightOfPlay (Monday), number (018), session{id,name}, type (EIGHT)
                # print(d['id'])
                # Parse Sessions
                if process_Sessions:
                    api.create_session_from_api(d['session'])

                # Parse Schedule
                if process_Schedules:
                    schedule_data = api.query_division_schedule(d['id'])

                    for s in schedule_data['data']['division']['schedule']:
                        # date, description, matches {} (see below), skip, weekOfPlay
                        # matches - for each
                        # away (id, isMine, name, number), home (id, isMine, name, number), location (id, name), status
                        # print(s['weekOfPlay'])
                        api.create_schedule_from_api(s, d)

                        if process_Venues or process_Teams:
                            for m in s['matches']:
                                if process_Venues:
                                    api.create_venue_from_api(m['location'])
                                if process_Teams:
                                    api.create_team_from_api(m['away'], d, m)
                                    api.create_team_from_api(m['home'], d, m)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        counts = new_object_counts(api.created_division_count, api.created_session_count,
                                   api.created_venue_count, api.created_team_count, api.created_schedule_count)
        err_counts = error_object_counts(api.error_division_count, api.error_session_count, api.error_venue_count,
                                         api.error_team_count, api.error_schedule_count)

        render_template('testing/index.html', title='Testing', counts=counts, err_counts=err_counts)

    return render_template('testing/index.html', title='Testing', counts=counts, err_counts=err_counts)


class new_object_counts:
    def __init__(self, division, session, venue, team, schedule):
        self.created_division_count = division
        self.created_session_count = session
        self.created_venue_count = venue
        self.created_team_count = team
        self.created_schedule_count = schedule


class error_object_counts:
    def __init__(self, division, session, venue, team, schedule):
        self.error_division_count = division
        self.error_session_count = session
        self.error_venue_count = venue
        self.error_team_count = team
        self.error_schedule_count = schedule
