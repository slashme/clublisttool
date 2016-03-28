import sqlite3, os, errno, datetime, re
from bottle import Bottle, route, get, post, request, run, template, debug, error, static_file

app = Bottle()

#Define regular expressions
hasnum = re.compile('\d+') #running hasnum.findall returns a list of all the digit sequences in a string, length 0 if none found.

def showproj(wishid):
  '''
  Displays a table with the information of the selected project,
  with links to set project parameters and upload project files.
  '''
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute('''
  SELECT
    wishes.name AS wish_name, 
    projectstatus.status AS proj_status,
    frametypes.name AS frametype_name,
    wishes.engine,
    blendfiles.uploadtime,
    blendfiles.filename,
    wishes.firstframe,
    wishes.lastframe
  FROM 
    wishes
    LEFT JOIN projectstatus ON wishes.status    = projectstatus.status
    LEFT JOIN frametypes    ON wishes.frametype = frametypes.frametypeid
    LEFT JOIN blendfiles    ON wishes.wishid    = blendfiles.wishid
    WHERE wishes.wishid = ?
  ''', (wishid,))
  result = c.fetchall()
  c.close()
  if len(result)==0:
    output = template('not_found', message='Project %s not found'%wishid, title='Unwished')
    return output
  result=result[0] #Only one row, so reduce the typing...
  wish_id=str(wishid)
  wish_name=result[0]
  proj_status=result[1]
  frametype_name=result[2]
  engine_name=result[3]
  try:
    uploadtime=result[4].split('.')[0] #If this is a timestamp, remove the fractions of seconds
  except AttributeError:
    uploadtime="" #Else there is no upload time.
  showprojtable = [[]] #Hack: Include an empty row so that there will be no table header
  showprojtable += [['Wish name:',['/wish/'+wish_id+'/update/wishes.name',wish_name]],['Status:',proj_status],['Frame type:',frametype_name],['Engine:',engine_name]]
  if not result[5]:
    showprojtable += [['No Blender file:',['/wish/'+wish_id+'/projupload','Upload .blend file']]]
  else:
    showprojtable += [['Blend file:',['/projects/'+wish_id+'/'+result[5],result[5]+', Uploaded at '+uploadtime]]]
    showprojtable += [['',['/wish/'+wish_id+'/projupload','Upload new .blend file']]]
  output = template('make_table', rows=showprojtable, title='Project %s'%result[0])
  return output
  #TODO:
  #Use mod_param template to allow project parameters to be modified.
  #Create method to update parameters.

#In progress: Creating form to modify single project parameter
#TODO: make this work for more than just list parameters.
@app.get('/wish/<wishid:int>/update/<param>') 
def mod_param(wishid, param):
  '''
  Create form to modify single parameter of project.
  "param" should have the form "table.field".
  '''
  #Extract the table, field and value from the parameter field.
  mp_tf=param.split('.') #mp_tf is mod_param table/field
  #Check if the wish ID is valid
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute("SELECT wishid, name FROM wishes WHERE wishid = ?", (wishid,))
  wishidlist = c.fetchall() #This should have length 1
  c.close()
  if len(wishidlist)==0:
    return template('not_found', message='Project %s not found'%wishid, title="Unwished")
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
    #titletext="change single parameter for project"
    titletext=str(foreign_relation)
    editaction="/wish/" + str(wishid) + "/update/" +str(param) #set form action variable
    editform = template('mod_param', edit_value=editvalue, edit_desc=editdesc, edit_action=editaction, edit_type=edittype, title=titletext, projname=wishidlist[0][1], info="info") #Generate parameter modification form
    return editform
  c = conn.cursor()
  #Again, can't parameterize table name, but we are again safe here.
  c.execute("PRAGMA table_info("+mp_tf[0]+")") 
  result = c.fetchall()
  c.close()
  vartype= [v for i, v in enumerate(result) if v[1] == mp_tf[1]][0][2]
  if vartype=="TEXT":
    edittype=vartype
    titletext="change text parameter for project"
  if vartype=="INTEGER":
    edittype='number'
    titletext="change integer parameter for project"
  c = conn.cursor()
  #Again, can't parameterize table name, but we are again safe here.
  c.execute("SELECT "+mp_tf[1]+" FROM "+mp_tf[0]+" WHERE wishid = " + str(wishid))
  result = c.fetchall()
  c.close()
  editvalue=result[0][0]
  editdesc=mp_tf[1]
  editaction="/wish/" + str(wishid) + "/update/" +str(param) #set form action variable
  editform = template('mod_param', edit_value=editvalue, edit_desc=editdesc, edit_action=editaction, edit_type=edittype, title=titletext, projname=wishidlist[0][1], info="info") #Generate parameter modification form
  return editform
  return template('not_found', message=str(vartype), title="Not yet implemented") 
  return template('not_found', message=str(mp_tf[0]), title="Not yet implemented") 

