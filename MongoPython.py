## This file contains several functions that do the following: 
## 1) create a collection in mongodb for bitcoin transactions
## 2) go through transaction outputs and find all addresses referenced, add to a new address collection
## 3) go through all addresses and find all associated incoming transactions, add them to the address collection
## 4) go through all transactions and find all "from-addresses" via inference of inputs and previous transaction hashes
## 5) create various time, frequency and input/output statistics for each address 
## this script assumes that you have a <transactions>.json file, which can be created by running bitcoinetl + full node 
## the main() function is at the bottom of this page

import pymongo
import json
import time

connection = pymongo.MongoClient('localhost', 27017)
database = connection['mydb_01']
collection = database['btc_transactions']
addresscollection = database['addresses']
filename = "transactionsMedium.json"

# write transactions into mongodb, specified transaction file name, and how many transactions to add
def read_file_and_add_to_db(filename, num_transactions):
	print("Reading transaction file into database")
	i = 0
	with open(filename) as f:
		for line in f:
			if i <= num_transactions:
				i+=1
				trans = json.loads(line)
				collection.insert_one(trans)

def populate_address_collection():
	print("Creating address collection via dummy")
	addresscollection.insert_one({"address" : "148U9CQ7PMHNaQSgUAixZjEbpZEkTtNbyi"})

	results = collection.find({}, {"outputs.addresses":1, "_id":0})
	counter = 0
	double_counter = 0
	print("Walking through transaction outputs to find addresses")
	for r in results:
		for c in range(258):
			try:
				address = r["outputs"][c]["addresses"][0]
				counter +=1
				if addresscollection.find_one({"address" : address}) == None:
					diction = {"address" : address, "received" : 0, "spent": 0, "num_transactions" : 0, "num_transactions_in": 0, "num_transactions_out": 0, "first_transaction_in_timestamp": 0, "last_transaction_timestamp":0, "average_transactions_per_day": 0 ,"payback_ratio" : 0, "mean_inputs": 0, "mean_outputs": 0, "mean_transaction_value_in":0, "mean_transaction_value_out":0, "transaction_frequency": 0, "num_coinbase_transactions": 0, "transactions_in" : [], "transactions_out": []}
					addresscollection.insert_one(diction)
				else: 
					double_counter +=1
			except:
				pass
	print("Output addresses found: " + str(counter))
	print("Duplicate addresses found and avoided: " + str(double_counter))
	print("Deleting dummy value")
	addresscollection.delete_one({"address": "148U9CQ7PMHNaQSgUAixZjEbpZEkTtNbyi"})
	print("Creating Address Index")
	addresscollection.create_index([("address", pymongo.DESCENDING)])

#this function is depreciated, faster method below is approximately 10 times faster
def find_transactions_in_and_add():
	print("Finding incoming bitcoin transactions for each address")
	addresses = addresscollection.find({})
	counter = 0
	hashtag = ""
	for a in addresses:
		for i in range(258):
			try:
				transaction_in = collection.find_one({f'outputs.{i}.addresses.0' : a["address"]})
				if transaction_in != None: 
					addresscollection.update_one({"address": a['address']}, {"$push": {"transactions_in": transaction_in}})
					received = transaction_in["outputs"][i]["value"]
					addresscollection.update_one({"address": a['address']}, {"$inc" : {"received" : received}})
					addresscollection.update_one({"address": a['address']}, {"$inc" : {"num_transactions" : 1}})
					addresscollection.update_one({"address": a['address']}, {"$inc" : {"num_transactions_in" : 1}})
					break
			except:
				print("ERROR occued in between line 59 and 66")
		counter += 1
		if (counter%500 == 0):
			hashtag += "#"
			print(str(counter) + " Addresses checked! Progress: " + hashtag)

## new version of frind trabsactions in and add:
def find_transactions_in_and_add_faster():
	print("Finding incoming bitcoin transactions for each address")
	counter = 0
	hashtag = ""
	transactions = collection.find({})
	all_addresses = addresscollection.find({})
	for t in transactions:
		num_outputs = t["output_count"]
		counter +=1
		for o in range(num_outputs):
			output_address = t["outputs"][o]["addresses"][0]
			try:
				addr = addresscollection.find_one({"address" : output_address})
				if addr != None:
					addresscollection.update_one({"address" : output_address}, {"$push": {"transactions_in": t}})
			except:
				pass
			try: 
				received = t["outputs"][o]["value"]
				addresscollection.update_one({"address": output_address}, {"$inc" : {"received" : received}})
				addresscollection.update_one({"address": output_address}, {"$inc" : {"num_transactions" : 1}})
				addresscollection.update_one({"address": output_address}, {"$inc" : {"num_transactions_in" : 1}})
			except: 
				print("addig in the other stuff didn't work")
			try:
				if t["is_coinbase"] == True: 
					addresscollection.update_one({"address": output_address}, {"$inc" : {"num_coinbase_transactions" : 1}})
			except:
				print("is coinbase failed")
				pass

		if (counter%1000 ==0):
			hashtag += "#"
			print(str(counter) + " Tranactions checked! Progress: " + hashtag)
			

