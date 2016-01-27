#Tornado Libraries
from tornado.ioloop import IOLoop
from tornado.escape import json_encode
from tornado.web import RequestHandler, Application, asynchronous, removeslash
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import engine, Task, coroutine

from motor import MotorClient
import os

db = MotorClient('mongodb://shubho:deep@ds047865.mongolab.com:47865/analyticsweekly').analyticsweekly

class MainHandler(RequestHandler):
	def get(self):
		self.write('Hello World')

class SignupHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self):
		self.render('register.html')

	@removeslash
	@coroutine
	def post(self):
		name = self.get_argument('name')
		email = self.get_argument('email')
		password = self.get_argument('password')
		_type = self.get_argument('type')
		users = yield db.Users.find_one({'email':email})
		if not bool(users):
			insert = yield db.Users.insert({'name':name,'email':email,'password':password,'type':_type})
		self.redirect('/')

class SigninHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self):
		self.render('login.html')

	@removeslash
	@coroutine
	def post(self):
		email = self.get_argument('email')
		password = self.get_argument('password')
		user = yield db.Users.find_one({'email':email,'password':password})
		if bool(user):
			self.set_secure_cookie('user')
			

settings = dict(
		template_path = os.path.join(os.path.dirname(__file__), "templates"),
		static_path = os.path.join(os.path.dirname(__file__), "static"),
		debug=True,
		cookie_secret="49fd21b3-b96b-4f18-9ff8-260c64fe10e9"
	)

application = Application([
	(r"/", MainHandler),
	(r"/register", SignupHandler),
	(r"/login", SigninHandler)
	], **settings)

#main init
if __name__ == "__main__":
	server = HTTPServer(application)
	server.listen(8000)
	IOLoop.current().start()