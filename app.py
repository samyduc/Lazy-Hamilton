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
	'/chclient', 'client.ChClient',
	'/addjob', 'job.AddJob',
	'/getjob', 'job.GetJob',
)

# config
debug_string = "!"
salt_charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
cookie_name = "id"
cookie_age = 99999

# in seconds
job_timeout = 10

db = web.database(dbn='sqlite', db='db.sqlite3')

class index:
	def GET(self, name=0):
		return name
		
if __name__ == "__main__": 
	web.config.debug = True
	app = web.application(urls, globals())
	app.run()
	