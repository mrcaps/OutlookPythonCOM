"""
Ilari Shafer
4/30/07
Simple server that allows connection to a few dynamic methods
	(provided by OutlookInterface) and serves up static pages
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse
from _outlook import *
import os

outlook = None

#call the given method with the specified query string
def qs_call(method, qs):
	allargs = dict()
	alst = qs.split("&")
	
	print alst
	
	for arg in alst:
		l = arg.split("=")
		if len(l) >= 2:
			allargs[l[0]] = l[1]
		
	return method(**allargs)

#define a custom response to HTTP requests
class Handler(BaseHTTPRequestHandler):
	#send back the given string to the client, requesting
	#no caching if cache is False
	def toss(self, str, cache):
		self.send_response(200)
		self.send_header("Content-type","text-html")
		if not cache:
			self.send_header("Expires","Mon, 26 Jul 1997 05:00:00 GMT" ); 
			self.send_header("Cache-Control","no-cache, must-revalidate"); 
			self.send_header("Pragma","no-cache");
		
		self.end_headers()
		self.wfile.write(str)
	
	#handle GET requests from clients
	def do_GET(self):
		pstr = urlparse(self.path)
		
		if pstr[2].startswith("/Outlook."):
			#invoke a method on our Outlook object
			print "Outlook invocation:", pstr
			method = getattr(outlook, pstr[2].split(".")[1])
			self.toss(qs_call(method, pstr[4]),False)
		elif os.path.exists(pstr[2][1:]):
			#return files
			fh = open(pstr[2][1:],"r")
			self.toss(fh.read(),True)
			fh.close()
		else:
			self.send_error(404,"Ugh, error.")

outlook = OutlookInterface()
server = HTTPServer(("",8080),Handler)
print "Serving!"
server.serve_forever()