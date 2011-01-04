# -*- coding: utf-8 -*-
# TAD courtesy
# Samy Duc
# job module
# handle job management

import web
import app
import client

# build charset
def build_charset(charset_option):
	charset = ""
	for char in charset_option:
		charset += app.charset[char]
		
	return charset	

# give next step for word generation algorithm
def generate_next_step(word, charset):
	# just need to add a new character
	if(len(word) == 0):
		word.append(charset[0])
		return True
	index = charset.find(word[-1])
	try:
		word[-1] = charset[index+1]
	except IndexError:
		word[-1] = charset[0]
		temp = word[:-1]
		generate_next_step(temp, charset)
		# tricky
		del word[:-1]
		temp.reverse()
		word.extend(temp)
		word.reverse()
	finally:
		return False
# generate new status from job given
def generate_status(start, range, charset_option):
	charset = build_charset(charset_option)
	
	# transform string to list
	# because string are imutable
	start = list(start)
	# last character, python powered
	i = 0
	while(i < range):
		generate_next_step(start, charset)
		i += 1
	# transform list to string
	# because we store string
	return "".join(start)

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
		# search current job
		entries = app.db.select('job', what="job_id, job_descriptor, job_task, job_status", where="job_maxclient >= job_client and job_status<>'done'")
		
		# peek the first one
		temp = list(entries)
		
		if(bool(temp) == False):
			return app.debug_string
		j = temp[0]
		
		# peek client id and cpu capabilities
		cookie = web.cookies().get(app.cookie_name)
		entries = app.db.select('client', what="client_id, client_cpu", where="client_cookie='%s'" % (cookie))
		
		temp = list(entries)
		
		if(bool(temp) == False):
			return app.debug_string
		c = temp[0]
		
		# compute settings from job_descriptor
		# charset:salt:range
		var_descriptor = j.job_descriptor.split(':', 2)
		
		# must be compute with cpu value
		range_value = 500000
		
		# create new range (with default value for the moment)
		app.db.insert('range', range_id_client=c.client_id, range_id_job=j.job_id, range_start=j.job_status, range_length=range_value, range_timestamp="strftime('%s','now')")
		
		# render xml response
		web.header('Content-Type', 'text/xml')
		
		response = "<range>\
			<start>%s</start>\
			<length>%s</length>\
			<charset>%s</charset>\
			<salt>%s</salt>\
			</range>" % (var_descriptor[2], range_value, var_descriptor[0], var_descriptor[1])
			
		# change job status
		var_descriptor[2] = generate_status(var_descriptor[2], range_value, var_descriptor[0])
		app.db.update('job', job_descriptor="%s" % (":".join(var_descriptor)), where="job_id=%s" % (j.job_id))
		
		return response
		
		
		
		
		
		
		
		
		
		
		
		
		
		