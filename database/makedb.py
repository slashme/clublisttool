#!/usr/bin/python

import sqlite3
con = sqlite3.connect('clubs.db')
con.execute('''
CREATE TABLE layers
-- A list of layers in the map. Normally countries.
(
  name TEXT PRIMARY KEY, --The name of the layer. 
  description TEXT, --Description of the layer
  color, TEXT --Color of the marker
)
''')
con.execute('''
CREATE TABLE clubs
-- A list of all the go clubs in the world
(
  clubid INTEGER PRIMARY KEY, --Need a separate key; name might be duplicate.
  name TEXT NOT NULL, --A uniquely defining name for the club
  layer TEXT, --Which layer is it on? Foreign key.
  lat REAL NOT NULL, --Decimal latitude
  lon REAL NOT NULL, --Decimal longitute
  website TEXT, --Website of the club, if any
  meetplace TEXT, --Meeting place of the club (as text address)
  meettime TEXT, --Meeting times of the club (as text for now)
  contact TEXT, --Contact details (Chuck all into one text field for now)
  FOREIGN KEY(layer) REFERENCES layers(name) --Which layer is it on?
)
''')
