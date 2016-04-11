from gluon import DAL, Field

db = DAL('sqlite://clubsnew.db')

#Define layers table: A list of layers in the map. Normally countries.
db.define_table(
    'layer',
    Field('layercode'),   #Layer code: typically country 2-letter code
    Field('description'), #Description of the layer, e.g. name of the org.
    Field('color'),       #Color of the marker as HTML color
    format = '%(name)s'

#Define club types table: A list of club types with marker types
db.define_table(
    'clubtype',
    Field('name'),        #What we call the type (e.g. "club" or "individual")
    Field('iconURL'),     #What icon picture to use for this type of club
    Field('description'), #What does this club type mean?
    format = '%(name)s'

#Define club status table: List of known club statuses with marker types
db.define_table(
    'clubstatus',
    Field('name'),        #What we call the status (e.g. "active")
    Field('iconClass'),   #What marker shape to use for this status
    Field('description'), #What does this status mean?
    format = '%(name)s'

#Define clubs table: List of all the clubs
db.define_table(
    'club',
    Field('name'),                        #A uniquely defining name for the club
    Field('layer_id',db.layer),           #Which layer is it on? Foreign key.
    Field('lat', 'decimal'),              #Decimal latitude
    Field('lon', 'decimal'),              #Decimal longitute
    Field('website'),                     #Website of the club, if any
    Field('meetplace'),                   #Meeting place of the club (as text address)
    Field('meettime'),                    #Meeting times of the club (as text for now)
    Field('contact'),                     #Contact details (Chuck all into one text field for now)
    Field('clubtype_id',db.clubtype),     #Type of club: is it a single player or a fixed club? foreign key
    Field('clubstatus_id',db.clubstatus), #Club status: active or inactive? foreign key
    format = '%(name)s'

db.layer.layercode.requires = IS_NOT_EMPTY()
db.club.lat.requires = IS_NOT_EMPTY()
db.club.lon.requires = IS_NOT_EMPTY()
