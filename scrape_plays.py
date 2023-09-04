
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from requests_html import HTMLSession
from util import get_soup, get_selenium_driver

import random

# Step 1: get links to plays

game_url = 'https://www.nba.com/game/cle-vs-nyk-0042200134/play-by-play?period=All'

session = HTMLSession()
r = session.get(game_url)
r.html.render()
plays = r.html.find("article[class^='GamePlayByPlay'] a")
links = list(map(lambda x: 'https://nba.com'+x.attrs['href'], plays))

print(links)


# Step 2: get links to mp4

# sample 40 videos
links = random.sample(links, 40)
driver = get_selenium_driver()

vids = []
for link in links:

    driver.get(link)

    element = WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main video"))
    )

    vid = driver.find_element(By.CSS_SELECTOR, 'main video').get_attribute('src')
    vids.append(vid)
    print(vid)

print(vids)

with open('./video_links.txt', 'w') as wf:
    for vid in vids:
        wf.write(vid+'\n')

# Step 3: download mp4