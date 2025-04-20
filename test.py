from scripts.match import LocalMatch
from bot.randy import RandomBot

match = LocalMatch()
match.bind(RandomBot, RandomBot)
match.run()
match.results()
