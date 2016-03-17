from time import sleep
import json
from bs4 import BeautifulSoup
import logging

import requests

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

LETRAS_BASE = 'https://www.letras.mus.br/'
with open('artists.txt') as f:
    ARTISTS = f.read().split('\n')

def get_songs_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    songs = soup.find('ul', class_='cnt-list').find_all('a')
    song_list = []
    for song in songs:
        song_list.append({'title': song.text, 'url': song.attrs['href']})
    return song_list


def retrieve_song(html):
    soup = BeautifulSoup(html, 'html.parser')
    lyric = soup.find('div', class_='cnt-letra')
    try:
        paragraphs = lyric.find_all('p')
    except AttributeError:
        return None
    text_list = []
    for p in paragraphs:
        for line in p.contents:
            if str(line) != '<br/>':
                text_list.append(str(line))
    return '\n'.join(text_list)

for artist in ARTISTS:
    logging.info('Retrieving song list for {}'.format(artist))
    songlist = requests.get(LETRAS_BASE + artist + '/')
    songs = get_songs_list(songlist.text)
    for song in songs:
        logging.info("Getting '{}'".format(song['title']))
        req = requests.get(LETRAS_BASE + song['url'])
        song['lyric'] = retrieve_song(req.text)
        sleep(3)
    with open(artist + '.json', 'w') as outpufile:
        outpufile.write(json.dumps(songs))
