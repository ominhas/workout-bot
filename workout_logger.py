import pandas as pd
import os
import datetime


class WorkoutLogger:
    def __init__(self, data_file):
        self.data_file = data_file

    def __enter__(self):
        """Loads the database"""

        try:
            self.df = pd.read_csv(self.data_file, dtype={
                "name": 'str',
                "time": 'float64'})
        except Exception as e:
            print(f"Error while trying to open {self.data_file}")
            self.df = pd.DataFrame({
                "name": pd.Series([], dtype='str'),
                "time": pd.Series([], dtype='float64')})
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Saves the database"""

        self.df.to_csv(self.data_file, header=True, index_label=False)
        print(f"saved to {self.data_file}")

    def add_workout(self, name):
        """Adds workout to database and returns a time since last workout (or None)"""

        time = datetime.datetime.now().timestamp()
        new_row = pd.DataFrame([[name, time]], columns=["name", "time"])
        self.df = self.df.append(new_row, ignore_index=True)
        name_history = self.df[self.df["name"] == name]

        if len(name_history) == 1:
            return None, 1
        else:
            time1 = name_history.iloc[-2].time
            time2 = name_history.iloc[-1].time
            time_diff = datetime.datetime.fromtimestamp(time2) - datetime.datetime.fromtimestamp(time1)
            return time_diff, len(name_history)

    def remove_last_workout(self, name):
        """Removes name's last workout. Returns whether workout was successfully removed"""

        name_history_indeces = self.df['name'] == name
        if not any(name_history_indeces):
            return False
        else:
            # find index of last match in df
            matches = name_history_indeces.to_list()
            last_index = len(matches) - 1 - matches[::-1].index(True)
            self.df.drop(last_index, axis=0, inplace=True)
            return True

    def get_points(self, name):
        """Returns how many points name has"""
        return len(self.df[self.df["name"] == name])

    def reset_leaderboard(self):
        """Creates a backup and resets the leaderboard"""
        # Note: there will only be one backup
        self.df.to_csv(self.data_file+".bak", header=True, index_label=False)
        self.df = pd.DataFrame(columns=["name", "time"])

    def get_leaderboard(self):
        """Returns a ranked list of names, and a dictionary from name to points"""

        name_to_points = dict()
        name_to_last_workout = dict()
        for index, row in self.df.iterrows():
            if row["name"] not in name_to_points:
                name_to_points[row["name"]] = 0
            name_to_points[row["name"]] += 1
            name_to_last_workout[row["name"]] = row["time"]

        points_to_names = dict()
        for name, points in name_to_points.items():
            if points not in points_to_names:
                points_to_names[points] = set()
            points_to_names[points].add(name)

        sorted_names = []
        # sort by decreasing points
        for points in sorted(points_to_names)[::-1]:
            last_workout_to_names = dict()
            for name in points_to_names[points]:
                last_workout = name_to_last_workout[name]
                last_workout_to_names[last_workout] = name
            # sort by increasing last_workout time
            for last_workout in sorted(last_workout_to_names):
                name = last_workout_to_names[last_workout]
                sorted_names.append(name)

        return sorted_names, name_to_points

    def _show_data(self):
        print(self.df)