@app.post('/wish/<wishid:int>/update/<param>') 
def do_mod_param(wishid, param):
  '''
  Modify single parameter of project based on user form input.
  "param" should have the form "table.field".
  '''
  returnvalue=request.forms.getunicode('returnvalue')
  return template('not_found', message=returnvalue, title="Not yet implemented") 

@app.route('/list') #List projects
def list():
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute('''
  SELECT
    wishid, name, status
  FROM 
    wishes 
  ''')
  result = c.fetchall()
  c.close()
  showprojtable = [['Project name', 'Status']]
  for row in result:
    showprojtable += [[['/wish/'+str(row[0]),row[1]],row[2]]]
  output = template('make_table', rows=showprojtable, title="Wish list")
  return output

@app.get('/wish/<wishid:int>/tnupload') 
def tnupload(wishid):
  '''
  Create form to upload thumbnail images for project,
  to allow verification of rendered frames.
  '''
  #Check if the wish ID is valid
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute("SELECT wishid, name FROM wishes WHERE wishid = ?", (wishid,))
  wishidlist = c.fetchall() #This should have length 1
  c.close()
  if len(wishidlist)==0:
    return template('not_found', message='Project %s not found'%wishid, title="Unwished")
  #No need for an else clause: returned.
  #TODO: Check whether we have thumbnails already, warn if so.
  titletext = "Upload thumbnails for project" + wishidlist[0][1]
  uploadaction="/wish/" + str(wishid) + "/tnupload" #set form action variable
  wishform = template('multi_upload', uploadaction=uploadaction, title=titletext, info="Select thumbnails named [frame number].png") #Generate multiple file upload form
  return wishform

@app.post('/wish/<wishid:int>/tnupload') #Upload a blender project file : post action
def do_tnupload(wishid):
  '''
  Upload thumbnail images supplied by user
  to allow verification of rendered frames.
  Register thumbnails in database.
  '''
  #If we don't yet have a directory for the project, create it:
  projpath = os.path.dirname(__file__) + "projects/" + str(wishid) + "/"
  try:
    os.mkdir(projpath)
  except OSError as exc:
    if exc.errno != errno.EEXIST:
      raise #TODO: Do I need to handle this more gracefully?
  for thumbnail in request.files.getlist('upload[]'): #For each file to be uploaded...
    tnfilenamelist=hasnum.findall(thumbnail.filename) #List of all numbers in filename
    if len(tnfilenamelist) == 0: #the filename doesn't contain a number
      error_text="File name " + thumbnail.filename + " doesn't contain a number"
      return template('not_found', message=error_text, title="Filename error")
    tnframenum = int(hasnum.findall(thumbnail.filename)[0]) #First number in filename should be frame number.
    conn = sqlite3.connect('wishes.db')
    c = conn.cursor()
    c.execute('''
    SELECT frametypes.ext AS frametype_ext FROM 
    wishes LEFT JOIN frametypes ON wishes.frametype = frametypes.frametypeid
    WHERE wishes.wishid = ?
    ''', (wishid,))
    tnfilenameext = c.fetchall()[0]
    tnfilename="tn_"+str(wishid)+"_"+str(tnframenum)+"."+tnfilenameext[0]
    thumbnail.save(destination=projpath + tnfilename, overwrite=True) #TODO: Check for proper filename and extension
    #Update the frames list: if the frame already exists, the UPDATE command will run,
    #otherwise the INSERT command will run.
    c.execute('''
    UPDATE OR IGNORE frames
      SET status=2, draftfilename=?
      WHERE wishid=? AND framenumber=?
    ''', (tnfilename, wishid, tnframenum))
    c.execute('''
    INSERT OR IGNORE INTO frames (status, wishid, framenumber, draftfilename)
    VALUES ('draft', ?, ?, ?)
    ''', (wishid, tnframenum, tnfilename))
    #Note, we set frame status to "draft".  TODO: How will this work if the current status is "running"?
    conn.commit()
    c.close()
    #TODO: check file type: if not the right image type or dimensions, kill it with fire.
  return list() #Just return something for now...

@app.get('/wish/<wishid:int>/projupload') 
def projupload(wishid):
  '''
  Create form to upload the file for the given project.
  If one already exists, make this clear to the user.
  '''
  #Check if the wish ID is valid
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute("SELECT wishid, name FROM wishes WHERE wishid = ?", (wishid,))
  wishidlist = c.fetchall() #This should have length 1
  if len(wishidlist)==0:
    return template('not_found', message='Project %s not found'%wishid, title="Unwished")
  #Get the upload time of the blend file. This will have length 1 if we're asked to overwrite a file, otherwise 0
  c.execute("SELECT uploadtime FROM blendfiles WHERE wishid = ?", (wishid,))
  uploadtimelist = c.fetchall()
  c.close()
  #Generate title text explaining to the user whether this will upload an existing file or create a new one.
  if len(uploadtimelist)==1:
    titletext = "Upload over blend file uploaded on " + uploadtimelist[0][0] + " for project " + wishidlist[0][1]
  else:
    #return template('not_found', message=str(wishidlist), title="Debugging") #Debug: testing
    titletext = "Upload blend file for project " + wishidlist[0][1]
  uploadaction="/wish/" + str(wishid) + "/projupload" #set form action variable
  wishform = template('single_upload', uploadaction=uploadaction, title=titletext) #Generate a file upload form
  return wishform

