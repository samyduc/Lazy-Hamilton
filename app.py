# -*- coding: utf-8 -*-
# TAD courtesy
# Samy Duc
# app main and config file

import web
import client
import job
import public

urls = (
	'/', 'public.Stats',
	'/index', 'index',
	'/addclient', 'client.AddClient',
	'/delclient', 'client.DelClient',
	'/register', 'client.Register',
	'/logout', 'client.LogOut',
	'/showclient', 'client.ShowClient',
	'/chclient', 'client.ChClient',
	'/addjob', 'job.AddJob',
	'/getjob', 'job.GetJob',
	'/donejob', 'job.DoneJob',
	'/pausejob', 'job.PauseJob',
	'/unpausejob', 'job.UnpauseJob',
	'/showjob', 'job.ShowJob',
)

# config
debug_string = "!"
salt_charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
cookie_name = "id"
cookie_age = 99999

score_down = 300000

# computation time in second for an average range
# number of computation choosen with this variable and cpu availability on host
average_range_time = 900

# mm:ss
range_timeout = '00:30:00'
# dict
charset = {'a' : 'abcdefghijklmnopqrstuvwxyz',\
	'A' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',\
	'0' : '0123456789',\
	'*' : ' !#$%&()*+,-./:;<=>?@[\\]^_{|}~'}

db = web.database(dbn='postgres', user='', pw='', db='', host='')

render = web.template.render('templates/')

class index:
	def GET(self):
		return "Lazy-Hamilton"
		
if __name__ == "__main__": 
	web.config.debug = True
	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
	app = web.application(urls, globals())
	app.run()
	