#!/usr/bin/python
#Script to create a stub database with a test layer

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
con.execute("INSERT INTO layers (name, description, color) VALUES ('DE',?,?)", (u'Deutsche Go-Bund', 'Yellow'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('ES',?,?)", (u'http://aego.biz', 'Gold'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('FR',?,?)", (u'http://ffg.jeudego.org/', 'Blue'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('NL',?,?)", (u'Nederlandse Go-Bond: https://gobond.nl/verenigingen', 'Orange'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('UK',?,?)", (u'British Go Association: http://www.britgo.org/clubs/list', 'Red'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('ZA',?,?)", (u'South African Go Association: http://www.sagoclubs.co.za/', 'DarkGreen'))
con.commit()
