from workout_logger import WorkoutLogger
import os

def clear_file(guild_id):
    filename = f"workouts-{guild_id}.csv"
    if os.path.exists(filename):
        os.remove(filename)


def test_enter_exit():
    test_id = "1234"
    clear_file(test_id)
    with WorkoutLogger(test_id) as wl:
        assert (wl.df.columns == ["member_id", "time"]).all()
        assert wl.df["member_id"].dtype == "string"
        assert wl.df["time"].dtype == "float64"
    clear_file(test_id)

    test_id = "4567"
    clear_file(test_id)
    with WorkoutLogger(test_id) as wl:
        wl.add_workout("1111")
    with WorkoutLogger(test_id) as wl:
        assert (wl.df.columns == ["member_id", "time"]).all()
        assert wl.df["member_id"].dtype == "string"
        assert wl.df["time"].dtype == "float64"
        assert (wl.df["member_id"] == ["1111"]).all()
        wl.add_workout("2222")
    with WorkoutLogger(test_id) as wl:
        assert (wl.df.columns == ["member_id", "time"]).all()
        assert wl.df["member_id"].dtype == "string"
        assert wl.df["time"].dtype == "float64"
        assert (wl.df["member_id"] == ["1111", "2222"]).all()
        wl.add_workout("1111")
    with WorkoutLogger(test_id) as wl:
        assert (wl.df["member_id"] == ["1111", "2222", "1111"]).all()
    clear_file(test_id)