@app.post('/wish/<wishid:int>/projupload') #Upload a blender project file : post action
def do_projupload(wishid):
  '''
  Upload the Blender file for the given project, and register it in the
  database.
  '''
  upload=request.files.get('upload')
  #If we don't yet have a directory for the project, create it:
  projpath = os.path.dirname(__file__) + "projects/" + str(wishid) + "/"
  try:
    os.mkdir(projpath)
  except OSError as exc:
    if exc.errno != errno.EEXIST:
      raise #Do I need to handle this more gracefully?
  upload.save(destination=projpath + str(wishid) + ".blend", overwrite=True) #Maybe warn?
  #TODO: check file type: if not Blender file, kill it with fire.
  savetime=datetime.datetime.utcnow()
  #Now update the database:
  #Find out whether the file already is listed.
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute("SELECT blendfileid FROM blendfiles WHERE wishid = ?", (wishid,))
  blendfileidlist = c.fetchall()
  c.close()
  #If file is listed, just update the upload time
  if len(blendfileidlist)==1:
    conn = sqlite3.connect('wishes.db')
    c = conn.cursor()
    c.execute("UPDATE blendfiles SET uploadtime= ? WHERE wishid = ?", (savetime.isoformat(' '), wishid))
    conn.commit()
    c.close()
  else:
    #If the file is not listed, insert into blendfiles table.
    conn = sqlite3.connect('wishes.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO blendfiles(wishid, filename, uploadtime)
    VALUES 
      (?, ?, ?)
    ''', (wishid, str(wishid) + ".blend", savetime.isoformat(' ')))
    conn.commit()
    c.close()
  return list() #Just return something for now...

@app.get('/makewish') #Create a new project: get action
def makewish():
  '''
  Create form to start a new project.
  '''
  #Get the list of allowed frametypes to insert into the template.
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute("SELECT frametypeid, name FROM frametypes")
  frametypelist = c.fetchall()
  c.execute("SELECT name FROM engines")
  enginelist = c.fetchall()
  c.close()
  wishform = template('wish_form', enginelist=enginelist, frametypelist=frametypelist, title="Make a Blender wish") #Generate a form with pre-populated option lists.
  return wishform

@app.post('/makewish') #Create a new project: post action
def do_makewish():
  '''
  Create a new project based on user input form.
  '''
  pn=request.forms.getunicode('wish_name')
  ft=request.forms.getunicode('ft')
  en=request.forms.getunicode('en')
  maj_ver=request.forms.getunicode('maj_ver')
  min_ver=request.forms.getunicode('min_ver')
  ver_suf=request.forms.getunicode('ver_suf')
  fr1=request.forms.getunicode('fr1')
  frn=request.forms.getunicode('frn')
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute('''
  INSERT INTO wishes(name, majorversion, minorversion, versionsuffix, status, frametype, firstframe, lastframe, engine)
  VALUES 
    (?, ?, ?, ?, ?, ?, ?, ?, ?)
  ''', (pn, maj_ver, min_ver, ver_suf, 'stopped', ft, fr1, frn, en))
  new_wish_id = c.lastrowid
  conn.commit()
  c.close()
  return showproj(new_wish_id)

@app.route('/wish/<wishid:int>') 
def showprojbynum(wishid):
  '''
  Return the project by number - showproj will redirect if not valid ID.
  '''
  return showproj(wishid)

@app.route('/wish/<wishname>') 
def showprojbyname(wishname):
  '''
  If valid project name, find the number and run showproj, else redirect.
  '''
  conn = sqlite3.connect('wishes.db')
  c = conn.cursor()
  c.execute("SELECT wishid FROM wishes WHERE name = ?", (wishname,))
  result=c.fetchall()
  if len(result)==0:
    return template('not_found', message='Project %s not found'%wishname, title="Unwished")
  else:
    #Just use the first matching name.  TODO: Handle duplicates?
    return showproj(result[0][0])

@app.route('/projects/<filepath:path>')
def server_static(filepath):
  '''
  Serve static project file by name.
  '''
  #TODO: serve with proper mime type; enforce download?
  return static_file(filepath, root=os.path.dirname(os.path.abspath(__file__))+'/projects/') 

@app.error(404)
def error404(error):
    '''
    When we don't have a path for a given request, return to the project list.
    '''
    return list()

debug(True)
run(app, host='localhost', port=8080, reloader=True)
