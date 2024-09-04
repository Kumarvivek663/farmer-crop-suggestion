from pymongo import MongoClient 
connection_string = "mongodb+srv://aryavivek663:YfP2nAyqnioJcOCh@farmer.cxfu5.mongodb.net/?retryWrites=true&w=majority&appName=farmer"
client = MongoClient(connection_string)
database = client['Farmer2']
collection = database['FarmerData1']

documents = collection.find()  # select * from table;
for document in documents: 
    print(document) 
print("thank you!") 

# execute this file to fectch your data from database 