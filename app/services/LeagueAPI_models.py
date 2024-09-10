from dataclasses import dataclass
from typing import List


# Define the Session class
@dataclass
class Session:
    id: int
    name: str


# Define the Division class
@dataclass
class Division:
    id: int
    name: str
    number: str
    format: str
    type: str
    nightOfPlay: str
    isMine: bool
    session: Session


# Define the League class
@dataclass
class League:
    id: int
    currentSessionId: int
    divisions: List[Division]


# Define the Data structure
@dataclass
class LeagueData:
    league: League


# Top-level structure
@dataclass
class ResponseData:
    data: LeagueData


class DivisionData:
    url = 'https://gql.poolplayers.com/graphql'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "query": """
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
            """,
        "variables": {
            "slug": "jacksonville",
            "session": None
        }
    }



