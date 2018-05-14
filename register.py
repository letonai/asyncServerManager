import web
import os
import socket
import json

CWD = os.path.dirname(os.path.abspath(__file__))+"/"
DBFILE=".controller.dat"
DB=web.database(dbn="sqlite",db=DBFILE)

class agentRegister:
    def GET(self, uri):
        web.header('Content-Type','application/json')
        web.header('Last-Modified','{now} GMT')
        web.header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
        web.header('Cache-Control','post-check=0, pre-check=0')
        web.header('Pragma','no-cache') 
    	rs=DB.query('select SERVERNAME from %s' % ('agents'))
    	#rs=DB.query('select SOURCESERVER,DIR from remotedir left join agents')
        return str(json.dumps(list(rs)))

    def POST(self,uri):
		exec('postData={"'+web.data().replace('=','":"').replace('&','","')+'"}')
		if  postData['action']=="register":
			print postData['servername']
			checkServer=DB.query('select IP from %s where SERVERNAME="%s"' % ('agents',postData['servername']))
			if len(list(checkServer))>0:
				return "Server already registred!"
			else:	
				print "Register: "+str(postData)
				DB.insert('agents',SERVERNAME=postData["servername"],IP=web.ctx['ip'])
				return "Registred..."
		elif postData['action']=="unregister":
			self.agentUnregister(postData["servername"])
			return "Server "+postData["servername"]+" unregistred"

		elif postData['action']=="check":
			return self.agentCheckRegister(postData["servername"],web.ctx['ip'])

		else: 
			return "Wrong post data"

    def agentUnregister(self,server):
		if self.agentCheckRegister(server,web.ctx['ip']):
			deleteServer=DB.query('delete from %s where SERVERNAME="%s"' % ('agents',server))
			return "unregistred"
		else:
			return "not registred"

    def agentCheckRegister(self,server,ip):
		checkServer=DB.query('select * from %s where SERVERNAME="%s" and IP="%s"' % ('agents',server,ip))
		for srv in checkServer:
			return True
		return False 



