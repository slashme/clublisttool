import sqlite3, os, errno, datetime, re
from bottle import Bottle, route, get, post, request, run, template, debug, error, static_file

app = Bottle()

#Define regular expressions
hasnum = re.compile('\d+') #running hasnum.findall returns a list of all the digit sequences in a string, length 0 if none found.

def showclub(clubid):
  '''
  Displays a table with the information of the selected club,
  with links to set club parameters.
  '''
  conn = sqlite3.connect('database/clubs.db')
  c = conn.cursor()
  c.execute('''
  SELECT
    clubs.name AS club_name, 
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
  c.close()
  if len(result)==0:
    output = template('not_found', message='Project %s not found'%clubid, title='No club found')
    return output
  result=result[0] #Only one row, so reduce the typing...
  club_id=str(clubid)
  showclubtable = [[]] #Hack: Include an empty row so that there will be no table header
  showclubtable += [
    ['Club name:', ['/club/'+club_id+'/update/clubs.name',result[0]] ],
    ['Country/group', result[1] ]
    ['Latitude',      result[2] ]
    ['Longitute',     result[3] ]
    ['Website',       result[4] ]
    ['Meeting place', result[5] ]
    ['Meeting time',  result[6] ]
    ['Club status',   result[7] ]
    ['Club type',     result[8] ]
  ]
  output = template('make_table', rows=showclubtable, title='Club %s'%result[0])
  return output

#In progress: Creating form to modify single club parameter
#TODO: make this work for more than just list parameters.
@app.get('/club/<clubid:int>/update/<param>') 
def mod_param(clubid, param):
  '''
  Create form to modify single parameter of club
  "param" should have the form "table.field".
  '''
  #Extract the table, field and value from the parameter field.
  mp_tf=param.split('.') #mp_tf is mod_param table/field
  #Check if the club ID is valid
  conn = sqlite3.connect('clubs.db')
  c = conn.cursor()
  c.execute("SELECT clubid, name FROM clubs WHERE clubid = ?", (clubid,))
  clubidlist = c.fetchall() #This should have length 1
  c.close()
  if len(clubidlist)==0:
    return template('not_found', message='Project %s not found'%clubid, title="No club found")
  #Now check whether the parameter is valid...
  c = conn.cursor()
  c.execute('''
  SELECT
    editable, namefield
  FROM 
    userfields
    WHERE tableid = ?
    AND field = ?
  ''', (mp_tf[0],mp_tf[1]))
  result = c.fetchall()
  c.close()
  if not result[0][0]:
    return template('not_found', message="Cannot change "+mp_tf[1]+" in "+mp_tf[0], title="Not permitted") 
  namefield=result[0][1]
  #Now check whether the parameter is a foreign key:
  c = conn.cursor()
  #Pragma statements cannot be parametrized, but we have already checked that
  #the table exists and the parameter is editable, so this should be OK:
  c.execute("PRAGMA foreign_key_list("+mp_tf[0]+")") 
  result = c.fetchall()
  c.close()
  #This returns a list of all the foreign keys in the given table.
  #Now list all foreign keys that match the requested field:
  foreign_relation = [v for i, v in enumerate(result) if v[3] == mp_tf[1]]
  if foreign_relation: # if it's not an empty list
    #return template('not_found', message=str(foreign_relation), title="Not yet implemented") 
    c = conn.cursor()
    #Again, can't parameterize table name, but we are again safe here.
    if(namefield):
      c.execute("SELECT "+foreign_relation[0][4]+","+namefield+" FROM " + foreign_relation[0][2]) 
    else:
      c.execute("SELECT "+foreign_relation[0][4]+","+foreign_relation[0][4]+" FROM " + foreign_relation[0][2]) 
    result = c.fetchall()
    c.close()
    editvalue=result
    edittype="select"
    editdesc=mp_tf[1]
    #titletext="change single parameter for club"
    titletext=str(foreign_relation)
    editaction="/club/" + str(clubid) + "/update/" +str(param) #set form action variable
    editform = template('mod_param', edit_value=editvalue, edit_desc=editdesc, edit_action=editaction, edit_type=edittype, title=titletext, clubname=clubidlist[0][1], info="info") #Generate parameter modification form
    return editform
  c = conn.cursor()
  #Again, can't parameterize table name, but we are again safe here.
  c.execute("PRAGMA table_info("+mp_tf[0]+")") 
  result = c.fetchall()
  c.close()
  vartype= [v for i, v in enumerate(result) if v[1] == mp_tf[1]][0][2]
  if vartype=="TEXT":
    edittype=vartype
    titletext="change text parameter for club"
  if vartype=="INTEGER":
    edittype='number'
    titletext="change integer parameter for club"
  c = conn.cursor()
  #Again, can't parameterize table name, but we are again safe here.
  c.execute("SELECT "+mp_tf[1]+" FROM "+mp_tf[0]+" WHERE clubid = " + str(clubid))
  result = c.fetchall()
  c.close()
  editvalue=result[0][0]
  editdesc=mp_tf[1]
  editaction="/club/" + str(clubid) + "/update/" +str(param) #set form action variable
  editform = template('mod_param', edit_value=editvalue, edit_desc=editdesc, edit_action=editaction, edit_type=edittype, title=titletext, clubname=clubidlist[0][1], info="info") #Generate parameter modification form
  return editform
  return template('not_found', message=str(vartype), title="Not yet implemented") 
  return template('not_found', message=str(mp_tf[0]), title="Not yet implemented") 

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
