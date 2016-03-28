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
CREATE TABLE clubtypes
-- List of known club types with marker types
(
  name TEXT PRIMARY KEY, --What we call the type (e.g. "club" or "individual")
  iconUrl TEXT, --What icon picture to use for this type of club
  description TEXT --What does this type include
)
''')
con.execute('''
CREATE TABLE clubstatuses
-- List of known club statuses with marker types
(
  name TEXT PRIMARY KEY, --What we call the status (e.g. "active")
  iconClass TEXT, --What marker shape to use for this status
  description TEXT --What does this status mean?
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
  clubtype TEXT, --Type of club: is it a single player or a fixed club? foreign key
  clubstatus TEXT, --Club status: active or inactive? foreign key
  FOREIGN KEY(clubstatus) REFERENCES clubstatuses(name), --Type of club: is it a single player or a fixed club?
  FOREIGN KEY(clubtype) REFERENCES clubtypes(name), --Type of club: is it a single player or a fixed club?
  FOREIGN KEY(layer) REFERENCES layers(name) --Which layer is it on?
)
''')
con.execute("INSERT INTO layers (name, description, color) VALUES ('DE',?,?)", (u'Deutsche Go-Bund', 'Yellow'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('ES',?,?)", (u'http://aego.biz', 'Gold'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('FR',?,?)", (u'http://ffg.jeudego.org/', 'Blue'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('NL',?,?)", (u'Nederlandse Go-Bond: https://gobond.nl/verenigingen', 'Orange'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('UK',?,?)", (u'British Go Association: http://www.britgo.org/clubs/list', 'Red'))
con.execute("INSERT INTO layers (name, description, color) VALUES ('ZA',?,?)", (u'South African Go Association: http://www.sagoclubs.co.za/', 'DarkGreen'))
con.execute("INSERT INTO clubstatuses (name, description) VALUES ('active','Currently active club')")
con.execute("INSERT INTO clubstatuses (name, iconClass, description) VALUES ('inactive','Ball','Inactive club')")
con.execute("INSERT INTO clubtypes (name, iconUrl, description) VALUES ('individual','/uploads/pictogram/pitch-24.png','Individual offering games')")
con.execute("INSERT INTO clubtypes (name, description) VALUES ('club','Regular club meeting')")
con.commit()
