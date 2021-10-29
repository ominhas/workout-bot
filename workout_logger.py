import pathlib
import pandas as pd
import datetime
import os
from pathlib import Path


DATA_FOLDER = pathlib.Path.home() / ".workout_bot"

class WorkoutLogger:
    def __init__(self, guild_id: str):
        self.guild_id = guild_id
        DATA_FOLDER.mkdir(parents=True, exist_ok=True)
        self.data_file = DATA_FOLDER / f"workouts-{guild_id}.csv"

    def __enter__(self):
        """Loads the database"""

        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file, dtype={
                "member_id": 'string',
                "time": 'float64'})
        else:
            print(f"Creating a new file at {self.data_file}")
            self.df = pd.DataFrame({
                "member_id": pd.Series([], dtype="string"),
                "time": pd.Series([], dtype="float64")})
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Saves the database"""
        self.df.to_csv(self.data_file, header=True, index_label=False)

    def add_workout(self, member_id: str, time: float):
        """Adds workout to database and returns a time since last workout (or None)"""

        new_row = pd.DataFrame([[member_id, time]], columns=["member_id", "time"])
        self.df = self.df.append(new_row, ignore_index=True)
        member_history = self.df[self.df["member_id"] == member_id]

        if len(member_history) == 1:
            return None, 1
        else:
            last_workout_date = datetime.datetime.fromtimestamp(member_history.iloc[-2].time)
            return last_workout_date, len(member_history)

    def remove_last_workout(self, member_id: str) -> bool:
        """Removes member's last workout. Returns whether workout was successfully removed"""

        member_history_indeces = self.df["member_id"] == member_id
        if not any(member_history_indeces):
            return False
        else:
            # find index of last match in df
            matches = member_history_indeces.to_list()
            last_index = len(matches) - 1 - matches[::-1].index(True)
            self.df.drop(last_index, axis=0, inplace=True)
            return True

    def get_points(self, member_id: str) -> int:
        """Returns how many points member has"""
        return len(self.df[self.df["member_id"] == member_id])

    def reset_leaderboard(self):
        """Creates a backup and resets the leaderboard"""
        # save a backup with date and time of when backup was created
        time_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        save_data_file = DATA_FOLDER / f"workouts-{self.guild_id}-{time_str}.csv"
        self.df.to_csv(save_data_file, header=True, index_label=False)

        # create a new dataframe which will be saved over current on in __exit__
        self.df = pd.DataFrame(columns=["member_id", "time"])

    def get_leaderboard(self) -> "tuple[list, dict]":
        """Returns a ranked list of members, and a dictionary from member_id to points"""
        member_id_to_points = dict()
        member_id_to_last_workout = dict()
        for index, row in self.df.iterrows():
            if row["member_id"] not in member_id_to_points:
                member_id_to_points[row["member_id"]] = 0
            member_id_to_points[row["member_id"]] += 1
            member_id_to_last_workout[row["member_id"]] = row["time"]

        points_to_member_ids = dict()
        for member_id, points in member_id_to_points.items():
            if points not in points_to_member_ids:
                points_to_member_ids[points] = set()
            points_to_member_ids[points].add(member_id)

        sorted_member_ids = []
        # sort by decreasing points
        for points in sorted(points_to_member_ids)[::-1]:
            last_workout_to_member_ids = dict()
            for member_id in points_to_member_ids[points]:
                last_workout = member_id_to_last_workout[member_id]
                last_workout_to_member_ids[last_workout] = member_id
            # sort by decreasing last_workout time
            for last_workout in sorted(last_workout_to_member_ids)[::-1]:
                member_id = last_workout_to_member_ids[last_workout]
                sorted_member_ids.append(member_id)

        return sorted_member_ids, member_id_to_points

    def _show_data(self):
        print(self.df)
