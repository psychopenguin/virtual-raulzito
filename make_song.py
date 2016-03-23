from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

import json
import yaml
import markovify
import random
import logging
from glob import glob

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
SONGFILES = glob('*.json')

with open('config.yaml') as config_file:
    config = yaml.safe_load(config_file.read())

WP_ENDPOINT = config['wordpress']['endpoint']
WP_USER = config['wordpress']['user']
WP_PASSWORD = config['wordpress']['password']

random.shuffle(SONGFILES)
songfile = random.choice(SONGFILES)

logging.info('Using {} as seed'.format(songfile))
with open(songfile) as f:
    songbase = json.loads(f.read())

lyrics = [m['lyric'] for m in songbase if m['lyric'] is not None]
titles = [m['title'] for m in songbase if m['title'] is not None]
lenghts = [len(m.split('\n')) for m in lyrics if m is not None]


num_verses = random.choice(range(min(lenghts), max(lenghts) + 1))
lyrics_model = markovify.text.NewlineText('\n'.join(lyrics), state_size=3)
titles_model = markovify.text.NewlineText('\n'.join(titles))

post = WordPressPost()
logging.info('Generating content with {} sentences'.format(num_verses))
content = [lyrics_model.make_sentence(tries=100) for x in range(num_verses)]
post.content = '\n'.join([s for s in content if s is not None])
post.post_status = 'publish'
logging.info('Generating title')
post.title = titles_model.make_sentence(tries=100)
if post.title is None:
    logging.info("Can't generate title, using a random sentence")
    post.title = random.choice(content)


wp = Client(WP_ENDPOINT, WP_USER, WP_PASSWORD)
logging.info('Posting to wordpress as {}'.format(post.title))
wp.call(NewPost(post))
logging.info('Finished')
