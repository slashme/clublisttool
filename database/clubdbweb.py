import sqlite3, os, errno, datetime, re, urllib
from bottle import Bottle, route, get, post, request, run, template, debug, error, static_file

app = Bottle()

#Define regular expressions
hasnum = re.compile('\d+') #running hasnum.findall returns a list of all the digit sequences in a string, length 0 if none found.

def showclub(clubid):
  '''
  Displays a table with the information of the selected club,
  with links to set club parameters.
  '''
  conn = sqlite3.connect('clubs.db')
  c = conn.cursor()
  c.execute('''
  SELECT
    clubs.name, 
    clubs.layer,
    clubs.lat,
    clubs.lon,
    clubs.website,
    clubs.meetplace,
    clubs.meettime,
    clubs.clubstatus,
    clubs.clubtype
  FROM 
    clubs
  WHERE clubs.clubid = ?
  ''', (clubid,))
  result = c.fetchall()
  #Get all the layers as a list
  c.execute('''
  SELECT
    layers.name, 
    layers.description
  FROM 
    layers
  ''')
  layerlist = c.fetchall()
  #Get all the statuses as a list
  c.execute('''
  SELECT
    name, description
  FROM 
    clubstatuses
  ''')
  statuslist = c.fetchall()
  #Now get all the clubtypes as a list
  c.execute('''
  SELECT
    name, description
  FROM 
    clubtypes
  ''')
  typelist = c.fetchall()
  c.close()
  #return str(layerlist) #DEBUG 
  if len(result)==0:
    output = template('not_found', message='Project %s not found'%clubid, title='No club found')
    return output
  result=result[0] #Only one row, so reduce the typing...
  club_id=str(clubid)
  showclubtable = [[]] #Hack: Include an empty row so that there will be no table header
  showclubtable += [
    ['Club name:',    ['input', 'text', 'club_name', result[0].replace('"', '')] ],
    ['Country/group', ['select', result[1], 'layer', layerlist] ],
    ['Latitude',      result[2]                              ],
    ['Longitute',     result[3]                              ],
    ['Website',       result[4]                              ],
    ['Meeting place', result[5]                              ],
    ['Meeting time',  result[6]                              ],
    ['Club status',   result[7]                              ],
    ['Club type',     result[8]                              ]
  ]
  #return str(showclubtable) #DEBUG 
  output = template('make_table', rows=showclubtable, title='Club %s'%result[0])
  return output

@app.post('/club/<clubid:int>/update/<param>') 
def do_mod_param(clubid, param):
  '''
  Modify single parameter of club based on user form input.
  "param" should have the form "table.field".
  '''
  returnvalue=request.forms.getunicode('returnvalue')
  return template('not_found', message=returnvalue, title="Not yet implemented") 

@app.route('/list') #List clubs
def list():
  conn = sqlite3.connect('clubs.db')
  c = conn.cursor()
  c.execute('''
  SELECT
    clubid, name, clubstatus, layer
  FROM 
    clubs 
  ''')
  result = c.fetchall()
  c.close()
  showclubtable = [['Club name', 'Status', 'Country']]
  for row in result:
    showclubtable += [[['/club/'+str(row[0]),row[1]],row[2],row[3]]]
  output = template('make_table', rows=showclubtable, title="Club list")
  return output

@app.get('/makeclub') #Create a new club: get action
def makeclub():
  '''
  Create form to list a new club.
  '''
  #Get the list of allowed clubtypes to insert into the template.
  conn = sqlite3.connect('clubs.db')
  c = conn.cursor()
  c.execute("SELECT clubtypeid, name FROM clubtypes")
  clubtypelist = c.fetchall()
  c.execute("SELECT name FROM engines")
  enginelist = c.fetchall()
  c.close()
  clubform = template('club_form', enginelist=enginelist, clubtypelist=clubtypelist, title="Enter new club") #Generate a form with pre-populated option lists.
  return clubform

@app.post('/makeclub') #Create a new club: post action
def do_makeclub():
  '''
  Create a new club list entry based on user input form.
  '''
  pn=request.forms.getunicode('club_name')
  ft=request.forms.getunicode('ft')
  en=request.forms.getunicode('en')
  maj_ver=request.forms.getunicode('maj_ver')
  min_ver=request.forms.getunicode('min_ver')
  ver_suf=request.forms.getunicode('ver_suf')
  fr1=request.forms.getunicode('fr1')
  frn=request.forms.getunicode('frn')
  conn = sqlite3.connect('clubs.db')
  c = conn.cursor()
  c.execute('''
  INSERT INTO clubs(name, majorversion, minorversion, versionsuffix, clubstatus, clubtype, firstframe, lastframe, engine)
  VALUES 
    (?, ?, ?, ?, ?, ?, ?, ?, ?)
  ''', (pn, maj_ver, min_ver, ver_suf, 'stopped', ft, fr1, frn, en))
  new_club_id = c.lastrowid
  conn.commit()
  c.close()
  return showclub(new_club_id)

@app.route('/club/<clubid:int>') 
def showclubbynum(clubid):
  '''
  Return the club by number - showclub will redirect if not valid ID.
  '''
  return showclub(clubid)

@app.error(404)
def error404(error):
    '''
    When we don't have a path for a given request, return to the club list.
    '''
    return list()

debug(True)
run(app, host='localhost', port=8080, reloader=True)
