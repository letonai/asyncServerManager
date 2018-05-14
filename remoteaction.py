#!/usr/bin/python3.7
# -*- coding: utf-8 -*-

import web
import os
import socket
import json
from hash import HASH
import copy 
import time
import base64
import pdb
import datamodel
import time 

CWD = os.path.dirname(os.path.abspath(__file__))+"/"
DBFILE=".controller.dat"
DB=web.database(dbn="sqlite",db=DBFILE)
#ABLEFILES="files"
#TABLEREMOTEFILES="remotefiles"
#TABLEREMOTEACTIONS="remoteactions"

class remoteAction:
	
	def GET(self,uri):
		web.header('Content-Type','application/json')
		web.header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
		web.header('Cache-Control','post-check=0, pre-check=0')
		web.header('Pragma','no-cache') 
		web.header('ETag',str(time.time()))
		exec('getData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		date = int(time.strftime("%s"))
		return DB.insert(datamodel.TABLEREMOTEACTIONS, ACTION=getData["action"],PARAMETERS=getData['param'],SOURCESERVER=getData['server'],APPLICATIONTARGET=getData['application'],RESULT="",DATE=date) 
		
	def POST(self,uri):
		return "nope"


class remoteActionStatus:
	def GET(self,uri):
		web.header('Content-Type','application/json')
		web.header('Last-Modified','{now} GMT')
		web.header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
		web.header('Cache-Control','post-check=0, pre-check=0')
		web.header('Pragma','no-cache')
		exec('getData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		rs=DB.query("select DATE,RESULT from %s where ID=%s and SOURCESERVER=\"%s\"" % (datamodel.TABLEREMOTEACTIONS,str(getData['ID']),getData['server']))
		return str(json.dumps(list(rs)))


class remoteActionList:
	def GET(self,uri):
		web.header('Content-Type','application/json')
		web.header('Last-Modified','{now} GMT')
		web.header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
		web.header('Cache-Control','post-check=0, pre-check=0')
		web.header('Pragma','no-cache')
		exec('getData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		rs=DB.query("select ACTION from %s where SOURCESERVER=\"%s\" group by 1" % (datamodel.TABLEAVALIABLEACTIONS,str(getData['server'])))
		return str(json.dumps(list(rs)))



class remoteActionRegister:
	def POST(self,url):
#		try:
		stream = web.input(data={})
		return DB.insert(datamodel.TABLEAVALIABLEACTIONS, SOURCESERVER=stream.sourceserver,ACTION=stream.action,APPLICATION=stream.application)
#		except Exception as err:
#			print "Status update error: "+str(err)
#			return "500"

#(ID integer primary key autoincrement, SOURCESERVER text ,ACTION text, APPLICATION text)" % datamodel.TABLEAVALIABLEACTIONS)
