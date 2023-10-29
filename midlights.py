from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scraper_util_avliu.util import get_soup, get_selenium_driver

# For downloading and stitching videos
import shutil
import os
import wget
import subprocess
import datetime
import random
import re

# Multiprocessing
from multiprocessing import Pool
from itertools import starmap



def is_url(link):
    return link.startswith('https://')


# Get games from today's date, e.g.: https://www.nba.com/games?date=2023-10-25
# class GameCard, class a href inside. Can create the URL below
def get_game_ids(day):

    print(f'get game_ids for day {day}')

    # day should be in right format
    assert(re.search('\d\d\d\d-\d\d-\d\d', day) is not None)

    url = f'https://www.nba.com/games?date={day}'
    soup = get_soup(url)

    css = 'section[class^="GameCard"] a'
    games = soup.select(css) 
    games = [game['href'] for game in games]
    games = filter(lambda x: len(x.split('/'))==3 and '?' not in x, games)
    games = list(set(list(games)))
    games = [game.split('/')[-1] for game in games]
    game_ids = games

    print(f'game_ids: {game_ids}')

    return game_ids 


def get_play_info(play_elem):
    play_text = play_elem.text
    if re.search(r"\bShot\b|\bLayup\b|\bDunk\b", play_text):
        play_type = 'good'
    elif re.search(r"\bFoul\b|\bTurnover\b|\bSteal\b|\bRebound\b", play_text):
        play_type = 'ok'
    elif re.search(r"\bFree Throw\b|\bJump Ball\b", play_text):
        play_type = 'na'
    else:
        play_type = 'na'
    href = play_elem.get_attribute('href')
    info = {
        'text': play_text,
        'play_type': play_type,
        'elem': play_elem,
        'url': href
    }
    return info


# get links to plays
def get_play_links(game_id, sample_amount=40):
    # TODO: testing
    #sample_amount = 4

    print(f'get play links for game_id {game_id}')

    game_url = f'https://www.nba.com/game/{game_id}/play-by-play?period=All'
    driver = get_selenium_driver(headless=True)
    driver.get(game_url)

    elems = driver.find_elements(By.CSS_SELECTOR,"article[class^='GamePlayByPlay'] a")
    print(f'got {len(elems)} total elements')

    # get info
    elems_info = [get_play_info(play_elem) for play_elem in elems]
    elems_info = [elems_info[i] | {'index':i} for i in range(len(elems_info))] 

    # (1) filter, (2) sample by quota, (3) stitch together and sort, (4) grab links
    good_quota = int(sample_amount * 0.8)
    ok_quota = int(sample_amount * 0.2)
    good_elems = list(filter(lambda x: x['play_type']=='good', elems_info))
    ok_elems = list(filter(lambda x: x['play_type']=='ok', elems_info))
    sample = random.sample(good_elems, min(good_quota, len(good_elems))) + random.sample(ok_elems, min(ok_quota, len(ok_elems)))
    sample = sorted(sample, key=lambda x: x['index'])
    sampled_play_links = [elem['url'] for elem in sample]

    print(f'sampled play links: {sampled_play_links}')

    return sampled_play_links


# Step 2: get links to mp4
def get_clip_link(play_link):
    print(f'get mp4 link from play link {play_link}')
    driver = get_selenium_driver(headless=False)

    driver.get(play_link)

    # wait for video player to show
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Video Player"]'))
    )
    # get the mp4 from the video player 
    mp4_search_str = 'div[aria-label="Video Player"] video'
    clip_link = driver.find_element(By.CSS_SELECTOR, mp4_search_str).get_attribute('src')

    print(f'mp4 link: {clip_link}')
    return clip_link 


# Step 3: download mp4
def download_clip(clip_link, download_dir='./temp'):
    print(f'download {clip_link} into {download_dir}')
    clip_link = clip_link.strip()
    filename = wget.download(clip_link, out=download_dir)
    return filename


def process_play(play_link, download_dir):
    assert(is_url(play_link))

    # get the mp4 clip link
    clip_link = get_clip_link(play_link)
    # download the mp4 and return the filename
    if is_url(clip_link) and 'missing' not in clip_link:
        filename = download_clip(clip_link, download_dir)
        return filename
    else:
        return None


def stitch_clips(concat_file='./temp/concat.txt', outputfile='./output.mp4'):
    # Could implement this with ffmpeg-python if I get a chance to learn it in-depth
    print(f'stitching clips listed in {concat_file} into {outputfile}')
    subprocess.run(f'ffmpeg -f concat -i {concat_file} -c copy {outputfile}', shell=True)


def process_game(game_id, clip_links = None):
    print(f'processing game {game_id}')
    start_time = datetime.datetime.now()
    print(f'start time: {start_time}')

    play_links = get_play_links(game_id)
    temp_dir = f'temp_{game_id}' 
    os.mkdir(temp_dir)

    # for every play, download its mp4
    params = [(play_link, temp_dir) for play_link in play_links]
    with Pool() as p:
        filenames = p.starmap(process_play, params) 
    print(f'filenames: {filenames}')

    # create the concat file and write to it
    concat_filename = f'{temp_dir}/concat.txt'
    with open(concat_filename, 'w') as concat_file:
        for filename in filenames:
            if filename:
                concat_file.write('file ' + filename[len(temp_dir)+1:] + '\n')

    # stitch the clips
    stitch_clips(concat_file=concat_filename,outputfile=f'{game_id}.mp4')
    shutil.rmtree(temp_dir)

    print(f'done processing game {game_id}')
    end_time = datetime.datetime.now()
    print(f'end time: {end_time}')
    print(f'total time: {(end_time-start_time).total_seconds()} seconds')
    print()


def process_day(day):
    print(f'processing day {day}')
    game_ids = get_game_ids(day)

    # TODO: testing
    #game_ids = [game_ids[-1]] 

    for game_id in game_ids:
        process_game(game_id)


def main():
    #url = 'https://www.nba.com/stats/events?CFID=&CFPARAMS=&GameEventID=21&GameID=0022300063&Season=2023-24&flag=1&title=Murray%2018%27%20Pullup%20Jump%20Shot%20(2%20PTS)'
    #clip_link = get_clip_link(url) 
    #print(f'clip link: {clip_link}')

    #clip_links = ['https://videos.nba.com/nba/pbp/media/2023/10/25/0022300072/478/3dad8de7-c5b5-ffec-293c-82fd844bc571_1280x720.mp4', 'https://videos.nba.com/nba/pbp/media/2023/10/25/0022300072/114/54eeb1fc-93b2-8a3c-6a3b-3c19574b2399_1280x720.mp4', 'https://videos.nba.com/nba/pbp/media/2023/10/25/0022300072/30/25b43b12-3c2a-fc0b-edf2-310b458c5c4d_1280x720.mp4']

    day = '2023-10-28'
    process_day(day)


if __name__=='__main__':
    main()






