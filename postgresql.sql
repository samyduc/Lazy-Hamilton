-- TAD courtesy
-- Samy Duc
-- SQL script to build PostgreSQL database for Lazy-Hamilton
-- Warning PostgreSQL only compliant

-- schema description
-- job
-- job_id : unique id
-- job_maxclient : max number of client for this job
-- job_client : current number of client working on this job
-- job_name : name of the job
-- job_task : task (scripts, name)
-- job_status : current status of the job (over, pending, result wrote here)
-- job_descriptor : description of the job
--
CREATE TABLE job(
	job_id SERIAL,
	job_maxclient INTEGER,
	job_client INTEGER,
	job_name VARCHAR(32) NOT NULL,
	job_task TEXT NOT NULL,
	job_status TEXT,
	job_descriptor TEXT,
	PRIMARY KEY(job_id)
	);

-- schema description
-- client
-- client_id : unique id
-- client_nickname : personnal nickanme for easy identification
-- client_password : password is stored as : SHA256( SHA256(clear password) + SALT)
-- client_salt : salt is a 3 random characters string
-- client_credential : rwx format
-- client_time : total cpu time given to the project
-- client_email : optionnal email for contact
-- client_cpu : current cpu power available from the client
-- client_cookie : cookie used for authentication
CREATE TABLE client(
	client_id SERIAL,
	client_nickname VARCHAR(32) NOT NULL,
	client_password CHAR(64) NOT NULL,
	client_salt VARCHAR(3) NOT NULL,
	client_credential VARCHAR(3) NOT NULL,
	client_time INTEGER,
	client_email VARCHAR(40),
	client_cpu FLOAT,
	client_cookie CHAR(64),
	PRIMARY KEY(client_id)
	);

-- schema description
-- range
-- range_id : unique identifier
-- range_id_job : job linked with this range
-- range_id_client : client linked with this range
-- range_start : starting point
-- range_length : length / duration / size of the range
-- range_timestamp : timestamp of the range	
CREATE TABLE range(
	range_id SERIAL,
	range_id_job INTEGER NOT NULL,
	range_id_client INTEGER NOT NULL,
	range_start TEXT,
	range_length INTEGER,
	range_timestamp TIMESTAMP NOT NULL,
	PRIMARY KEY(range_id),
	FOREIGN KEY(range_id_job) REFERENCES job(job_id),
	FOREIGN KEY(range_id_client) REFERENCES client(client_id)
	);
	
-- create default admin
INSERT INTO client(client_nickname, client_password, client_salt, client_credential, client_time) 
	VALUES('admin', 
	'b827d91fe6effb0e5fe0f6a8d7e37df120e9f7c41ea971c7eb2ebdc892368b6d', 
	'wxJ', 
	'rwx',
	0);