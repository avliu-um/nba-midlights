from util import get_clock_seconds, get_score_tuple, stitch_clips, is_url
from scraper_util_avliu.util import get_selenium_driver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import shutil
import os
import random
import re
import datetime
import wget
import time

from multiprocessing import Pool


# get play elements for given game id
def get_play_elems(game_id):
    game_url = f'https://www.nba.com/game/{game_id}/play-by-play?period=All'
    print(f'get play links for game_id {game_id}, url {game_url}')
    driver = get_selenium_driver(headless=True)
    driver.get(game_url)

    # get parent elems
    play_elems = driver.find_elements(By.CSS_SELECTOR,"article[class^='GamePlayByPlay']")

    return play_elems


# for a list of play elements, get the associated info
def get_play_infos(play_elems):
    all_plays = []
    
    prev_time = 900
    period = 1
    prev_score = (0, 0)
    idx = 0
    for play in play_elems:
        clock_search_str = 'span[class^="GamePlayByPlayRow_clock"]'
        score_search_str = 'span[class^="GamePlayByPlayRow_scoring"]'
        play_search_str = 'a'
    
        clock_elems = play.find_elements(By.CSS_SELECTOR, clock_search_str)
        score_elems = play.find_elements(By.CSS_SELECTOR, score_search_str)
        play_elems = play.find_elements(By.CSS_SELECTOR, play_search_str)
    
        clock = get_clock_seconds(clock_elems[0].text) if len(clock_elems) > 0 else -1
        score = get_score_tuple(score_elems[0].text) if len(score_elems) > 0 else ()
        if len(score) > 0:
            prev_score = score
        else:
            score = prev_score
        href = play_elems[0].get_attribute('href') if len(play_elems) > 0 else ''
        play_text = play_elems[0].text if len(play_elems) > 0 else ''
    
        # generate "tiers" of plays, depending on importance (to me)
        if re.search(r"\bShot\b|\bLayup\b|\bDunk\b", play_text):
            play_type = 'good'
        elif re.search(r"\bFoul\b|\bTurnover\b|\bSteal\b|\bRebound\b", play_text):
            play_type = 'ok'
        elif re.search(r"\bFree Throw\b|\bJump Ball\b", play_text):
            play_type = 'na'
        else:
            play_type = 'na'
    
        #print(f'index: {idx}, period: {period}, clock: {clock}, score: {score}, play type: {play_type}, text: {play_text}')
    
        info = {
            'index': idx,
            'period': period,
            'clock': clock,
            'score': score,
            'play_type': play_type,
            'text': play_text,
            'url': href,
        }
        all_plays.append(info)
        
        if clock > prev_time:
            period += 1
        prev_time = clock
        idx += 1

    if len(all_plays)>0:
        print(f'final period: {all_plays[-1]["period"]}, final score: {all_plays[-1]["score"]}')
    return all_plays


