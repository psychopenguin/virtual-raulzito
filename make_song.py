from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

import json
import yaml
import markovify
import random
from glob import glob

SONGFILES = glob('*.json')

with open('config.yaml') as config_file:
    config = yaml.safe_load(config_file.read())

WP_ENDPOINT = config['wordpress']['endpoint']
WP_USER = config['wordpress']['user']
WP_PASSWORD = config['wordpress']['password']

songfile = random.choice(SONGFILES)

print('Using {} as seed'.format(songfile))
with open(songfile) as f:
    songbase = json.loads(f.read())

lyrics = [m['lyric'] for m in songbase if m['lyric'] is not None]
titles = [m['title'] for m in songbase if m['title'] is not None]
lenghts = [len(m.split('\n')) for m in lyrics if m is not None]


num_verses = random.choice(range(min(lenghts), max(lenghts) + 1))
title_len = random.choice(range(10, 50))
lyrics_model = markovify.text.NewlineText('\n'.join(lyrics))
titles_model = markovify.text.NewlineText('\n'.join(titles))

post = WordPressPost()
post.title = titles_model.make_short_sentence(title_len, tries=1000)
post.content = '\n'.join([lyrics_model.make_sentence(tries=1000) for x in range(num_verses)])
post.post_status = 'publish'

wp = Client(WP_ENDPOINT, WP_USER, WP_PASSWORD)
wp.call(NewPost(post))
