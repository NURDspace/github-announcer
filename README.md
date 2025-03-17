# github-announcer
Announces new member repositories in an RSS-feed-file

# database:
create table users(user varchar(256), last_check int not null, primary key(user));

# token
You need an api-token for github.
See https://github.com/settings/tokens
