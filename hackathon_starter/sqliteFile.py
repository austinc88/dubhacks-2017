#import sqlite3
import json
from hackathon.models import Ingredients

db = sqlite3.connect('data/data.json')

cursor = db.cursor()

cursor.execute('CREATE TABLE food (id INTEGER PRIMARY KEY, foodName TEXT, calories INTEGER')

db.commit()

"""data_file = 'data.json'    # name of the sqlite database file
table_name1 = 'food'  # name of the table to be created
#table_name2 = 'my_table_2'  # name of the table to be created
new_field1 = 'foodName' # name of the column
new_field2 = 'calories'
new_field3 = 'amount'
field_type1 = 'STRING'  # column data type
field_type2 = 'INTEGER'
field_type3 = 'INTEGER'"""


# Connecting to the database file
#conn = sqlite3.connect(data_file)
#c = conn.cursor()
with open('data/data.json') as data_file:  
	jsonStr = data.decode("utf-8")  
	data = json.loads(data_file.read())
for food_name,calories in data:
	print("food_name: " + food_name)
	cur = Ingredients(ingredient=food_name, calories=calories)
	cur.save()

# Creating a new SQLite table with 1 column
#c.execute('CREATE TABLE {tn} ({nf1} {ft1}) ({nf2} {ft2}) ({nf3} {nf3})'\
  #      .format(tn=table_name1, nf1=new_field1, ft1=field_type1, nf2=new_field2, ft2=field_type2, nf3=new_field3, ft3=field_type3))

# Creating a second table with 1 column and set it as PRIMARY KEY
# note that PRIMARY KEY column must consist of unique values!
#c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
#        .format(tn=table_name2, nf=new_field, ft=field_type))

# Committing changes and closing the connection to the database file
#conn.commit()
#conn.close()