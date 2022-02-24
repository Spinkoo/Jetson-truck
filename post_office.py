from threading import Thread
import queue
from time import sleep
import os
import json
import requests
from datetime import datetime
from glob import glob

URL = "https://truck-staging.ew.r.appspot.com/collection/"
TRUCK_TOKEN = "AJ2Rx5RN5FPG5QEjKMyw"
class office(object):
	"""docstring for office"""
	def __init__(self, ):
		self.queue = queue.Queue()
		self.work = True
		self.TRUCK_TOKEN =  self.get_TRUCK_TOKEN()
		self.init_collection()

		self.thread = Thread(target=self.send_loop, daemon=True)
		self.thread.start()


	def get_TRUCK_TOKEN(self):
		return TRUCK_TOKEN

	def init_collection(self):
		self.COLLECTION_TOKEN = get_token()

	def check_untreated_data(self):
		return len(glob('data/*.json'))>0

	def send_remaining_data(self):
		data = glob('data/*.json')
		for d in data:
                	try:
                	    self.send_request(d)
                	except:
                	    continue

	def send_request(self, json_path):
		try:
			print(json_path)
			with open(json_path) as json_file:
				data = json.load(json_file)
		except:
			print('File not found')
			return
		fpath, save_time, lon, lat = data['fpath'], data['time_stamp'], data['longitude'], data['latitude']

		try:

			if int(lat) == 0:
				lat = "-69.6969"
			if int(lon) == 0:
				lon = "-69.6969"
			r = requests.post(
		        f"{URL}{self.COLLECTION_TOKEN}/batch",
		        headers={'Token': f"{self.TRUCK_TOKEN}"},
		        files={
		            'image': open(fpath, 'rb'),
		        },
		        data={ 
		            'timestamp': save_time,
		            "longitude": lon,
		            "latitude" : lat
		        	 }
		    )
			resp = r.text
			
			if "imageURL" in resp:
				os.remove(json_path)
				os.remove(fpath)
				
		except requests.exceptions.ConnectionError: # no internet connection
		    print("batch not sent")
		except requests.exceptions.RequestException as e:  # This is the correct syntax
			print(e)


	def send_loop(self):
		while self.work or ( not self.work and self.queue.qsize() > 0):
			if self.COLLECTION_TOKEN is None :
				self.init_collection()
				continue
			if self.check_untreated_data():
				self.send_remaining_data()
			json_path = self.queue.get()
			try:
			   self.send_request(json_path)
			except :
			   continue
			

	def push_data(self, data):
		self.queue.put(data)

def create_token() :

	try:
	    r = requests.post(
	        URL,
	        headers={'Token': TRUCK_TOKEN},
	        json={
	            "startAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	        }
	    )
	    data = json.loads(r.text)
	    return data['ID']
	except requests.exceptions.ConnectionError: # no internet connection
	    print("collection not created")
	    return None

def get_token():

	if os.path.exists('./connection_token.txt'):
		f = open('./connection_token.txt', 'r')
		token = f.read()
		return token
	else:
		token = create_token()
		if token is None :
			return None
		f = open('./connection_token.txt', 'w')
		f.write(token)
		f.close()
		return token