def find_from_addresses():
	print("Finding outgoing bitcoin addresses from previous transaction outputs")

	transactions = collection.find({})
	counter = 0

	for t in transactions:
		string = "Transaction: "
		try:
			input_count = t["input_count"]
			for i in range(input_count):
				spent_transaction_hash = t["inputs"][i]["spent_transaction_hash"]
				spent_output_index = t["inputs"][i]["spent_output_index"]
				string += f" input {i}: " + " Spent Transaction Hash: " + spent_transaction_hash + " spent_output_index: " + str(spent_output_index)
				spent_transaction = collection.find_one({"hash": spent_transaction_hash})
				from_address = spent_transaction["outputs"][spent_output_index]["addresses"][0]
				string += " FROM ADDRESS: " + from_address
				
				try:
					addresscollection.update_one({"address": from_address}, {"$push": {"transactions_out": t}})
					#print(string)
					counter += 1
				except:
					print("cound not add transaction " + t["hash"] + " for some reason")
					pass
				try:
					addresscollection.update_one({"address": from_address}, {"$inc": {"num_transactions" : 1}})
				except:
					print("update num transaction fail")
					pass
				try:
					addresscollection.update_one({"address": from_address}, {"$inc": {"num_transactions_out" : 1}})
				except:
					print("update num transactions out fail")
					pass
				try:
					spent = spent_transaction["outputs"][spent_output_index]["value"]
					addresscollection.update_one({"address": from_address}, {"$inc": {"spent" : spent}})
				except:
					print("update spent fail")
					pass

		except: 
			pass
	print("Total 'from-addresses' added: " + str(counter))

# find first transaction in timestamp
def find_time_metrics():
	print("finding time based metrics for addresses")
	all_addresses = addresscollection.find({})

	for a in all_addresses:
		timestamp = 0
		all_timestamps = []

		# first and last timestamps:
		for i in range(a["num_transactions_in"]):
			try:
				t_time = a["transactions_in"][i]["block_timestamp"]
				all_timestamps.append(t_time)
			except:
				pass

		if a["num_transactions_out"] > 0:
			for o in range(a["num_transactions_out"]):
				try:
					o_time = a["transactions_out"][o]["block_timestamp"]
					all_timestamps.append(o_time)
				except: 
					pass

		first_timestamp = min(all_timestamps)
		last_timestamp = max(all_timestamps)
		addresscollection.update_one({"address": a["address"]}, {"$inc" : {"first_transaction_in_timestamp" : first_timestamp}})
		addresscollection.update_one({"address": a["address"]}, {"$inc": {"last_transaction_timestamp" : last_timestamp}})
		
		diff = last_timestamp - first_timestamp
		if diff > 0:
			frequency_seconds = diff / a["num_transactions"]
			frequency = frequency_seconds % 86400
			addresscollection.update_one({"address": a["address"]}, {"$inc": {"average_transactions_per_day" : frequency}})

# mean value of number of inputs and outpus
def find_mean_values():
	print("finding mean values of inputs and outputs")
	all_addresses = addresscollection.find({"num_transactions_out": {"$gt" : 0}})

	for a in all_addresses:
		transactions_out = a["transactions_out"]
		total_num_inputs = 0
		total_num_outputs = 0 
		for t in transactions_out:
			total_num_inputs += t["input_count"]
			total_num_outputs += t["output_count"]
		mean_inputs = total_num_inputs / a["num_transactions_out"]
		mean_outputs = total_num_outputs / a["num_transactions_out"]
		addresscollection.update_one({"address": a["address"]}, {"$inc": {"mean_inputs" : mean_inputs}})
		addresscollection.update_one({"address": a["address"]}, {"$inc": {"mean_outputs" : mean_outputs}})


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#-----------------------------------------------------#
#######################################################
########## COMPLETE SCRIPT EXECUTION: #################

def main():
	time1 = time.time()
	read_file_and_add_to_db(filename, 500)
	populate_address_collection()
	find_transactions_in_and_add_faster()
	find_from_addresses()
	find_time_metrics()
	find_mean_values()

	time2 = time.time()
	print("Total Program Time: " + str(time2 - time1))


if __name__ == '__main__':
	main()

# 30,000 transactions take about 36 minutes to process
#-----------------------------------------------------#
#########------------------------------------##########
####################--------------#####################
#######################################################