import web
import os,json
import time


CWD = os.path.dirname(os.path.abspath(__file__))+"/"
DBFILE=".controller.dat"
DB=web.database(dbn="sqlite",db=DBFILE)
TABLEREMOTEACTIONS="remoteactions"

class status:

	def GET(self,url):
		web.header('Content-Type','application/json')
		web.header('ETag',str(time.time()))
		web.header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
		web.header('Cache-Control','post-check=0, pre-check=0')
		web.header('Pragma','no-cache') 
		#/getremotequeuedactions"
		exec('getData={"'+web.ctx['query'].replace('=','":"').replace('&','","').strip('?')+'"}')
		rs=DB.query("select ACTION,PARAMETERS, DATE from %s where ifnull(RESULT, '') = '' and SOURCESERVER='%s' and REQUESTDATE > %d" % (TABLEREMOTEACTIONS,getData['servername'],(time.time()-120)))
		return json.dumps(list(rs))
	 
	def POST(self,url):
		try:
			stream = web.input(data={})
			print "XXXXXX: "+str(stream)
			exec("date="+str(stream['DATE']))
			DB.update(TABLEREMOTEACTIONS, where="DATE="+str(date), RESULT=str(stream['cmdreturn']))
			return 200
		except Exception as err:
			print "Status update error: "+str(err)
			exec("date="+str(stream['DATE']))
			DB.update(TABLEREMOTEACTIONS, where="DATE="+str(date), RESULT="ERROR")


