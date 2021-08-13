#! /usr/bin/python3

# pip3 install pygithub
# pip3 install feedgen

from dateutil import parser
from feedgen.feed import FeedGenerator
import github
import sqlite3

n_items = 25
db = '/root/nurdspace/github-announcer.db'
file_out = '/var/www/htdocs.keetweej.vanheusden.com/ns-gh-rss.xml'
github_auth_token = ' something sensible here '

fg = FeedGenerator()
fg.title('NURDSpace affiliates github-repo thing')
fg.description('See title')
fg.link(href='https://github.com/NURDspace/github-announcer')

g = github.Github(github_auth_token)

dbcon = sqlite3.connect(db)
dbcur = dbcon.cursor()

dbcur.execute('SELECT DISTINCT user, last_check FROM users')

to_announce = set()
users_update = set()

for record in dbcur:
    user = g.get_user(record[0])
    print(record[0])

    latest = None

    for event in user.get_events():
        event_epoch = event.created_at.timestamp()

        if latest == None:
            latest = int(event_epoch)
            users_update.add((latest, record[0]))
            print('\t', event.created_at, latest, record[0])

        if event_epoch < record[1]:
            break

        if event.type == 'CreateEvent':
            add = (event.repo.name, event.payload['description'])
            print(f'\t{add}')

            to_announce.add(add)

            if len(to_announce) >= n_items:
                break

    if len(to_announce) >= n_items:
        break

try:
    for a in to_announce:
        fe = fg.add_entry()
        fe.title(f'{a[0]}: {a[1]}')
        fe.description(f'{a[0]}: {a[1]}')
        fe.link(href='https://www.github.com/%s' % a[0])

    fg.rss_file(file_out)

    dbcur = dbcon.cursor()

    for u in users_update:
        dbcur.execute('UPDATE users SET last_check="%d" WHERE user="%s"' % (u[0], u[1]))

    dbcon.commit()

except Exception as e:
    print(f'Failed: {e}')
