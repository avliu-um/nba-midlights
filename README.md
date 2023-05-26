# nba-midlights

The inspiration from this project comes from my experience and current problems with media consumption options as a serious NBA fan. Like most people, I cannot watch entire games often because I'm busy with work, school, etc. Instead, I rely on clipped versions of the game, called highlight videos. 

However, the issue with highlight videos is that they only show made baskets. Times where players score. To the casual NBA fan, that's maybe what they want to see. For me though, such a summarization of an NBA game is too narrow. 

First, highlight videos systematically biases towards volume scoring, which led me to associate those that routinely showed up in highlights with great players. For instance, Jordan Poole, a highlight-driven player who in reality routinely demonstrates poor shot selection, is seen in a positively-biased light. Players who often make mistakes that aren't captured in highlights, such as turnovers, fouls, and bad shot selection, do not get their fair shake. Second, highlight videos limit us from seeing parts of the game that are equally as beautiful as buckets, such as great defensive schemes and individual defensive performances.

Enter, NBA Midlights, a web-scraping and video-stiching project that creates more realistic, natural, and consistent video reals of NBA games.

Currently, we implement random sampling of clips from NBA.com and generate videos based on that. Our goal is to create videos that more accurately represent players. For instance, if a player shoots 30% from the field, then only 30% of their clips in the Midlights video will be makes. Similarly for Assist-Turnover ratio.

This repo contains the code for NBA mid-lights. See [here](https://docs.google.com/document/d/1O63A0ZqUo_-5Kp7YrVpc6f_02PndsTvvwCEJmmM7Ark/edit) for notes doc.

See [here](https://drive.google.com/file/d/1lHONnpNAqYj44xjszP7DJzvCYiRcicfQ/view?usp=sharing) for example Midlight video (Knicks vs. Cavaliers, 4/23/2023), generated automatically by the below scripts.

Included files:
* scrape_plays.py- uses BeautifulSoup and Selenium to sample clips of plays from a given game on NBA.com
* create_videos.py- uses ffmpeg to stitch videos automatically, and output to mp4
