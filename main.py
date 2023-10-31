from game import process_game
from scraper_util_avliu.util import get_soup

import argparse
import re
from datetime import datetime, timedelta


# Get games from today's date, e.g.: https://www.nba.com/games?date=2023-10-25
# class GameCard, class a href inside. Can create the URL below
def get_game_ids(day):

    print(f'get game_ids for day {day}')

    url = f'https://www.nba.com/games?date={day}'
    soup = get_soup(url)

    css = 'section[class^="GameCard"] a'
    games = soup.select(css)
    games = [game['href'] for game in games]
    games = filter(lambda x: len(x.split('/')) == 3 and '?' not in x, games)
    games = list(set(list(games)))
    games = [game.split('/')[-1] for game in games]
    game_ids = games

    print(f'game_ids: {game_ids}')

    return game_ids


def process_day(day):
    print(f'processing day {day}')
    game_ids = get_game_ids(day)

    # TODO: testing
    #game_ids = [game_ids[-1]] 

    for game_id in game_ids:
        process_game(game_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date", required=False, help="date in format YYYY-MM-DD (at most 4 days ago; default yesterday)"
    )
    args = parser.parse_args()
    date = args.date

    if not date:
        date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # date should be in right format
    assert(re.search('\d\d\d\d-\d\d-\d\d', date) is not None)

    process_day(date)


if __name__ == '__main__':
    main()


