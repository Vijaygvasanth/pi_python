#!/usr/bin/env python

import RPi.GPIO as GPIO
import SimpleMFRC522
import time
import json
import requests

entry = True
cart_id = ""
USER_RESOURCE="http://localhost:8080/users/"
CART_RESOURCE="http://localhost:8080/carts/"

headers = {'Content-type': 'application/json'}

rfid_user_map = { '553128273391': '1' }

def process_rfid(rfid):
	global entry,cart_id
	if(str(rfid) == '553128273391'):
		user_id = rfid_user_map[str(rfid)]
                cart_req = {}
                cart_req['userId'] = user_id
                cart_req_js = json.dumps(cart_req)

		if(entry):
			entry = False
			user_uri = USER_RESOURCE+user_id
			response = requests.get(url = user_uri)
			user_data = response.json()
			user_name = user_data['name']
			user_balance =  int(user_data['balance'])
			balance_full = str(user_balance/100)
			balance_dec = str(user_balance%100)
			if(len(balance_dec) == 1):
				balance_dec+= '0'
			print "Welcome " + str(user_name) + "!! Your current wallet balance is: " + str(balance_full) + "." + str(balance_dec)
			response = requests.post(url = CART_RESOURCE, data = cart_req_js, headers=headers)
			cart_data = response.json()
			print cart_data
			cart_id = str(cart_data['id'])
		else:
			print "Exit"
			response = requests.post(url = CART_RESOURCE, data = cart_req_js, headers=headers)
			print response.status_code
	else:
		if(len(cart_id) == 0):
			print "User not logged in"
		else:
			print "Adding product:"+str(rfid)
			cart_item_req = {}
			cart_item_req['rfid'] = rfid
			cart_item_req_js = json.dumps(cart_item_req)
			cart_uri = CART_RESOURCE + cart_id
			print cart_uri
			response = requests.post(url = cart_uri, data = cart_item_req_js, headers=headers)
			print(response.status_code)
			

reader = SimpleMFRC522.SimpleMFRC522()

try:
	while 1==1:
        	id, text = reader.read()
		process_rfid(id)
		time.sleep(5)
finally:
        GPIO.cleanup()

