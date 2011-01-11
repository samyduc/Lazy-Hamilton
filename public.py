import app

class Stats:
	def GET(self):
		# no credential here
		entries = app.db.select('client', \
				what="client_nickname, client_time, client_cpu", where="client_time <> 0", order="client_time DESC")
		
		return app.render.stats(entries)