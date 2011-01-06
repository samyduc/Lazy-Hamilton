# -*- coding: utf-8 -*-
# TAD courtesy
# Samy Duc
# app main and config file

import web
import client
import job

urls = (
	'/', 'index',
	'/addclient', 'client.AddClient',
	'/delclient', 'client.DelClient',
	'/register', 'client.Register',
	'/logout', 'client.LogOut',
	'/showclient', 'client.ShowClient',
	'/chclient', 'client.ChClient',
	'/addjob', 'job.AddJob',
	'/getjob', 'job.GetJob',
	'/donejob', 'job.DoneJob',
	'/showjob', 'job.ShowJob',
)

# config
debug_string = "!"
salt_charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
cookie_name = "id"
cookie_age = 99999

# in seconds
range_timeout = 10
# dict
charset = {'a' : 'abcdefghijklmnopqrstuvwxyz',\
	'A' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',\
	'0' : '0123456789',\
	'*' : ' !\"#$%&\'()*+,-./:;<=>?@[\\]^_{|}~'}

db = web.database(dbn='sqlite', db='db.sqlite3')

class index:
	def GET(self):
		return "Lazy-Hamilton"
		
if __name__ == "__main__": 
	web.config.debug = True
	app = web.application(urls, globals())
	app.run()
	