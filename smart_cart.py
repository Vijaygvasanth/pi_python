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

def price_to_str(price):
	price_full = str(price/100)
	price_dec = str(price%100)
	if(len(price_dec) ==1):
		price_dec+='0'
	return price_full + "." + price_dec

def show_bill_summary(user_id):
	cart_uri = CART_RESOURCE + cart_id
	response = requests.get(url = cart_uri)
	cart_item_data = response.json()
	print cart_item_data
	if(len(cart_item_data) > 0):
		print "------------------------------------------------------------------------------------------------"
		print "						Your Bill Summary				"
		print "------------------------------------------------------------------------------------------------"
		print "   Item					Unit Price		Qty		Price	  "
		print "------------------------------------------------------------------------------------------------"
		total_amt = 0
		for i in range(len(cart_item_data)):
			cart_item_name = cart_item_data[i]['item']['name']
			cart_item_unit_price = cart_item_data[i]['item']['price']
			cart_item_qty = cart_item_data[i]['quantity']
			cart_item_price = cart_item_unit_price * cart_item_qty
			total_amt += cart_item_price
			print "  " + cart_item_name + " 				" + price_to_str(cart_item_unit_price) + "			" + str(cart_item_qty) + "		" + price_to_str(cart_item_price) 
		print "-------------------------------------------------------------------------------------------------"
		print " 								Total Amount: " + price_to_str(total_amt)
		print "-------------------------------------------------------------------------------------------------"
		print ""
		print ""
		print "		Bill Amount: "+ price_to_str(total_amt) + " is detected from your Wallet."

                cart_req = {}
                cart_req['userId'] = user_id
                cart_req_js = json.dumps(cart_req)
		user_uri = USER_RESOURCE+user_id
		response = requests.get(url = user_uri)
		user_data = response.json()
		user_balance = user_data['balance']
		print "		Your current wallet balance is:" + price_to_str(user_balance)
			

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
			show_bill_summary(user_id)
			response = requests.post(url = CART_RESOURCE, data = cart_req_js, headers=headers)
			print response.status_code
			entry = True
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
			if('itemId' in response.text):
				cart_item_data = response.json()
				cart_item_name = cart_item_data['item']['name']
				cart_item_price = int(cart_item_data['item']['price'])
				cart_item_quantity = cart_item_data['quantity']
				item_price_full = str(cart_item_price/100)
				item_price_dec = str(cart_item_price%100)
				if(len(item_price_dec) == 1):
					item_price_dec+='0'
				print "Item "+ cart_item_name + " added to your cart, Quantity: " + str(cart_item_quantity) + " Price: " + item_price_full + "." + item_price_dec
			else:
				print "Item removed"
			print(response.status_code)
			

reader = SimpleMFRC522.SimpleMFRC522()

try:
	while 1==1:
        	id, text = reader.read()
		process_rfid(id)
		time.sleep(3)
finally:
        GPIO.cleanup()

