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
def generate_status(start, size, charset_option):
	charset = build_charset(charset_option)
	i = -1
	trueSize = 1
	while(size > len(charset)):
		if (len(start) < -i):
			start.append(charset[0])
		size = size/len(charset)
		i = i-1
		trueSize = trueSize*len(charset)
		
	# the size is now less than the charset length
	trueSize = trueSize*size
	temp = start[:len(start)+i+1]
	for j in range(0, size):
		generate_next_step(temp, charset)
		
	for value in start[i+1:]:
		temp.append(value)

	return "".join(temp), trueSize

#
# Add a new job
# arg
#	name : name of the job
# 	task : description of the task
#	descriptor : charset:salt:range
#	maxclient : maxclient for the job
#
class AddJob:
	def GET(self):
		arg = web.input()

		# check parameters
		if( 'name' not in arg or \
			'task' not in arg or \
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
			app.db.insert('job', job_maxclient=int(arg['maxclient']), job_name=arg['name'], \
				job_task=arg['task'], job_descriptor=arg['descriptor'], job_status="fresh", \
				job_client=0)
		except:
			t.rollback()
			return app.debug_string
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

	# update score depending on finished range
	def update_score(self, arg):
		entries = app.db.query("SELECT * FROM range JOIN client ON range.range_id_client = client.client_id and range.range_id = $id", \
			vars={'id': arg['id']})
		temp = list(entries)
		if(bool(temp) != False):
			score = temp[0].client_time
			score += temp[0].range_length / app.score_down + 1 # minimum increment is one
			app.db.update('client', client_time=score, where="client_id=$id", vars={ 'id' : temp[0].client_id})
			
		# delete
		app.db.delete('range', where="range_id=$id", vars={ 'id' : arg['id']})
		
	# r : recycle range
	def recycling(self, r):
		# select related job
		# peak the first one
		entry = app.db.select('job', what="job_id, job_name, job_descriptor, job_task, job_status", \
			where="job_id=$id", vars={'id':r.range_id_job})
				
		temp = list(entry)
			
		if(bool(temp) == False):
			return app.debug_string
		j = temp[0]
			
		# update current range to change id with current client
		cookie = web.cookies().get(app.cookie_name)
		
		entries = app.db.select('client', what="client_id, client_cpu", \
				where="client_cookie=$cookie", vars= {'cookie' : cookie})
		temp = list(entries)
		if(bool(temp) == False):
			return app.debug_string
		c = temp[0]
		app.db.update('range', range_id_client=c.client_id, range_timestamp="now()", \
				where="range_id=$id", vars= {'id' : r.range_id})
		
		var_descriptor = j.job_descriptor.split(':', 2)
		
		return r.range_id, r.range_length, j.job_task, var_descriptor[0], var_descriptor[1], r.range_start
			
	def craft(self):
		entries = app.db.select('job', what="job_id, job_name, job_descriptor, job_task, job_status", \
					where="job_maxclient >= job_client and job_status='fresh'", order="job_id")
			
		# peek the first one
		temp = list(entries)
			
		if(bool(temp) == False):
			return app.debug_string
		j = temp[0]

		# peek client id and cpu capabilities
		cookie = web.cookies().get(app.cookie_name)
		entries = app.db.select('client', what="client_id, client_cpu", \
					where="client_cookie=$cookie", vars= {'cookie' : cookie})
			
		temp = list(entries)
			
		if(bool(temp) == False):
			return app.debug_string
		c = temp[0]
			
		# must be compute with cpu value
		range_value = int(c.client_cpu*app.average_range_time)
		
		# compute settings from job_descriptor
		# charset:salt:range
		var_descriptor = j.job_descriptor.split(':', 2)
			
		start = var_descriptor[2]
		
		temp = list(var_descriptor[2])
		var_descriptor[2], range_value = generate_status(temp, range_value, var_descriptor[0])
		
		# create new range (with default value for the moment)
		t = app.db.transaction()
		row_id = 0
		
		try:
			row_id = app.db.insert('range', range_id_client=c.client_id, range_id_job=j.job_id, range_start=start, \
						range_length=range_value, range_timestamp='NOW()')
		except:
			t.rollback()
			return app.debug_string 
		else:
			t.commit()
				
		# awful hack to get the last id
		# bug : raw_id is always empty
		entries = app.db.select('range', what="range_id", \
					where="range_id_client=$id", vars={'id':c.client_id}, order="range_timestamp desc", limit=1)
		temp = list(entries)
		if(bool(temp) == False):
			return app.debug_string
		r = temp[0]
			
		# change job status
		app.db.update('job', job_descriptor=":".join(var_descriptor), \
			where="job_id=$id", vars= {'id':j.job_id})
			
		return r.range_id, range_value, j.job_task, var_descriptor[0], var_descriptor[1], start

	def GET(self):
		arg = web.input()
		recycle = False
		# check credential (session)
		ret = client.check_credential(["x"], "cookie")
		if(ret == None):
			return app.debug_string
		
		# delete old task
		if('id' in arg):
			self.update_score(arg)
			
		# search if current task timeout
		entries = app.db.select('range', what="range_id, range_id_job, range_start, range_length", \
			where="LOCALTIMESTAMP - range_timestamp > interval '%s' " % (app.range_timeout), \
			order="range_timestamp", limit=1)
		
		temp = list(entries)
		# if timeout
		if(bool(temp) != False):
			id, length, task, charset, salt, start = self.recycling(temp[0])
		else:
			id, length, task, charset, salt, start = self.craft()
		
		# render xml response
		web.header('Content-Type', 'text/xml')
		
		response = "<range>\
			<id>%s</id>\
			<length>%s</length>\
			<task>%s</task>\
			<charset>%s</charset>\
			<salt>%s</salt>\
			<start>\"%s\"</start>\
			</range>" % (id, length, task, charset, salt, start)
		
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
		ret = client.check_credential(["x"], "cookie")
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

# Pause a given job
# arg
#	id : job's id
#
class PauseJob:
	def GET(self):
		arg = web.input()
		
		# check credential (session)
		ret = client.check_credential(["w"], "cookie")
		if(ret == None):
			return app.debug_string
		
		# do not pause job already done
		entries = app.db.select('job', what="job_status", where="job_id=$id", vars={'id':arg['id']})
		
		temp = list(entries)
		
		if(bool(temp) == False):
			return app.debug_string
			
		j = temp[0]	
			
		if(j.job_status == "done"):
			return app.debug_string
		
		app.db.update('job', job_status="paused", where="job_id=$id", vars={'id':arg['id']})
		
		return "pausejob"

# Unpause a given job
# arg
#	id : job's id
#
class UnpauseJob:
	def GET(self):
		arg = web.input()
		
		# check credential (session)
		ret = client.check_credential(["w"], "cookie")
		if(ret == None):
			return app.debug_string
		
		app.db.update('job', job_status="fresh", where="job_id=$id", vars={'id':arg['id']})
		
		return "unpausejob"
		
#
# Show job or one job and all related range
# arg
#	(optionnal) id : id of a job
#		
class ShowJob:
	def GET(self):
		arg = web.input()
		
		# check credential (session)
		ret = client.check_credential(["r"], "cookie")
		if(ret == None):
			return app.debug_string
		
		if('id' not in arg):
			# select everything
			entries = app.db.select('job', what="*", order="job_status")
			
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
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		