import requests


class LeagueAPI:
    def __init__(self, base_url):
        """
        Initialize the LeagueAPI class.

        Parameters:
        - base_url (str): The base URL for the GraphQL API.
        - For the APA League, this will always be: "https://gql.poolplayers.com/graphql"
        """
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }

    def query(self, query_txt, variables):
        """
        This is a wrapper used by all underlying API functions.
        Sends a POST request to the GraphQL API with the given query and variables.

        Parameters:
        - query_txt (str): The GraphQL query string.
        - variables (dict): A dictionary of variables for the query.

        Returns:
        - dict: The JSON response from the API.

        Raises:
        - HTTPError: If the request to the API fails.
        """
        payload = {
            "query": query_txt,
            "variables": variables
        }

        # Send POST request and check for response status
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def query_league(self, slug):
        """
        Queries league information based on the league's slug.

        Parameters:
        - slug (str): The unique identifier for the league. For the Jacksonville league, this is "jacksonville".

        Returns:
        - dict: The league details including ID, current session, name, and other metadata.
        """
        variables = {
            "slug": slug
        }

        query_txt = '''
        query query_league($slug: String!) {
            league(slug: $slug) {
                id
                currentSessionId
                name
                slug
                email
                phone
                homePageUrl
                facebookUrl
                officeHours
                logo
                byLaws {
                    id
                    url
                    __typename
                }
                __typename
            }
        }
        '''
        return self.query(query_txt, variables)

    def query_divisions(self, slug, session_id):
        """
        Queries information on all divisions in a given league session.

        Parameters:
        - slug (str): The league slug.
        - session_id (int): The ID of the session to query.

        Returns:
        - dict: A list of divisions with details such as ID, name, teams, and play schedule.
        """
        variables = {
            "slug": slug,
            "session": session_id
        }

        query_txt = '''
        query leagueLayout($slug: String!, $session: Int) {
            league(slug: $slug) {
                divisions(session: $session) {
                    id
                    name
                    number
                    format
                    type
                    nightOfPlay
                    teams {
                        id
                        name
                        number
                        isBye
                    }
                }
                __typename
            }
        }
        '''
        return self.query(query_txt, variables)

    def query_division(self, division_id):
        """
        Queries specific details for a single division by division ID.

        Parameters:
        - division_id (int): The unique identifier for the division.

        Returns:
        - dict: The division information including ID, number, format, and type.
        """
        variables = {
            "id": division_id
        }

        query_txt = '''
        query divisionSchedule($id: Int!) {
            division(id: $id) {
                id
                number
                format
                type
            }
        }
        '''
        return self.query(query_txt, variables)

    def query_division_schedule(self, division_id):
        """
        Retrieves the schedule and match details for a specified division.

        Parameters:
        - division_id (int): The unique identifier for the division.

        Returns:
        - dict: The schedule and match details for the division, including match IDs, teams, and locations.
        """
        variables = {
            "id": division_id
        }

        query_txt = '''
        query divisionSchedule($id: Int!) {
            division(id: $id) {
                id
                number
                format
                type
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
                        isPlayoff
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
                        }
                        away {
                            id
                            name
                            number
                        }
                    }
                }
                scheduleInEdit
            }
        }
        '''
        return self.query(query_txt, variables)

    def query_league_venues(self, slug, session_id):
        """
        Retrieves information on venues associated with league matches in a session.

        Parameters:
        - slug (str): The unique identifier for the league.
        - session_id (int): The ID of the session to query.

        Returns:
        - dict: Details about the venues used in the session, including IDs and names.
        """
        variables = {
            "slug": slug,
            "session": session_id
        }

        query_txt = '''
        query leagueLayout($slug: String!, $session: Int) {
            league(slug: $slug) {
                id
                currentSessionId
                divisions(session: $session) {
                    id
                    schedule {
                        matches {
                            location {
                                id
                                name
                            }
                        }
                    }
                }
                __typename
            }
        }
        '''
        return self.query(query_txt, variables)
