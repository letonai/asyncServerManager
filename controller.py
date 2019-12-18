#!/usr/bin/python
# -*- coding: utf-8 -*-
import web
import os
import sqlite3
from register import agentRegister
from filetransfer import fileList
from filetransfer import fileDownload
from filetransfer import fileUpload
from filetransfer import fileDownloadFromServer
#from filetransfer import remoteFileList
from filetransfer import remoteDirList
from remoteaction import remoteAction
from remoteaction import remoteActionStatus
from remoteaction import remoteActionList
from remoteaction import remoteActionRegister
import datamodel
from status import status
#from cheroot.server import HTTPServer
#from cheroot.ssl.builtin import BuiltinSSLAdapter
from web.wsgiserver import CherryPyWSGIServer
from errorPage import errorPage

#Disable/Enable debug messages
#web.config.debug = False

CWD = os.path.dirname(os.path.abspath(__file__))+"/static"
DBFILE=".controller.dat"
DB=web.database(dbn="sqlite",db=DBFILE)

os.environ["PORT"] = "8081"        
urls = (
    "/agentregister(.*)", agentRegister,
    "/agentcheckegister(.*)", agentRegister,
    "/agents(.*)",agentRegister,
    "/getfilelist(.*)", fileList,
    "/filedownload(.*)", fileDownload,
    "/addfile(.*)", fileUpload,
    "/getfromserver(.*)", fileDownloadFromServer,
    "/getremotequeuedactions(.*)", status,
    #"/getremotefilelist(.*)", remoteFileList,
    "/getremotedirlist(.*)", remoteDirList,
    "/setremoteaction(.*)", remoteAction,
    "/getremoteactionlist(.*)", remoteActionList,
    "/getremoteactionstatus(.*)", remoteActionStatus,
    "/registerremoteaction(.*)", remoteActionRegister,
    "/(.*)", errorPage

)

app = web.application(urls, globals())

CONN=None



    

def firstRun():
    print "No previous configuration detected!"
    DB.query("create table %s (ID integer primary key autoincrement,SERVERNAME text,IP text)" % (datamodel.TABLEAGENTS))
    DB.query("create table %s (USERID text,PERMISSIONS blob )" % (datamodel.TABLEUSERS))
    DB.query("create table %s (FILEID text ,FILENAME text ,SERVERTARGET text, APPLICATIONTARGET text,HASH text,DOWNLOADED text )" % datamodel.TABLEFILES)
    DB.query("create table %s (FILEID text ,FILENAME text ,SOURCESERVER text, APPLICATIONTARGET text,HASH text,DOWNLOADED text )" % datamodel.TABLEREMOTEFILES)
    DB.query("create table %s (ID integer primary key autoincrement,REQUESTDATE date, ACTION text ,PARAMETERS text,SOURCESERVER text, APPLICATIONTARGET text ,RESULT text ,DATE text )" % datamodel.TABLEREMOTEACTIONS)
    DB.query("create table %s (ID integer primary key autoincrement, SOURCESERVER text ,DIR text, APPLICATION text)" % datamodel.TABLEREMOTEDIR)
    DB.query("create table %s (ID integer primary key autoincrement, SOURCESERVER text ,ACTION text, APPLICATION text)" % datamodel.TABLEAVALIABLEACTIONS)

#from cheroot.server import HTTPServer
#from cheroot.ssl.builtin import BuiltinSSLAdapter

#HTTPServer.ssl_adapter = BuiltinSSLAdapter(
#        certificate='cert/server.crt', 
#		private_key='cert/domain.key')

CherryPyWSGIServer.ssl_certificate = "cert/server.crt"
CherryPyWSGIServer.ssl_private_key = "cert/domain.key"

if __name__ == "__main__":
    if not os.path.exists( DBFILE ):
    	firstRun()
    app.run()

