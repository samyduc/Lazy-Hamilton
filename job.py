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

#
# Add a new job
# arg
# 	task : description of the task
#	descriptor : charset:salt:range
#	maxclient : maxclient for the job
#
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

#
# get a new job
# arg
# 	(optionnal) id : id of an old range
# do an old range if timeout
# else get a new range
#		
class GetJob:
	def GET(self):
		arg = web.input()
		
		# check credential (session)
		ret = client.check_credential(["x"], "cookie")
		if(ret == None):
			return app.debug_string
		
		# delete old task
		if('id' in arg):
			app.db.delete('range', where="range_id=$id", vars={ 'id' : arg['id']})
		
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
		row_id = app.db.insert('range', range_id_client=c.client_id, range_id_job=j.job_id, range_start=var_descriptor[2], range_length=range_value, range_timestamp="strftime('%s','now')")

		# render xml response
		web.header('Content-Type', 'text/xml')
		
		response = "<range>\
			<id>%s</id>\
			<start>%s</start>\
			<length>%s</length>\
			<charset>%s</charset>\
			<salt>%s</salt>\
			</range>" % (row_id, var_descriptor[2], range_value, var_descriptor[0], var_descriptor[1])
			
		# change job status
		var_descriptor[2] = generate_status(var_descriptor[2], range_value, var_descriptor[0])
		app.db.update('job', job_descriptor="%s" % (":".join(var_descriptor)), where="job_id=%s" % (j.job_id))
		
		return response

#
# Change the status of a job to 'done'
# arg
#	id : id of the working range
# 	descriptor : result
#
class DoneJob:
	def GET(self):
		arg = web.input()
		
		# check credential (session)
		ret = client.check_credential(["r"], "cookie")
		if(ret == None):
			return app.debug_string
		
		# check parameters
		if('id' not in arg or\
		'descriptor' not in arg):
			return app.debug_string
		
		# check credential (session)
		ret = client.check_credential(["x"], "cookie")
		if(ret == None):
			return app.debug_string
			
		# search range associated with this client
		entries = app.db.select('range', what="range_id, range_id_job", where="range_id=$id", vars={'id': arg['id']})
		
		# peek the first one
		temp = list(entries)
		if(bool(temp) == False):
			return app.debug_string
		r = temp[0]

		# security
		# do not erase result from a solved job
		entries = app.db.select('job', what="job_status", where="job_id=$id", vars={'id': r.range_id_job})
		
		temp = list(entries)
		
		if(bool(temp) == False):
			return app.debug_string
			
		j = temp[0]
		
		# avoid result poisoning
		# far from perfect
		if(j.job_status == "done"):
			return app.debug_string
			
		# udpate job	
		app.db.update('job', job_descriptor=arg['descriptor'], job_status="done", where="job_id=$id", vars={'id': r.range_id_job})

		# erase all range linked with this job
		app.db.delete('range', where="range_id_job=$id", vars={'id': r.range_id_job})
		
		return "donejob"

#
# Show job or one job and all related range
# arg
#	(optionnal) id : id of a job
#		
class ShowJob:
	def GET(self):
		arg = web.input()
		
		if('id' not in arg):
			# select everything
			entries = app.db.select('job', what="*")
			
			response = ""
			
			for entry in entries:
				response += "\n" + "-"*20 + "\n"
				response += str(entry)
				response += "\n" + "-"*20 + "\n"
			
			return response
			
		else:
			# select one job
			entries = app.db.select('job', what="*", where="job_id=$id", vars={'id': arg['id']})
			
			response = ""
			
			temp = list(entries)
		
			if(bool(temp) == False):
				return app.debug_string
			
			j = temp[0]
			
			response += "\n" + "-"*20 + "\n"
			response += str(j)
			response += "\n" + "-"*20 + "\n"
			
			# select all related range
			entries = app.db.select('range', what="*", where="range_id_job=$id", vars={'id': arg['id']})
		
			for entry in entries:
				response += "\n" + "-"*20 + "\n"
				response += str(entry)
				response += "\n" + "-"*20 + "\n"
			
			return response
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		