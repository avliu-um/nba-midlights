import subprocess


def is_url(link):
    return link.startswith('https://')


def get_clock_seconds(s):
    arr = s.split(':')
    minutes = int(arr[0])
    seconds = int(arr[1])
    return minutes * 60 + seconds


def get_score_tuple(s):
    arr = s.strip().split('-')
    return (int(arr[0].strip()), int(arr[1].strip()))


def stitch_clips(concat_file='./temp/concat.txt', outputfile='./output.mp4'):
    # Could implement this with ffmpeg-python if I get a chance to learn it in-depth
    print(f'stitching clips listed in {concat_file} into {outputfile}')
    subprocess.run(f'ffmpeg -f concat -i {concat_file} -c copy {outputfile}', shell=True)


if __name__=='__main__':
    print(get_score_tuple(' 10 - 15'))