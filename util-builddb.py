# -*- coding: utf-8 -*-
# TAD courtesy
# Samy Duc
# build db (sql 3 compliant)
# attented to be used with sqlite3
import sqlite3
import hashlib
import random

# schema description
# job
# job_id : unique id
# job_maxclient : max number of client for this job
# job_client : current number of client working on this job
# job_task : task (scripts, name)
# job_status : current status of the job (over, pending, result wrote here)
# job_descriptor : description of the job
#
schema_job = "CREATE TABLE job(\
	job_id INTEGER,\
	job_maxclient INTEGER,\
	job_client INTEGER,\
	job_task TEXT NOT NULL,\
	job_status TEXT,\
	job_descriptor TEXT,\
	PRIMARY KEY(job_id)\
	);"
	
# schema description
# client
# client_id : unique id
# client_nickname : personnal nickanme for easy identification
# client_password : password is stored as : SHA256( SHA256(clear password) + SALT)
# client_salt : salt is a 3 random characters string
# client_credential : rwx format
# client_time : total cpu time given to the project
# client_email : optionnal email for contact
# client_cpu : current cpu power available from the client ->
#	number of 2 md5 computation with one comparison per second
# client_cookie : cookie used for authentication
schema_client = "CREATE TABLE client(\
	client_id INTEGER,\
	client_nickname VARCHAR(32) NOT NULL,\
	client_password CHAR(64) NOT NULL,\
	client_salt VARCHAR(3) NOT NULL,\
	client_credential VARCHAR(3) NOT NULL,\
	client_time INTEGER,\
	client_email VARCHAR(40),\
	client_cpu FLOAT,\
	client_cookie CHAR(64),\
	PRIMARY KEY(client_id)\
	);"

# schema description
# range
# range_id : unique identifier
# range_id_job : job linked with this range
# range_id_client : client linked with this range
# range_start : starting point
# range_length : length / duration / size of the range
# range_timestamp : timestamp of the range
schema_range = "CREATE TABLE range(\
	range_id INTEGER,\
	range_id_job INTEGER NOT NULL,\
	range_id_client INTEGER NOT NULL,\
	range_start TEXT,\
	range_length INTEGER,\
	range_timestamp TIMESTAMP,\
	PRIMARY KEY(range_id),\
	FOREIGN KEY(range_id_job) REFERENCES job(job_id),\
	FOREIGN KEY(range_id_client) REFERENCES client(client_id)\
	);"
	
def generate_salt():
	salt_charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
	salt = ""
	# pick 3 random characters from charset
	salt += random.choice(salt_charset)
	salt += random.choice(salt_charset)
	salt += random.choice(salt_charset)
	return salt
	
def build_password(password):
	salt = generate_salt()
	a = hashlib.sha256(password).hexdigest()
	b = hashlib.sha256(a + salt).hexdigest()
	return b, salt
	
def build_req_default_admin():
	hash_password, salt = build_password("kikoolol")
	
	req_default_admin = "INSERT INTO client(\
		client_nickname, client_password, client_salt,\
		client_credential\
		) VALUES(\
		'admin', '" + hash_password + "', '"+salt +\
		"', 'rwx'\
		);"
	return req_default_admin
	
if __name__ == "__main__":
	# create database 
	conn = sqlite3.connect('./db.sqlite3')
	c = conn.cursor()
	
	# create schema
	c.execute(schema_job)
	c.execute(schema_client)
	c.execute(schema_range)
	
	# create default admin
	c.execute(build_req_default_admin())
	print(build_req_default_admin())
	
	conn.commit()
	conn.close()
	