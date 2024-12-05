import json
import sqlite3
import re
import pandas as pd
from fuzzywuzzy import fuzz

def getTime(time: str) -> int:
    result = 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', time)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        result = hours * 60 + minutes
    return result

def getDifficulty(prepTime: str, cookTime: str) -> str:
    prepTime = getTime(prepTime)
    cookTime = getTime(cookTime)
    sum = prepTime + cookTime
    if sum < 30:
        return 'Easy'
    elif sum < 60:
        return 'Medium'
    else:
        return 'Hard'

def readJson(path: str) -> list:
    with open(path, 'r', encoding="utf8") as file:
        fileContent = file.read()
        fileContent = fileContent.replace('}\n{', '},{')
        fileContent = f"[{fileContent}]"
        return json.loads(fileContent)

def setupRecipes(connection: sqlite3.Connection):
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ingredients TEXT,
            url TEXT,
            image TEXT,
            cookTime TEXT,
            recipeYield TEXT,
            datePublished TEXT,
            prepTime TEXT,
            description TEXT
        )
    ''')

def addRecipe(cursor, name, ingredients, url, image, cookTime, recipeYield, datePublished, prepTime, description):
    cursor.execute('''
        INSERT INTO recipes (name , ingredients, url, image, cookTime, recipeYield, datePublished, prepTime, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name, ingredients, url, image, cookTime, recipeYield, datePublished, prepTime, description
    ))

def loadRecipes(connection: sqlite3.Connection, recipes: list):
    cursor = connection.cursor()
    for recipe in recipes:
        addRecipe( cursor, recipe['name'], recipe['ingredients'], recipe['url'], recipe['image'], recipe['cookTime'], recipe['recipeYield'], recipe['datePublished'], recipe['prepTime'], recipe['description'])
    connection.commit()

def updateDifficulty(connection: sqlite3.Connection, recipes: list):
    cursor = connection.cursor()
    cursor.execute('''
        ALTER TABLE recipes
        ADD COLUMN difficulty TEXT
    ''')

    for recipe in recipes:
        cursor.execute('''
            UPDATE recipes
            SET difficulty = ?
            WHERE name = ?
        ''', (recipe['difficulty'], recipe['name']))
    connection.commit()

def write_to_csv(recipes):
    df = pd.DataFrame(recipes)
    df.to_csv('recipes.csv', index=False)

def main():
    connection = sqlite3.connect('recipes.db')

    setupRecipes(connection)
    recipes = readJson('./recipes.json')
    loadRecipes(connection, recipes)

    chiliRecipes = []
    for recipe in recipes:
        ingredients = recipe['ingredients']
        if fuzz.partial_ratio('Chilies', ingredients) > 85 or fuzz.partial_ratio('Chili', ingredients) > 85:
                recipe['difficulty'] = getDifficulty(recipe['prepTime'], recipe['cookTime'])
                chiliRecipes.append(recipe)

    updateDifficulty(connection, chiliRecipes)
    write_to_csv(chiliRecipes)
    
    connection.close()

if __name__ == '__main__':
    main()