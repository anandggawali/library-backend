from pymongo import MongoClient

client = MongoClient("mongodb+srv://anand_11:anand@cluster0.k9fsamf.mongodb.net/?appName=Cluster0")

db = client["library_db"]

# Login users (signup/login accounts)
users = db["users"]

# Library members registered by admin (separate table)
members = db["members"]

# Books
books = db["books"]

# Records/Transactions
records = db["records"]
