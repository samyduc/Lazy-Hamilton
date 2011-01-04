# -*- coding: utf-8 -*-
# TAD courtesy
# Samy Duc
# client module
# handle authentification and credential
# basic client management

import time
import random
import hashlib
import web
import app


def generate_salt():
	salt = ""
	# pick 3 random characters from charset
	salt += random.choice(app.salt_charset)
	salt += random.choice(app.salt_charset)
	salt += random.choice(app.salt_charset)
	return salt

# note : password MUST be hashed !
def build_password(password, salt=None):
	if(salt == None):
		salt = generate_salt()
	b = hashlib.sha256(password + salt).hexdigest()
	return b, salt
	
# generate new cookie
def generate_cookie(nickname):
	cookie = nickname + str(time.time()) + random.choice(app.salt_charset)
	return hashlib.sha256(cookie).hexdigest()

# check credential using one of two methods
def check_credential(credential, method, nickname=None):
	if(method == "cookie"):
		return check_credential_cookie(credential)
	else:
		return check_credential_nickname(credential, nickname)

# check credential from cookie
def check_credential_cookie(credential):
	cookie = web.cookies()
	if(cookie == None):
		return None
	cookie_id = cookie.get(app.cookie_name)
	if(cookie_id == None):
		return None
		
	entries = app.db.select('client', what="client_cookie, client_credential", where="client_cookie='%s'" % (cookie_id))

	# check if entry exists and compare value
	temp = list(entries)
	if(bool(temp) == False):
		return None
	entry = temp[0]
	if(entry.client_cookie != cookie_id):
		return None
	entry = temp[0]
	if(check_credential_basic(credential, entry) == False):
		return None
	else:
		return "Ok"

# check credential from nickname
def check_credential_nickname(credential, nickname):
	entries = app.db.select('client', what="client_cookie, client_credential", where="client_nickname='%s'" % (nickname))

	# nickname must be unique
	# ugly hack with list because sqlite do not return the number of row (from official mailing list)
	temp = list(entries)
	if(bool(temp) == False):
		return None
	entry = temp[0]
	
	if(check_credential_basic(credential, entry) == False):
		return None

	# if no cookie, create new one
	if(entry.client_cookie == None):
		cookie =  generate_cookie(nickname)
		# save new cookie in database
		t = app.db.transaction()
		app.db.update('client', client_cookie=cookie, where='client_nickname="%s"' % (nickname))
		try:
			app.db.update('client', client_cookie=cookie, where='client_nickname="%s"' % (nickname))
		except:
			t.rollback()
		else:
			t.commit()
		return cookie
	else:
		return entry.client_cookie
	
# basic credential check
def check_credential_basic(credential, entry):

	for current in credential:
		if(entry.client_credential.find(current) == -1):
			return False
	return True
	
# check authentification from login / password
def check_authentification(nickname, password):
	entries = app.db.select('client', what="client_password, client_salt", where="client_nickname='%s'" % (nickname))
	
	temp = list(entries)
	
	if(bool(temp) == False):
		return False
	entry = temp[0]
	
	# hash password
	password, salt = build_password(password, entry.client_salt)
	
	if(password != entry.client_password):
		return False
	else:
		return True
	
	
class AddClient:
	def GET(self):
		arg = web.input()

		# check parameters
		if('nickname' not in arg or \
			'password' not in arg):
			return app.debug_string
			
		# check credential (session)
		if(check_credential(["w"], "cookie") == None):
			return app.debug_string
		
		# insure unicity of nickname
		entries = app.db.select('client', what="client_nickname", where="client_nickname='%s'" % (arg['nickname']))
		if(bool(entries) != False):
			return app.debug_string
		
		# insert new user
		password, salt = build_password(arg['password'])
		
		t = app.db.transaction()
		try:
			app.db.insert('client', client_nickname=arg['nickname'], client_password=password, client_salt=salt, client_credential="x")
		except:
			t.rollback()
		else:
			t.commit()
			
		return "addclient"
			
class Register:
	def GET(self):
		arg = web.input()

		# check parameters
		if('nickname' not in arg or \
			'password' not in arg or \
			'cpu' not in arg):
			return app.debug_string
		
		# do authentification
		if(check_authentification(arg['nickname'], arg['password']) == False):
			return "no authentification"
		
		# check credential (session)
		# usefull to ban people or force disconnexion
		cookie = check_credential(["x"], "nickname", arg['nickname'])
		if(cookie == None):
			return app.debug_string
			
		# set cookie
		# warning : cookie is already saved for us in db
		web.setcookie(app.cookie_name, cookie, app.cookie_age)
		
		# save cpu power
		t = app.db.transaction()
		try:
			app.db.update('client', client_cpu=float(arg['cpu']), where="client_cookie='%s'" % (cookie))
		except:
			t.rollback()
		else:
			t.commit()
		
		
		return "register"

class ChClient:
	def GET(self):
		arg = web.input()
		
		# check parameters
		if('nickname' not in arg or \
			'right' not in arg):
			return app.debug_string
			
		# check credential (session)
		ret = check_credential(["w"], "cookie")
		if(ret == None):
			return app.debug_string
			
		# be sure that new right are ok
		for letter in arg['right']:
			if(letter != "r" and letter != "w" and letter != "x"):
				return app.debug_string
		
		# update right
		t = app.db.transaction()
		try:
			app.db.update('client', client_credential=arg['right'], where="client_nickname='%s'" % (arg['nickname']))
		except:
			t.rollback()
		else:
			t.commit()
		
		return "chclient"
		
class DelClient:
	def GET(self):
		arg = web.input()
		
		# check parameters
		if('nickname' not in arg):
			return app.debug_string
			
		# check credential (session)
		ret = check_credential(["w"], "cookie")
		if(ret == None):
			return app.debug_string
		
		cookie = web.cookies().get(app.cookie_name)
		
		# del user
		t = app.db.transaction()
		try:
			app.db.delete('client', where="client_nickname='%s'" % (arg['nickname']))
		except:
			t.rollback()
		else:
			t.commit()
		
		return "delclient"
		
class LogOut:
	def GET(self): 
		# check credential (session)
		ret = check_credential(["x"], "cookie")
		if(ret == None):
			return app.debug_string
		
		cookie = web.cookies().get(app.cookie_name)
		
		# delete cookie in database
		t = app.db.transaction()
		try:
			app.db.update('client', client_cookie=None, where="client_cookie='%s'" % (cookie))
		except:
			t.rollback()
		else:
			t.commit()
		
		return "logout"
		

		
		
		
		