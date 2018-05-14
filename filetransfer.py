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


CWD = os.path.dirname(os.path.abspath(__file__))+"/"
DBFILE=".controller.dat"
DB=web.database(dbn="sqlite",db=DBFILE)
TABLEFILES="files"
TABLEREMOTEFILES="remotefiles"
TABLEREMOTEACTIONS="remoteactions"

class fileList:
    def GET(self, uri):
		exec('getData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		rs=DB.query("select * from %s where SERVERTARGET='%s' and DOWNLOADED='0'" % (TABLEFILES,getData['servername']))
		files=[]
		for x in rs:
			fileInfo={
			  "FILENAME":x.FILENAME,
			  "FILEID":x.FILEID,
			  "APPLICATIONTARGET":x.APPLICATIONTARGET,
			  "HASH":x.HASH
			}
			files.append(fileInfo)
		ret=json.dumps(files)
		return ret
        #return "No files for you!"


    def POST(self,uri):
		return "Method not allowed"

class remoteDirList:
	
	def GET(self,uri):
		web.header('Content-Type','application/json')
		web.header('Last-Modified','{now} GMT')
		web.header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
		web.header('Cache-Control','post-check=0, pre-check=0')
		web.header('Pragma','no-cache')
		exec('getData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		#print getData['server']
		rs=DB.query("select SOURCESERVER,DIR from %s where SOURCESERVER=\"%s\"" % (datamodel.TABLEREMOTEDIR,getData['server']))
		return str(json.dumps(list(rs)))
		
	def POST(self,uri):
		return "nope"
	

class fileDownload:
	def GET(self, uri):
		exec('getData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		filedir = './uploads/'
		fileInfo=list(DB.query("select * from %s where SERVERTARGET='%s' and FILEID=%s" % (TABLEFILES,getData['servername'],getData['fileid'])))
		if getData['confirmDownload']=="OK":
			print "Download OK"
			print "update %s set DOWNLOADED='1' where FILEID='%s'" % (TABLEFILES,fileInfo[0]['FILEID']) 
			#pdb.set_trace()
			x = DB.update(TABLEFILES, where="FILEID='%s'" % (fileInfo[0]['FILEID']), DOWNLOADED="1")
			print "xxx: "+ x
			
		else:
			
			web.header("Content-Disposition", "attachment; filename=%s" % fileInfo[0]['FILENAME'])
			web.header("Content-Type", "application/octet-stream")
			web.header('Transfer-Encoding','chunked')
			f = open(filedir+fileInfo[0]['FILENAME'], 'rb')
			while 1:
				print "Sending file"
				buf = f.read(1024)
				if not buf:
					print 
					break
				yield buf
			DB.update(TABLEFILES, where="FILEID='%s'" % (fileInfo[0]['FILEID']), DOWNLOADED="1")
		return
		
	def POST(self,uri):
		print "Method not allowed"



class fileUpload:
	def GET(self, uri):
		print "Method not allowed"
#http://webpy.org/cookbook/fileupload
#http://webpy.org/cookbook/storeupload/
#curl -q -F data=@./static/file2.zip "http://localhost:8999/addfile?servertarget=localhost&app=TESTE"
	def POST(self, uri):
		exec('postData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		stream = web.input(data={})
		filedir = './uploads' # change this to the directory you want to store the file in.
		if 'data' in stream: # to check if the file-object is created
			rs=DB.query("select count(FILEID) as FILEID from %s" % (TABLEFILES))
			id=rs[0]['FILEID']
			hash = HASH()
			filepath=stream.data.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
			filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
			fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
			fout.write(stream.data.file.read()) # writes the uploaded file to the newly created file.
			fout.close() # closes the file, upload complete.
			md5=hash.md5(filedir +'/'+ filename)
			if not len(list(DB.query("select HASH from %s where HASH='%s'" % (TABLEFILES,md5))))>0:
				DB.insert('files',FILEID=id,FILENAME=filename,SERVERTARGET=postData["servertarget"],APPLICATIONTARGET=postData["app"],HASH=md5,DOWNLOADED="0")
			else:
				print "Arquivo ja existe"
		raise web.seeother('/upload')
		
#Recebe um GET e aguarda o agente detectar a solicitacao de download.
#o agente ao detectar a solicitacao fara um POST com o arquivo e liberara o GET com o stream do arquivo
#problema deste método é arquivos muito grandes vão travar o navegador ou receber timeout
#possível solução é fazer download do arquivo do servidor e liberar um link para download quando o arquivo
#estiver pronto, amarrar esse link por id de usuário/sessão, uma pagina ajax vai consultar os arquivos disponiveis e disponibilizar o link
class fileDownloadFromServer:
	 	
	def GET(self,uri):
		if web.ctx['query'].strip("?") == "avaliableList":
			return json.dumps(list(DB.query("select * from %s" % (TABLEREMOTEFILES))))
			
	#curl -F data=@./tmpSrvDownloads/web.py-0.38.tar -F "servername=raspberry" -F "application=teste" "http://localhost:8999/getfromserver"
	def POST(self,uri):
		hash = HASH()
		stream = web.input(data={})
		fileOnDisk = open("tmpSrvDownloads/"+stream.data.filename,"w+")
		fileOnDisk.write(stream.data.file.read())
		fileOnDisk.flush()
		fileOnDisk.close()
		md5=hash.md5("tmpSrvDownloads/"+stream.data.filename)
		if len(list(DB.query("select FILEID as FILEID from %s where FILENAME='%s' and HASH='%s'" % (TABLEREMOTEFILES,stream.data.filename,md5))))==0:
			id=DB.query("select count(FILEID) as FILEID from %s" % (TABLEREMOTEFILES))[0]['FILEID']
			DB.insert(TABLEREMOTEFILES,FILEID=id,FILENAME=stream.data.filename,SOURCESERVER=web.input().servername,APPLICATIONTARGET=web.input().application,HASH=md5,DOWNLOADED="0")
			return "File ready"
		else:
			return "File already exists"
		
		
#Antigo		
# class fileDownloadFromServer:
# 	stream=None
# 	def GET(self,uri):
# 		print uri
# 		while fileDownloadFromServer.stream==None:
# 			time.sleep(1)
# 		print fileDownloadFromServer.stream
# 		filename=str(fileDownloadFromServer.stream['data'].filename)
# 		data=fileDownloadFromServer.stream.data.file.read()
# 		fileDownloadFromServer.stream=None
# 		data64=base64.b64encode(data)
# 		return "<html><body><a download='"+filename+"' href='data:application/octet-stream;charset=utf-8;base64,"+data64+"'>Download</a></body></html>"

# 	def POST(self,uri):
# 		fileDownloadFromServer.stream = web.input(data={})
		


