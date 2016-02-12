#Tornado Libraries
from tornado.ioloop import IOLoop
from tornado.escape import json_encode
from tornado.web import RequestHandler, Application, asynchronous, removeslash
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import engine, Task, coroutine

from motor import MotorClient
import os

db = MotorClient().analyticsweekly

class MainHandler(RequestHandler):
	@removeslash
	def get(self):
		if not bool(self.get_secure_cookie("user")):
			self.redirect('/login')
		self.render('file.html')
	@coroutine
	def post(self):
		_id = self.get_secure_cookie("user")
		files = self.request.files['file'][0]
		_query = self.get_argument("query")
		_select = self.get_argument("select")
		fnd = yield db.files.find({'uid':str(_id)}).to_list(None)
		count = len(fnd)+1
		extn = os.path.splitext(files['filename'])[1]
		cname = str(_id) +'_'+str(count)+ extn
		fh = open("static/uploads/" + cname, 'w')
		fh.write(files['body'])
		insert = yield db.files.insert({'uid':str(_id),'file':cname,'query':_query,'methods':_select})
		self.redirect('/')
		



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
		if not bool(self.get_secure_cookie("user")):
			self.render('index.html')
		else:
			self.redirect('/')

	@removeslash
	@coroutine
	def post(self):
		email = self.get_argument('email')
		password = self.get_argument('password')
		user = yield db.Users.find_one({'email':email,'password':password})
		if bool(user):
			self.set_secure_cookie('user', str(user['_id']))
			self.redirect('/')
		else:
			self.redirect('/login')
	
class LogoutHandler(RequestHandler):
	@removeslash
	def get(self):
		self.clear_cookie('user')
		self.redirect("/login")		


class AdminHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self):
		res = yield db.files.find().to_list(None)
		self.render('admin.html',res = res)

settings = dict(
		template_path = os.path.join(os.path.dirname(__file__), "templates"),
		static_path = os.path.join(os.path.dirname(__file__), "static"),
		debug=True,
		cookie_secret="49fd21b3-b96b-4f18-9ff8-260c64fe10e9"
	)

application = Application([
	(r"/", MainHandler),
	(r"/register", SignupHandler),
	(r"/login", SigninHandler),
	(r"/logout", LogoutHandler),
	(r"/admin", AdminHandler)
	], **settings)

#main init
if __name__ == "__main__":
	server = HTTPServer(application)
	server.listen(8000)
	IOLoop.current().start()