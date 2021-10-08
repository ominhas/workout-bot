from workout_logger import WorkoutLogger
from tabulate import tabulate


def pretty_delta(diff):
    # based on https://stackoverflow.com/a/5164027
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s//60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s//3600)


def shorten_name(name, length=None):
    """Removes id portion of name, and if name is still longer than length,
    shortens it with ellipses. If length is None, then don't shorten with ellipses.
    """
    if "#" not in name:
        raise Exception("Expected name to be in format name#0000, but missing '#'")
    if length is not None and length < 3:
        raise Exception(f"shorten_name requires length >= 3, got {length}")

    name = name.split("#")[0]
    if length is None or len(name) < length:
        return name
    else:
        return name[:length-3] + "."*3



class CommandHandler:
    def handle_command(message):
        # remove surrounding white space
        text = message.content.strip()

        function = CommandHandler._find_command(text)
        if function is None:
            return None
        else:
            return function(message)

    def _find_command(text):
        if text.startswith("!"):
            command = text[1:]
            if command in COMMAND_MAP:
                return COMMAND_MAP[command]
        return None

    def _point(message):
        DATA_FILE = f"workouts-{message.guild.id}.csv"
        name = str(message.author)
        with WorkoutLogger(DATA_FILE) as wl:
            time_diff, points = wl.add_workout(name)
        if time_diff is None:
            response = "You now have 1 point. Congrats on the first workout!"
        else:
            response = f"You now have {points} points. The workout before this was {pretty_delta(time_diff)}."
        return response

    def _loser(message):
        DATA_FILE = f"workouts-{message.guild.id}.csv"
        name = str(message.author)
        with WorkoutLogger(DATA_FILE) as wl:
            removed_test = wl.remove_last_workout(name)
        if removed_test:
            with WorkoutLogger(DATA_FILE) as wl:
                points = wl.get_points(name)
            if points == 0:
                response = "You don't have any more points."
            elif points == 1:
                response = "You have 1 point left."
            else:
                response = f"You have {points} points left."
        else:
            response = "You don't have any points to remove!"
        return response

    def _scoreboard(message):
        DATA_FILE = f"workouts-{message.guild.id}.csv"
        with WorkoutLogger(DATA_FILE) as wl:
            sorted_names, name_to_points = wl.get_leaderboard()
        if not sorted_names:
            return "Scoreboard is empty!"
        table = []
        headers = ["Rank", "Name", "Points"]
        for i, name in enumerate(sorted_names):
            # using 14 because that's minimum screen size report by users
            shortened_name = shorten_name(name, 14)
            table.append([i+1, shortened_name, name_to_points[name]])
        return "```\n" + tabulate(table, headers) + "\n```"

    def _resetscoreboard(message):
        DATA_FILE = f"workouts-{message.guild.id}.csv"
        with WorkoutLogger(DATA_FILE) as wl:
            wl.reset_leaderboard()
        response = "Scoreboard has been reset!"
        return response

    def _help(message):
        help_items = [
            "!point - add a workout",
            "!loser - remove the last workout",
            "!scoreboard - show the rankings",
            "!resetscoreboard - remove all workouts",
            "!help - show this help text"
        ]
        return "\n".join(help_items)


COMMAND_MAP = {
    "point": CommandHandler._point,
    "loser": CommandHandler._loser,
    "scoreboard": CommandHandler._scoreboard,
    "resetscoreboard": CommandHandler._resetscoreboard,
    "help": CommandHandler._help
}
