import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.models import Session, Division, Venue, Team, Schedule
from app.extensions import SessionLocal
from datetime import datetime

class LeagueAPI:
    def __init__(self, base_url):
        self.created_division_count = 0
        self.created_session_count = 0
        self.created_venue_count = 0
        self.created_team_count = 0
        self.created_schedule_count = 0

        self.error_division_count = 0
        self.error_session_count = 0
        self.error_venue_count = 0
        self.error_team_count = 0
        self.error_schedule_count = 0

        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }

    def query_league_divisions(self, slug, session):
        # GraphQL query for fetching divisions
        query = '''
        query leagueDivisions($slug: String!, $session: Int) {
            league(slug: $slug) {
                id
                currentSessionId
                divisions(session: $session) {
                    id
                    name
                    number
                    format
                    type
                    nightOfPlay
                    isMine
                    session {
                        id
                        name
                    }
                }
            }
        }
        '''
        variables = {
            "slug": slug,
            "session": session
        }

        payload = {
            "query": query,
            "variables": variables
        }

        # Send POST request
        response = requests.post(self.base_url, headers=self.headers, json=payload)

        # Check for response status and raise error if needed
        response.raise_for_status()

        # Parse response as JSON
        data = response.json()

        # Check if the data contains the expected structure
        if 'data' in data and 'league' in data['data']:
            return data
        else:
            raise ValueError(f"Unexpected response structure: {data}")

    def query_division_schedule(self, division_id):
        # GraphQL query for fetching division schedule with venue information
        query = '''
        query divisionSchedule($id: Int!) {
            division(id: $id) {
                id
                schedule {
                    id
                    description
                    date
                    weekOfPlay
                    skip
                    matches {
                        id
                        isBye
                        status
                        scoresheet
                        startTime
                        isMine
                        isPaid
                        isPlayoff
                        results {
                            homeAway
                            points {
                                total
                            }
                        }
                        location {
                            id
                            name
                            address {
                                id
                                name
                            }
                        }
                        home {
                            id
                            name
                            number
                            isMine
                        }
                        away {
                            id
                            name
                            number
                            isMine
                        }
                        # Include venue information for the match
                        location {
                            id
                            name
                            address {
                                id
                                name
                            }
                        }
                    }
                }
                scheduleInEdit
            }
        }
        '''

        variables = {
            "id": division_id
        }

        payload = {
            "query": query,
            "variables": variables
        }

        # Send POST request
        response = requests.post(self.base_url, headers=self.headers, json=payload)

        # Check for response status and raise error if needed
        response.raise_for_status()

        # Parse response as JSON
        data = response.json()

        # Check if the data contains the expected structure
        if 'data' in data and 'division' in data['data']:
            # Return the data (active host locations)
            return data
        else:
            raise ValueError(f"Unexpected response structure: {data}")

    def query_division_rosters(self, division_id):
        # Updated GraphQL query to handle the roster using a fragment for both player types
        query = '''
        query divisionRosters($id: Int!) {
            division(id: $id) {
                id
                teams {
                    isBye
                    id
                    name
                    number
                }
            }
        }
        '''

        variables = {
            "id": division_id
        }

        payload = {
            "query": query,
            "variables": variables
        }

        # Send POST request
        response = requests.post(self.base_url, headers=self.headers, json=payload)

        # Check for response status and raise error if needed
        response.raise_for_status()
        print(response.status_code)
        print(response.text)

        # Parse response as JSON
        data = response.json()

        # Check if the data contains the expected structure
        if 'data' in data and 'division' in data['data']:
            # Return the data
            return data
        else:
            raise ValueError(f"Unexpected response structure: {data}")

    def get_active_host_locations(self, league_id):
        # Define the URL for fetching active host locations
        url = f"https://api.poolplayers.com/ActiveHostLocations?leagueId={league_id}"

        # Send GET request
        response = requests.get(url, headers={'Accept': 'application/json'})

        # Check for response status and raise error if needed
        response.raise_for_status()

        # Parse response as JSON
        data = response.json()

        # Return the data (active host locations)
        return data

    def create_division_from_api_response(self, division_data):
        # Create a database session
        db = SessionLocal()
        msg = ''

        try:
            # Check if the session already exists, if not create it
            session_data = division_data['session']
            session_record = db.query(Session).filter_by(id=session_data['id']).first()
            if not session_record:
                session_record = Session(
                    id=session_data['id'],
                    name=session_data['name']
                )
                db.add(session_record)
                db.commit()

            # Check if the division already exists in the database
            division_record = db.query(Division).filter_by(id=division_data['id']).first()
            if not division_record:
                # Create a new division record
                division_record = Division(
                    id=division_data['id'],
                    name=division_data['name'],
                    number=division_data['number'],
                    format=division_data['format'],
                    type=division_data['type'],
                    night_of_play=division_data.get('nightOfPlay'),  # Use .get() in case it's optional
                    is_mine=division_data['isMine'],
                    session_id=session_record.id  # Link to the session
                )
                db.add(division_record)
                db.commit()  # Commit the transaction to save the division
                self.created_division_count += 1

        except Exception as e:
            self.error_division_count += 1
            db.rollback()  # Rollback in case of error
            print(f"Error occurred: {e}")

        finally:
            db.close()  # Close the session

    def create_session_from_api(self, session_data):
        db = SessionLocal()
        msg = ''

        try:
            # Check if the session exists
            session_record = db.query(Session).filter_by(id=session_data['id']).first()
            if not session_record:
                # Create a new session
                session_record = Session(
                    id=session_data['id'],
                    name=session_data['name']
                )
                db.add(session_record)
                db.commit()
                self.created_session_count += 1
                print('Created Session: ' + session_data['name'])
        except Exception as e:
            self.error_session_count += 1
            db.rollback()
            print(f"Error creating session: {e}")
        finally:
            db.close()

    def create_venue_from_api(self, venue_data):
        """Create a Venue from the API response."""
        db = SessionLocal()
        msg = ''

        try:
            # Check if the venue exists
            venue_record = db.query(Venue).filter_by(id=venue_data['id']).first()
            if not venue_record:
                # Create a new venue
                venue_record = Venue(
                    id=venue_data['id'],
                    name=venue_data['name']
                )
                db.add(venue_record)
                db.commit()
                self.created_venue_count += 1
            return venue_record
        except Exception as e:
            self.error_venue_count += 1
            db.rollback()
            print(f"Error creating venue: {e}")
        finally:
            db.close()

    def create_team_from_api(self, team_data, division, venue):
        """Create a Team from the API response."""
        db = SessionLocal()
        try:
            # Check if the team exists
            team_record = db.query(Team).filter_by(id=team_data['id']).first()
            if not team_record:
                # Create a new team
                team_record = Team(
                    id=team_data['id'],
                    name=team_data['name'],
                    number=team_data['number'],
                    division_id=division['id'],  # Foreign key reference
                    venue_id=venue['id']  # Foreign key reference to venue if it exists
                )
                db.add(team_record)
                db.commit()
                self.created_team_count += 1
        except Exception as e:
            self.error_team_count += 1
            db.rollback()
            print(f"Error creating team: {e}")
        finally:
            db.close()

    def create_schedule_from_api(self, schedule_data, division_data):
        """Create a Schedule from the API response and update division's venue if identified."""
        db = SessionLocal()

        try:
            # Extract the division ID from the dictionary
            division_id = division_data['id']

            # Query the division record by its ID
            division_record = db.query(Division).filter_by(id=division_id).first()
            if not division_record:
                raise ValueError(f"Division with ID {division_id} not found.")

            # Check if the schedule exists
            schedule_record = db.query(Schedule).filter_by(id=schedule_data['id']).first()
            if not schedule_record:
                # Convert the date from string to datetime
                try:
                    schedule_date_str = schedule_data['date'].replace("Z", "+00:00")
                    schedule_date = datetime.strptime(schedule_date_str, '%Y-%m-%dT%H:%M:%S%z')
                    schedule_date_only = schedule_date.date()
                except ValueError as ve:
                    raise ValueError(f"Error parsing date: {ve}")

                # Track if we've identified the division's venue
                identified_division_venue = False

                # Iterate over the matches in the schedule data
                for match_data in schedule_data.get('matches', []):
                    home_team_id = match_data['home']['id']
                    away_team_id = match_data['away']['id']

                    # Check if venue exists, and if not, create it
                    venue_id = match_data['location']['id']
                    venue_name = match_data['location']['name']
                    venue_record = db.query(Venue).filter_by(id=venue_id).first()

                    if venue_record is None:
                        # Create the venue if it doesn't exist
                        venue_record = Venue(
                            id=venue_id,
                            name=venue_name
                        )
                        db.add(venue_record)
                        db.commit()
                        self.created_venue_count += 1  # Increment the created venue counter

                    # Check and update division's venue if not already assigned
                    if not identified_division_venue and division_record.venue_id is None and venue_record.name != "No Match This Week":
                        division_record.venue_id = venue_record.id  # Assign venue to division
                        db.add(division_record)
                        db.commit()
                        identified_division_venue = True  # Mark that the venue has been identified for the division

                    # Create a new schedule entry for each match
                    schedule_record = Schedule(
                        id=match_data['id'],  # Use match ID instead of schedule ID
                        description=schedule_data.get('description'),
                        date=schedule_date_only,
                        week_of_play=schedule_data.get('weekOfPlay'),
                        home_team_id=home_team_id,  # Home team foreign key
                        away_team_id=away_team_id,  # Away team foreign key
                        skip=schedule_data.get('skip', False),
                        division_id=division_record.id,  # Foreign key reference to division
                        venue_id=venue_record.id  # Foreign key reference to venue
                    )
                    db.add(schedule_record)
                    db.commit()
                    self.created_schedule_count += 1

                return True

        except Exception as e:
            self.error_schedule_count += 1
            db.rollback()
            print(f"Error creating schedule: {e}")
            return False
        finally:
            db.close()
