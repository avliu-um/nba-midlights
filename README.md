# NBA Midlights

This project generates video reels for basketball games that are more representative of the game than the usual "highlight" videos that you find online.
This repo contains code for scraping NBA.com for game clips and combining them into these video reels.
The code utilizes several web scraping tactics, parallelization, and video stitching tools.

I've been running this pipeline since late October 2023, and already I've made interesting observations about games that cannot be identified in highlight reels, e.g.:
* The defensive gravity of Victor Wembenyama even when he isn't blocking a shot.
* Jaren Jackson Junior's foul-prone lapses.

## Motivation

The inspiration from this project comes from my experience and current problems with media consumption options as a serious NBA fan. Like most people, I cannot watch entire games often because I'm busy with work, school, etc. Instead, I rely on clipped versions of the game, called highlight videos. 

However, the issue with highlight videos is that they only show made baskets. Times where players score. To the casual NBA fan, that's maybe what they want to see. For me though, such a summarization of an NBA game is too narrow. 

First, highlight videos systematically biases towards volume scoring, which led me to associate those that routinely showed up in highlights with great players. For instance, Jordan Poole, a highlight-driven player who in reality routinely demonstrates poor shot selection, is seen in a positively-biased light. Players who often make mistakes that aren't captured in highlights, such as turnovers, fouls, and bad shot selection, do not get their fair shake. Second, highlight videos limit us from seeing parts of the game that are equally as beautiful as buckets, such as great defensive schemes and individual defensive performances.

Enter, NBA Midlights, a web-scraping and video-stiching project that creates more realistic, natural, and consistent video reels of NBA games.

## Implementation

This repo contains the code for NBA Midlights. 

See [here](https://drive.google.com/drive/folders/1T6EhLKyoYiK7uTHnVipAZrLA72qDXanN?usp=sharing) for example Midlight videos.

We use several web scraping tools to crawl NBA.com and find relevant clips, including BeautifulSoup and Selenium. 
In the most general use case, our code accepts a date as input, and then generates Midlight videos for every game that occured on that date. 
The process for generating these videos is as follows (all info is scraped from NBA.com):
* For the given date, find the game ID's for every game that occured on that day (e.g. "phi-vs-tor-0022300092").
* To process a game, collect all plays that occured during that game (e.g. "Player X missed layup"), sample a subset of the plays, process the sampled plays, then stitch them together into one video.
* To process the play, we load the clip representing the play, grab the mp4 for the clip, and then download the clip.

For many web scraping tasks, I borrow helper functions from my own PyPI package, [scraper-util-avliu](https://pypi.org/project/scraper-util-avliu/).

Currently, sampling plays from a game is implemented with the following heuristic: In regulation, 70% of the plays are shots (jump shot, layup, dunk, etc.) regardless of make or miss, and 30% of the plays are other categories that are still relevant to the game (Foul, turnover, steal, rebound). 
If there are any clutch plays in regulation (defined below), then they take the place of these plays, starting with non-shot plays, and then shot plays if necessary.
Clutch plays in overtime are appended to the end of the video.

We define **clutch plays** as a play during the last 2 minutes of a **clutch period**, where a clutch period is a period that is within 10 points with less than 5 minutes remaining in the game, as defined by the NBA.
Having clutch plays in regulation replace other regulation plays helps us maintain consistent video lengths (we don't want longer videos just because there's more clutch plays).
Appending clutch plays in overtime to the end of the video (i.e. not replacing) gives us room to capture clips from both regulation and OT, and is rare enough in practice that we don't need to worry about concistently creating longer videos.

This heuristic can be edited to suit viewer's needs, and in the future will be easily customizable for the end-user.

Since there are many plays per game (default is about 50), it would be very time consuming to implement play processing sequentially.
This is especially true because processing a play involves loading a non-headless Selenium driver and downloading the mp4 link.
Thus, we use Python's multiprocessing package to parallelize play processing.
Overall, parallelization has brought game processing tiem from over 30 minutes per game to 2-4 minutes per game (running locally).

## Code
To run the code, enter `python main.py --date='YYYY-MM-DD'`, with your specified date, or no date which defaults to yesterday.

Included files:
* main.py- runs the code for a specified day.
* game.py- uses BeautifulSoup and Selenium to sample clips for a given game.
* requirements.txt- Python packages.
* random.ipynb- personal notebook for testing different code functionality

Requirements:
* Python packages (see requirements.txt)
* ffmpeg
* chromedriver
* Google Chrome
