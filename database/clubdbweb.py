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
    ['',              ['hidden', '',        'id',        clubid     ] ],
    ['Club name:',    ['input',  'text',    'name',      result[0]  ] ],
    ['Country/group', ['select', result[1], 'layer',     layerlist  ] ],
    ['Latitude',      ['input',  'number',  'lat',       result[2]  ] ],
    ['Longitute',     ['input',  'number',  'lon',       result[3]  ] ],
    ['Website',       ['input',  'text',    'website',   result[4]  ] ],
    ['Meeting place', ['input',  'text',    'meetplace', result[5]  ] ],
    ['Meeting time',  ['input',  'text',    'meettime',  result[6]  ] ],
    ['Club status',   ['select', result[7], 'status',    statuslist ] ],
    ['Club type',     ['select', result[8], 'type',      typelist   ] ]
  ]
  #return str(showclubtable) #DEBUG 
  output = template('make_table', rows=showclubtable, title='Club %s'%result[0])
  return output

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

@app.get('/club/<clubid:int>') 
def showclubbynum(clubid):
  '''
  Return the club by number - showclub will redirect if not valid ID.
  '''
  return showclub(clubid)

@app.post('/updateclub') 
def do_mod_param():
  #FIXME: Hardly any checking going on here...
  '''
  Modify club data based on user form input.
  '''
  clubid=request.forms.getunicode('id')
  clubname=request.forms.getunicode('name')
  clublayer=request.forms.getunicode('layer')
  clublat=request.forms.getunicode('lat')
  clublon=request.forms.getunicode('lon')
  clubwebsite=request.forms.getunicode('website')
  clubmeetplace=request.forms.getunicode('meetplace')
  clubmeettime=request.forms.getunicode('meettime')
  clubstatus=request.forms.getunicode('status')
  clubtype=request.forms.getunicode('type')
  #Database connection
  conn = sqlite3.connect('clubs.db')
  c = conn.cursor()
  c.execute('''
  UPDATE clubs
    SET 
      name = ?,
      layer = ?,
      lat = ?,
      lon = ?,
      website = ?,
      meetplace = ?,
      meettime = ?,
      clubstatus = ?,
      clubtype = ?
  WHERE clubid = ?
  ''', (clubname, clublayer, clublat, clublon, clubwebsite, clubmeetplace, clubmeettime, clubstatus, clubtype, clubid))
  conn.commit()
  return showclub(clubid)

@app.error(404)
def error404(error):
    '''
    When we don't have a path for a given request, return to the club list.
    '''
    return list()

debug(True)
run(app, host='localhost', port=8080, reloader=True)
