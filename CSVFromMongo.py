import csv
import pymongo

connection = pymongo.MongoClient('localhost', 27017)
database = connection['mydb_01']
collection = database['addresses']


addresses = collection.find({})
with open('test.csv', 'w', newline='') as file:
	writer = csv.writer(file)
	#writer.writerow(["Address", "Received", "Spent", "Num_Transactions", "Num_transactions_in", "Num_Transactions_out",
	# "first_transaction_in_timestamp", "last_transaction_timestamp", "average_transactions_per_day", "mean_inputs",
	# "mean_outputs", "mean_transaction_value_in", "mean_transaction_value_out", "num_coinbase_transactions"])
	for a in addresses:
		address = a["address"]
		received = a["received"]
		spent = a["spent"]
		num_transactions = a["num_transactions"]
		num_transactions_in = a["num_transactions_in"]
		num_transactions_out = a["num_transactions_out"]
		first_transaction_timestamp = a["first_transaction_in_timestamp"]
		last_transaction_timestamp = a["last_transaction_timestamp"]
		average_per_day = a["average_transactions_per_day"]
		mean_inputs = a["mean_inputs"]
		mean_outputs = a["mean_outputs"]
		mean_in_value = a["mean_transaction_value_in"]
		mean_out_value = a["mean_transaction_value_out"]
		num_coinbase = a["num_coinbase_transactions"]

		writer.writerow([str(address), 
			str(received), 
			str(spent), 
			str(num_transactions), 
			str(num_transactions_in), 
			str(num_transactions_out),
			str(first_transaction_timestamp),
			str(last_transaction_timestamp),
			str(average_per_day),
			str(mean_inputs),
			str(mean_outputs),
			str(mean_in_value),
			str(mean_out_value),
			str(num_coinbase)])

