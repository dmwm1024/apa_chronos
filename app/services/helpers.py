import pdfplumber
import re
from app.models import Division, Team


class Schedule:
    def __init__(self, pdf_path):
        self.Extractor = ScheduleExtractor(pdf_path).extract_all()
        self.full_text = self.Extractor.full_text
        self.division_number = self.Extractor.division_number
        self.teams = self.Extractor.teams
        self.matchups = self.Extractor.matchups


class ScheduleExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.full_text = ""
        self.division_number = None
        self.matchups = []
        self.teams = []

    def extract_pdf_text(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                self.full_text += page.extract_text()

    def extract_division_number(self):
        division_pattern = re.compile(r"(\d{3})\s+-\s+")
        match = division_pattern.search(self.full_text)
        if match:
            self.division_number = match.group(1)
            return match.group(1)
        else:
            return None

    def extract_team_mapping(self):
        division = Division.query.filter_by(Division_Number=self.division_number).first()

        if division:
            division_number = division.Division_Number
            venue_name = division.Venue_rel.Venue_Name

            pattern = rf"({division_number}\d+)\s([A-Za-z0-9\s'?]+)(?={venue_name})"
            matches = re.findall(pattern, self.full_text)

            teams = [{
                "Team Number": match[0],
                "Team Name": match[1].strip()
            } for match in matches]

            for team in teams:
                self.teams.append(team)

            self.teams = teams

    def extract_matchups(self):
        week_pattern = re.compile(r"(\d{1,2})\s+(\d{2}/\d{2}/\d{4})\s+((?:\d+-\d+\s+)+)")
        for match in week_pattern.finditer(self.full_text):
            week_number = match.group(1)
            week_date = match.group(2)
            matchups = match.group(3).strip().split()

            week_matchups = []
            for matchup in matchups:
                home_team, away_team = matchup.split('-')
                week_matchups.append({"home_team": home_team, "away_team": away_team})

            self.matchups.append({"week": week_number, "date": week_date, "matchups": week_matchups})

        if self.matchups:
            return self.matchups
        else:
            return None

    def extract_all(self):
        self.extract_pdf_text()
        self.extract_division_number()
        self.extract_team_mapping()
        self.extract_matchups()
        return self

    def debug_display_results(self):
        print(f"Division Number: {self.division_number}")

        print("\nMatchups:")
        for week in self.matchups:
            print(f"Week {week['week']} ({week['date']}):")
            for matchup in week['matchups']:
                print(f"  {matchup['home_team']} vs {matchup['away_team']}")
            print()

