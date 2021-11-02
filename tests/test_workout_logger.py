from workout_logger import WorkoutLogger
import pandas as pd
import os
from pathlib import Path

def clear_file(guild_id):
    filename = Path.home() / ".workout_bot" / f"workouts-{guild_id}.csv"
    if os.path.exists(filename):
        os.remove(filename)


def check_df(df: pd.DataFrame, member_ids: "list[str]", times: "list[float]"):
    assert len(member_ids) == len(times)

    assert len(df.columns) == 2
    assert df.columns.tolist() == ["member_id", "time"]
    assert not df.isnull().values.any()

    assert len(df["member_id"]) == len(member_ids)
    assert df["member_id"].tolist() == member_ids
    assert len(df["time"]) == len(member_ids)
    assert df["time"].tolist() == times


def test_enter_exit():
    test_id = "1234"
    clear_file(test_id)
    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, [], [])
    clear_file(test_id)

def test_add_workout():
    test_id = "4567"
    clear_file(test_id)
    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, [], [])
        wl.add_workout("1111", 100.2)
        check_df(wl.df, ["1111"], [100.2])

    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, ["1111"], [100.2])
        wl.add_workout("2222", 100.3)
        check_df(wl.df, ["1111", "2222"], [100.2, 100.3])

    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, ["1111", "2222"], [100.2, 100.3])
        wl.add_workout("1111", 101.0)
        check_df(wl.df, ["1111", "2222", "1111"], [100.2, 100.3, 101.0])

    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, ["1111", "2222", "1111"], [100.2, 100.3, 101.0])
    clear_file(test_id)

def test_remove_workout():
    test_id = "0001"
    clear_file(test_id)
    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, [], [])
        wl.add_workout("1111", 1e3)
        check_df(wl.df, ["1111"], [1e3])

    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, ["1111"], [1e3])
        assert wl.remove_last_workout("2222") == False
        check_df(wl.df, ["1111"], [1e3])
        assert wl.remove_last_workout("1111") == True
        check_df(wl.df, [], [])
        assert wl.remove_last_workout("1111") == False
        check_df(wl.df, [], [])

    with WorkoutLogger(test_id) as wl:
        check_df(wl.df, [], [])
        wl.add_workout("2222", 1e3)
        wl.add_workout("2222", 2e3)
        wl.add_workout("2222", 3e3)
        wl.add_workout("2222", 4e3)
        check_df(wl.df, ["2222"]*4, [1e3, 2e3, 3e3, 4e3])
        assert wl.remove_last_workout("2222") == True
        assert wl.remove_last_workout("2222") == True
        check_df(wl.df, ["2222"]*2, [1e3, 2e3])
        wl.add_workout("1111", 5e3)
        check_df(wl.df, ["2222", "2222", "1111"], [1e3, 2e3, 5e3])
        assert wl.remove_last_workout("2222") == True
        check_df(wl.df, ["2222", "1111"], [1e3, 5e3])
    clear_file(test_id)

def test_get_points():
    test_id = "9999"
    clear_file(test_id)
    with WorkoutLogger(test_id) as wl:
        assert wl.get_points("1111") == 0
        assert wl.get_points("2222") == 0
        assert wl.get_points("") == 0
        wl.add_workout("1111", 1e3)
        assert wl.get_points("1111") == 1
        assert wl.get_points("2222") == 0
        wl.remove_last_workout("1111")
        assert wl.get_points("1111") == 0

        wl.add_workout("1111", 1e3)
        for i in range(20):
            wl.add_workout("2222", 0)
        assert wl.get_points("1111") == 1
        assert wl.get_points("2222") == 20

        wl.add_workout("1111", 1e3)
        assert wl.get_points("1111") == 2
        assert wl.get_points("2222") == 20
    clear_file(test_id)