from gluon import DAL, Field

db = DAL('sqlite://clubsnew.db')

def create_layer():
    # create an insert form from the table
    form = SQLFORM(db.layer).process()

    # if form correct perform the insert
    if form.accepted:
        response.flash = 'new record inserted'

    # and get a list of all persons
    records = SQLTABLE(db().select(db.layer.ALL),headers='fieldname:capitalize')

    return dict(form=form, records=records)
