# -*- coding: utf-8 -*-
# TAD courtesy
# Samy Duc
# job module
# handle job management

import web
import app
import client
import json

class AddJob:
	def GET(self):
		arg = web.input()

		# check parameters
		if('task' not in arg or \
			'descriptor' not in arg or \
			'maxclient' not in arg):
			return app.debug_string
			
		# check credential (session)
		ret = client.check_credential(["w"], "cookie")
		if(ret == None):
			return app.debug_string
		
		# add job
		t = app.db.transaction()
		try:
			app.db.insert('job', job_maxclient=int(arg['maxclient']), job_task=arg['task'],\
				job_descriptor=arg['descriptor'], job_status="fresh", job_client=0)
		except:
			t.rollback()
		else:
			t.commit()
		
		return "addjob"
		
class GetJob:
	def GET(self):
		arg = web.input()
		
		# check credential (session)
		ret = client.check_credential(["x"], "cookie")
		if(ret == None):
			return app.debug_string
			
		# searsh if current task timeout
		entries = app.db.select('range', what="range_id, range_id_job, range_start, range_length", where="DATETIME(range_timestamp, 'now') > %s " % (str(app.range_timeout)))
		
		# give oldest task
		for entry in entries:
			#TODO
			return "lol"
		
		# if no task
		# searsh current job
		entries = app.db.select('job', what="job_id, job_descriptor, job_task", where="job_maxclient <= job_client and job_status='fresh'")
		
		
		
		return
		
		
		
		
		
		
		
		
		
		
		
		
		
		