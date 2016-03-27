#!/usr/bin/python

#Script to load geojson club data into database

import json, sys, sqlite3

#Load the file given as an argument on the command line
infile=open(sys.argv[1],'r')

#Parse it as json data
clubdata=json.load(infile)

#Open database connection
con = sqlite3.connect('test.db')

#FIXME: finish this
for club in clubdata['features']:
  con.execute("INSERT INTO clubs (name, foo) VALUES (blah, foo)")

con.commit()
