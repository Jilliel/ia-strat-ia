from scripts.match import LocalMatch, APIMatch
from bot.randy import RandomBot

def test_local():
    """
    Teste un match en local.
    """
    match = LocalMatch()
    match.bind(RandomBot, RandomBot)
    match.run()
    match.results()

def test_distant():
    """
    Teste un match via l'API.
    """
    match = APIMatch(port="8080")
    match.bind(RandomBot, RandomBot)
    match.run()

if __name__ == "__main__":
    test_local()
    #test_distant()