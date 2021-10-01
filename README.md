# workout-bot

This creates a discord bot that you can use to track workouts, and show a leader board based on who has tracked the most points. It keeps a log of when the workout was added to break ties.

### Setup
1. Clone the repository
```bash
git clone https://github.com/zainhussaini/workout-bot.git
```

2. Create a Discord bot and generate a token at https://discord.com/developers/docs/topics/oauth2. At this step you can also add it to your Discord sever(s).

3. Set up redis server
```bash
sudo apt install redis
redis-cli
set 'DISCORD_TOKEN' '<insert token here>'
```
4. Install python packages
```bash
pip3 install -U discord.py tabulate pandas datetime redis
```
5. Run the program
```bash
python3 main.py
```

### TODO
1. Add unit testing
2. Add a voting system for resetscoreboard?
3. Separate data-logging for different servers under same bot instance
