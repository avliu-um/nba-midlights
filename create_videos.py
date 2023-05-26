import shutil
import os
import wget
import subprocess


os.mkdir('./temp')

with open('video_links.txt', 'r') as fp:
    download_links = fp.readlines()
    with open('./temp/concat.txt', 'w') as concat_file:
        for link in download_links:
            link = link.strip()
            filename = wget.download(link, out='./temp')
            concat_file.write('file ' + filename[len('./temp')+1:] + '\n')

# TODO: Could implement this with ffmpeg-python if I get a chance to learn it in-depth
subprocess.run('ffmpeg -f concat -i ./temp/concat.txt -c copy ./output.mp4', shell=True)

shutil.rmtree('./temp')