# given a list of play info dicts, sample it
def sample_plays(all_plays, sample_amount=50, good_ratio=0.7, ok_ratio=0.3):
    
    # filter by url exists 
    all_plays = list(filter(lambda x: len(x['url'])>0, all_plays))

    good_elems = list(filter(lambda x: x['play_type']=='good', all_plays))
    ok_elems = list(filter(lambda x: x['play_type']=='ok', all_plays))

    # get clutch plays
    clutch_plays = []
    clutch_periods = []
    clutch_time_cutoff=300 # the cutoff of "clutch" time, using NBA definition it is 5 minutes
    clutch_clip_time = 120 # time in the period from which we scrape plays (2 minutes)
    for period in range(4, all_plays[-1]['period']+1):
        period_plays = list(filter(lambda x: x['period']==period, all_plays))
        i = len(period_plays)-1
        close = False
        while i>0:
            score, clock = period_plays[i]['score'], period_plays[i]['clock']
            if abs(score[0]-score[1])<=5:
                close = True
            if clock>clutch_time_cutoff:
                break
            i -= 1

        if close:
            clutch_periods.append(period)
            clutch_period_plays = list(filter(lambda x: x['clock']<clutch_clip_time and x['play_type']=='good', period_plays))
            clutch_plays += clutch_period_plays

    good_quota = int(sample_amount * good_ratio)
    ok_quota = int(sample_amount * ok_ratio)    
    print(f'{len(good_elems)} good, {len(ok_elems)} ok, and {len(clutch_plays)} clutch to select from')

    # if clutch time is in regulation, then take away from the ok clips
    if 4 in clutch_periods:
        q4_clutch_count = len(list(filter(lambda x: x['period']==4, clutch_plays)))
        print(f'old: good={good_quota}, ok={ok_quota}, q4_clutch={q4_clutch_count}')
        if q4_clutch_count > ok_quota:
            good_quota -= (q4_clutch_count - ok_quota)
            good_quota = max(0, good_quota)
            ok_quota = 0
        else:
            ok_quota -= q4_clutch_count
        print(f'new: good={good_quota}, ok={ok_quota}, q4_clutch={q4_clutch_count}')


    # combine good clips, ok clips, and clutch clips
    good_sample = random.sample(good_elems, min(good_quota, len(good_elems)))
    ok_sample = random.sample(ok_elems, min(ok_quota, len(ok_elems)))
    sampled_plays = good_sample + ok_sample + clutch_plays
    sampled_plays.sort(key=lambda x: x['index'])

    print(f'{len(good_sample)} good, {len(ok_sample)} ok, {len(clutch_plays)} clutch -> {len(sampled_plays)} total clips')

    return sampled_plays


def download_clip(clip_link, download_dir='./temp'):
    print(f'download {clip_link} into {download_dir}')
    assert(is_url(clip_link) and 'missing' not in clip_link)
    clip_link = clip_link.strip()
    filename = wget.download(clip_link, out=download_dir)
    return filename


# given a game id, get plays and associated info, sample them, download them, and stitch them
def process_game(game_id):
    print(f'processing game {game_id}')
    start_time = datetime.datetime.now()
    print(f'start time: {start_time}')

    play_elems = get_play_elems(game_id)
    play_infos = get_play_infos(play_elems)
    sampled_plays = sample_plays(play_infos, sample_amount=50)
    sampled_play_links = [elem['url'] for elem in sampled_plays]
    print(f'sampled play links: {sampled_play_links}')

    # get mp4 link from each play link
    clip_links = []
    driver = get_selenium_driver(headless=False)
    time.sleep(10) # need otherwise first link isn't found

    for play_link in sampled_play_links:
        print(f'get mp4 link from play link {play_link}')

        driver.get(play_link)
        try:
            # wait for video player to show
            WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Video Player"]'))
            )
            # get the mp4 from the video player 
            mp4_search_str = 'div[aria-label="Video Player"] video'
            clip_link = driver.find_element(By.CSS_SELECTOR, mp4_search_str).get_attribute('src')
            assert(is_url(clip_link) and 'missing' not in clip_link)
            clip_links.append(clip_link)
            print(f'mp4 link: {clip_link}')
        except:
            print(f'mp4 link not found')
            pass


    # in parallel, download mp4's
    temp_dir = f'temp_{game_id}' 
    os.mkdir(temp_dir)

    # for every play, download its mp4
    params = [(clip_link, temp_dir) for clip_link in clip_links]
    with Pool() as p:
        filenames = p.starmap(download_clip, params) 
    print(f'filenames: {filenames}')

    # create the concat file and write to it
    concat_filename = f'{temp_dir}/concat.txt'
    with open(concat_filename, 'w') as concat_file:
        for filename in filenames:
            if filename:
                concat_file.write('file ' + filename[len(temp_dir)+1:] + '\n')

    # stitch the clips
    stitch_clips(concat_file=concat_filename, outputfile=f'{game_id}.mp4')
    shutil.rmtree(temp_dir)

    print(f'done processing game {game_id}')
    end_time = datetime.datetime.now()
    print(f'end time: {end_time}')
    print(f'total time: {(end_time-start_time).total_seconds()} seconds')
    print()


if __name__ == '__main__':
    test_game_id = 'lal-vs-sac-0022300100'
    process_game(test_game_id)
