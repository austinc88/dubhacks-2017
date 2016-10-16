import csv
import json

foodObj = {}

nutritionObj = {}

data = {}
with open('food.csv', 'rb') as csvfile:
    foodReader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in foodReader:
        if row[4] != 'FoodDescription':
            ingredient = row[4]
            foodId = row[0]
            foodObj[foodId] = ingredient

with open('nutrient.csv', 'rb') as csvfile:
    foodReader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in foodReader:
        if row[2] != 'NutrientValue':
            foodId = row[0]
            nutrientValue = float(row[2])/100
            if row[1] == '208':
                nutritionObj[foodId] = nutrientValue

counter = 1
for key in foodObj :
    calories = nutritionObj[key]
    if calories :
        model = {
            "model" : "hackathon.Ingredients",
            "pk" : counter,
            "fields" : {

            }
        }
        description = foodObj[key]
        nutrition = str(nutritionObj[key])
        model["fields"]["ingredient"] = description
        model["fields"]["calories"] = nutrition
        model["fields"]["amount"] = 1
        data[str(counter)] = model
        counter = counter + 1
        print(model)


# for key in data:
#     print "Food is " + key + ", calories per gram is " + str(data[key])

with open('data.json', 'w') as outfile:
    json.dump(unicode(data), outfile)
