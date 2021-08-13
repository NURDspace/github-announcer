#! /usr/bin/python3

# pip3 install pygithub
# pip3 install irc

from dateutil import parser
import irc.client
import github
import sqlite3

irc_channel = '#nurdsbofh'
irc_server = 'irc.oftc.net'
irc_nick = 'nurdgitbutt'
db = 'github-announcer.db'
github_auth_token = ' *** hier wat zinnigs invullen *** '

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

            if len(to_announce) >= 3:
                break

    if len(to_announce) >= 3:
        break

def on_connect(connection, event):
    global irc_channel
    connection.join(irc_channel)

def on_join(connection, event):
    global irc_channel
    global dbcon
    global to_announce
    global users_update

    try:
        dbcur = dbcon.cursor()

        for a in to_announce:
            connection.privmsg(irc_channel, f'{a[0]}: {a[1]}')

        for u in users_update:
            dbcur.execute('UPDATE users SET last_check="%d" WHERE user="%s"' % (u[0], u[1]))

        dbcon.commit()

    except Exception as e:
        print(f'Failed: {e}')

    connection.quit('Groeten aan je moeder')

def on_disconnect(connection, event):
    raise SystemExit()

if len(to_announce) > 0:
    reactor = irc.client.Reactor()
    c = reactor.server().connect(irc_server, 6667, irc_nick)
    c.add_global_handler("welcome", on_connect)
    c.add_global_handler("join", on_join)
    c.add_global_handler("disconnect", on_disconnect)
    reactor.process_forever()
