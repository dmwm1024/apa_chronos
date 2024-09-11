
from app.models import Venue, Schedule, PoolTable
from app.extensions import SessionLocal
import itertools


class TableWizard:
    def __init__(self, venue, schedule_date):
        self.db = SessionLocal()
        self.venue = venue
        self.schedule_date = schedule_date

        # self.venue = self.db.query(Venue).filter_by(id=self.venue_id).first()
        self.schedules = self.db.query(Schedule).filter_by(venue_id=self.venue.id, date=self.schedule_date).all()

        # Preload schedule information and team names
        self.schedule_info = {schedule.id: schedule for schedule in self.schedules}
        self.team_names = {schedule.id: (schedule.home_team.name, schedule.away_team.name) for schedule in self.schedules}

        # Pool tables available at the venue
        self.available_tables = sorted(self.venue.pooltables, key=lambda t: int(t.name))

        # Precompute proximity scores between tables
        self.precomputed_proximity = self.precompute_proximity_scores()

        # Ensure tables are unassigned before running the algorithm
        self.unassign_existing_tables()

        # Generate all possible combinations and select the best solution
        best_solution = self.generate_all_combinations_and_select_best()
        self.assign_best_solution(best_solution)

    def precompute_proximity_scores(self):
        """ Precompute proximity scores between all table pairs. """
        proximity = {}
        for table1 in self.available_tables:
            for table2 in self.available_tables:
                if table1 != table2:
                    proximity[(table1.id, table2.id)] = 1 / (abs(int(table1.name) - int(table2.name)) + 1)
        return proximity

    def unassign_existing_tables(self):
        """ Unassign all existing pool table assignments for this venue/date. """
        for schedule in self.schedules:
            schedule.pooltable_id = None
            self.db.add(schedule)
        self.db.commit()

    def generate_all_combinations_and_select_best(self):
        """ Generate all possible permutations of match-table assignments and select the best one. """
        # Filter schedules to exclude 'Bye' matches
        valid_schedules = [schedule for schedule in self.schedules if
                           schedule.home_team.name != "Bye" and schedule.away_team.name != "Bye"]

        # Check if there are valid schedules and tables to work with
        if not valid_schedules:
            print(f"Division - {self.venue.division.name}: No valid schedules to assign tables to.")
            return None

        if len(self.available_tables) < len(valid_schedules):
            print(f"Division - {self.venue.name}: Not enough available tables to assign. Have ({len(self.available_tables)}) - Need: {len(valid_schedules)}")
            return None

        # Generate all possible table assignments (permutations)
        all_permutations = itertools.permutations(self.available_tables, len(valid_schedules))

        best_solution = None
        best_fitness = float('-inf')

        # Evaluate each permutation
        for table_assignment in all_permutations:
            # Create an assignment dictionary mapping schedule.id to table
            assignment = {schedule.id: table for schedule, table in zip(valid_schedules, table_assignment)}

            # Calculate the fitness of this permutation
            fitness = self.fitness_function(assignment)

            # If this is the best solution so far, store it
            if fitness > best_fitness:
                best_fitness = fitness
                best_solution = assignment

        # If no solution was found, return None
        if best_solution is None:
            print("No valid table assignments could be generated.")
            return None

        return best_solution

    def fitness_function(self, assignment):
        """ Score the assignment based on proximity and valid table assignments. """
        fitness = 0
        for schedule_id, assigned_table in assignment.items():
            home_team_name, away_team_name = self.team_names[schedule_id]

            # Skip 'Bye' matches
            if home_team_name == "Bye" or away_team_name == "Bye":
                continue

            # Calculate proximity bonuses for teams with the same name playing nearby
            for other_schedule_id, other_assigned_table in assignment.items():
                if schedule_id != other_schedule_id:
                    other_home_team, other_away_team = self.team_names[other_schedule_id]

                    if home_team_name == other_home_team or home_team_name == other_away_team:
                        table_pair = (assigned_table.id, other_assigned_table.id)
                        # Ensure the table pair exists in the precomputed proximity dictionary
                        if table_pair in self.precomputed_proximity:
                            fitness += self.precomputed_proximity[table_pair]

        return fitness

    def assign_best_solution(self, best_solution):
        """ Commit the best solution to the database by assigning tables to schedules. """
        if best_solution is None:
            print("No valid solution found. Skipping table assignment.")
            return

        for schedule_id, assigned_table in best_solution.items():
            schedule = self.schedule_info[schedule_id]
            schedule.pooltable_id = assigned_table.id
            self.db.add(schedule)

        self.db.commit()
