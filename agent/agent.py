#!/usr/bin/python
# -*- coding: utf-8 -*-
import web
import urllib2
import requests
import socket
import argparse
import os
import time
import json
import shutil
import sys
import subprocess
import imp
import inotify.adapters
import threading 
from time import sleep
import signal

#IPADDR=socket.getaddrinfo(socket.gethostname(),22)[0][4][0]
SERVERNAME=socket.gethostname()
DATA = {'servername':SERVERNAME}
CWD = os.path.dirname(os.path.abspath(__file__))+"/"
DBFILE=".agent.dat"
DB=web.database(dbn="sqlite",db=DBFILE)
TABLESRVCFG="SERVERCFG"
mainExit=False
#http_proxy=http://10.170.136.135:8080
#https_proxy=http://10.170.136.135:8080

#

proxies = {'https': 'http://10.170.136.135:8080'}

def moduleWatcher():
	i = inotify.adapters.Inotify()
	i.add_watch('./modules')
	for event in i.event_gen():
		if mainExit:
			print "EXIT"
			sys.exit()
		if event is not None:
			(header, type_names, watch_path, filename) = event
			if type_names[0] in ('IN_CREATE','IN_MOVED_TO'):
				if filename.endswith(".py"):
					print "Modulo adicionado: "+filename
					print "registrando novo modulo"
					DATA['sourceserver']=socket.gethostname()
					DATA['action']=filename[0:len(filename)-3].strip(".")
					DATA['application']="teste"
					URL='https://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)+"/registerremoteaction"
					print URL
					response = requests.post(URL, data=DATA, proxies=proxies,verify=False)
					print response
				else:
					print "no new modules..."

def getRemoteServerInfo():
	rs=list(DB.query("select * from %s" % (TABLESRVCFG)))
	if len(rs)<1:
		print "No server Registred! Must run agent -h"
		sys.exit()
	for URL in rs:
		return URL
		

def serverRegister(server):
	DATA['action']="register"
	DATA['servername']=SERVERNAME
	response = requests.post("https://"+server+'/agentregister', proxies=proxies,data=DATA,verify=False)
	print "Server say: "+str(response.content)
	if response.status_code == 200:
		if len(list(DB.query("select * from %s" % (TABLESRVCFG))))>0:
			print "Agent say: "+" previous remote server found within agent configuration, replacing then!"
			DB.query("delete from %s" % (TABLESRVCFG))
			DB.insert(TABLESRVCFG,IP=server.split(':')[0],PORT=server.split(':')[1])
			print "Agent say; "+"Done"
		else:
			DB.insert(TABLESRVCFG,IP=server.split(':')[0],PORT=server.split(':')[1])


def serverUnregister():
	response= requests.Response()
	try:
		DATA['action']="unregister"
		DATA['servername']=SERVERNAME
		URL='https://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)+'/agentregister'
		response = requests.post(URL,  proxies=proxies,data=DATA,verify=False)
		print response.status_code
		if response.status_code<500:
			print "Server say: "+str(response.content)
			DB.query("delete from %s" % (TABLESRVCFG))
			print "Agent say: "+"cleaning up agent configuration."
		else:
			response.raise_for_status()
	except Exception as err:
		print str(err)



def agentBeacon():
	try:
		URL='https://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)+"/getremotequeuedactions"
		DATA['servername']=SERVERNAME
		date=""
		response = requests.get(URL, params=DATA,stream=True ,proxies=proxies,verify=False)
		if response.status_code==200:
			print "Result: "+str(response.content)
			cmd=json.loads(response.content)
			for c in cmd:
				#Busca os modulos no diretorio "modules" e importa, cada modulo deve conter um metodo run()
				module = str(c[c.keys()[0]])
				date=c[c.keys()[1]]
				f, filename, description = imp.find_module("modules/"+module)
				m=imp.load_module(module,f,filename,description)
				
				cmd="DATA[\"cmdreturn\"]=\""+m.run(c[c.keys()[2]])#.replace("\n",' ')+"\""
				print cmd
				DATA["DATE"]=c[c.keys()[1]]
				exec(cmd)
				#print DATA
				postresponse = requests.post(URL, params=DATA,stream=True,verify=False)
				print postresponse
		else:
			response.raise_for_status()

	except ImportError as impErr:
		print "Import error: "+str(impErr)
		cmd="DATA[\"cmdreturn\"]=\""+str(impErr)+"\""
		exec(cmd)
		DATA["DATE"]=date
		requests.post(URL, params=DATA,stream=True,proxies=proxies,verify=False)
	except Exception as err:
		print "ERRO: "+str(err)
	print "Beacon "+URL

