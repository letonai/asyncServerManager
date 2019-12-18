import web
import os,json
import time

class errorPage:
	
	def GET(self,uri):
		print("Request")
		return 404
		
	def POST(self,uri):
		return "nope"