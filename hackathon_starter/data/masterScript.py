import csv
import json

foodObj = {}

nutritionObj = {}

data = {}
with open('food.csv', 'rb') as csvfile:
    foodReader = csv.reader(csvfile, delimiter=',', quotechar='\"')
    for row in foodReader:
        if row[4] != 'FoodDescription':
            ingredient = row[4]
            foodId = row[0]
            foodObj[foodId] = ingredient

with open('nutrient.csv', 'rb') as csvfile:
    foodReader = csv.reader(csvfile, delimiter=',', quotechar='\"')
    for row in foodReader:
        if row[2] != 'NutrientValue':
            foodId = row[0]
            nutrientValue = float(row[2])/100
            if row[1] == '208':
                nutritionObj[foodId] = nutrientValue


for key in foodObj :
    calories = nutritionObj[key]
    if calories :
        description = foodObj[key]
        nutrition = str(nutritionObj[key])
        data[description] = nutrition

for key in data:
    print "Food is " + key + ", calories per gram is " + str(data[key])

with open('data.json', 'w') as outfile:
    json.dump(unicode(data), outfile)