def fileDownloader(fileid,application,filename):
	URL='https://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)
	DATA['fileid']=fileid
	DATA['confirmDownload']="NOK"
	response = requests.get(URL+'/filedownload', params=DATA,stream=True, proxies=proxies,verify=False)
	if response.status_code == 200:
		i = 0
		with open('download/'+filename, 'w') as f:
			for chunk in response.iter_content(1024):
				i+=1
				if chunk:
					f.write(chunk)
					f.flush()
			#print "tchau"
				#sys.stdout.write('.')

		print "\nFile Downloaded"
	else:
		print "Agent say: "+"Server Error "+str(response.status_code)+str(response)

def fileUpload():
	URL='http://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)
	response = requests.get(URL+'/getfromserver', params="avaliableList",stream=True,proxies=proxies,verify=False)
	files=json.loads(response.content)
	
def confirmDownload(fileid):
	URL='http://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)
	DATA['confirmDownload']="OK"
	DATA['fileid']=fileid
	response = requests.get(URL+'/filedownload', params=DATA,stream=True,proxies=proxies,verify=False)
	if response.status_code == 200:
		print "Download registred on server "+str(response.status_code)
	else: 
		print "Error: "+str(response.status_code)
	


def getFileDownloadList():
	URL='http://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)
	print URL
	response = requests.get(URL+'/getfilelist',params=DATA,proxies=proxies,verify=False)
	return response.content
	
def checkDownloadableFiles():
	files = getFileDownloadList()
	print files
	for f in list(json.loads(files)):
		print "Downloading: "+f['FILENAME']
		fileDownloader(f['FILEID'],f['APPLICATIONTARGET'],f['FILENAME'])
		#confirmDownload(f['FILEID'])
	
	

def extensionRunner():
	print "extension"

def killThread(self,x):
	global mainExit
	mainExit=bool(True)
	print "Saiu: "+str(mainExit)
	exit(0)
		
def agentStartDeamon():
	t1 = threading.Thread(target=moduleWatcher, args=[])
	t1.start()
	signal.signal(signal.SIGINT, killThread)
	print "start"
	while mainExit==False:
		print "Running..."
		time.sleep(5)
		#URL='http://'+getRemoteServerInfo().IP+":"+str(getRemoteServerInfo().PORT)
		#response = requests.get(URL+'/getfilelist',params=DATA)
		#print checkDownloadableFiles() 
		agentBeacon()
	

parser = argparse.ArgumentParser(description='WASManager Agent',epilog="by Ricardo Letonai")

parser.add_argument('-r','--register', metavar=('IP:PORT'), type=serverRegister, nargs=1,action='store',help='Register this server on controller.')
#parser.add_argument('-u','--unregister', metavar=('SERVERNAME'), type=serverUnregister, nargs='?',const=DATA['servername'],action='store',help='Unregister a server on controller. Empty parameter = this server')
parser.add_argument('-u','--unregister',action='store_true', help='Unregister this server from remote controller (clear all local agent configuration)')
parser.add_argument('-d','--deamon',action='store_true', help='Start agent as deamon')
parser.add_argument('-p','--proxy',action='store_true', help='Use proxy')
parser.add_argument('-t','--test',action='store_true', help='Test')


args = parser.parse_args()

if args.deamon:
	agentStartDeamon()
if args.unregister:
	serverUnregister()
if args.test:
	#for dwlInfo in getFileDownloadList():
	#	fileDownloader(dwlInfo['FILEID'],dwlInfo['APPLICATIONTARGET'],dwlInfo['FILENAME'])
	fileUpload()

def firstRun():
    print "No previous configuration detected for the agent!"
    DB.query("create table "+TABLESRVCFG+" (IP text,PORT txt)")

if __name__ == "__main__":
    if not os.path.exists( DBFILE ):
        firstRun()



