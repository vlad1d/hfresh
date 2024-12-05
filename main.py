"""Main module for loading recipes from a JSON file and determining the difficulty of chili recipes."""

import json
import sqlite3
import re
import os
import pandas as pd
from fuzzywuzzy import fuzz

def getTime(time: str) -> int:
    """
    Convert a given time string of the form PT#H#M to minutes.

    Args:
        time (str): The time string to convert
    
    Returns:
        int: The time in minutes
    """
    result = 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', time)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        result = hours * 60 + minutes
    return result

def getDifficulty(prepTime: str, cookTime: str) -> str:
    """
    Determine the difficulty of a recipe based on the sum of the prep and cook times.
    
    Args: 
        prepTime (str): The prep time of the recipe
        cookTime (str): The cook time of the recipe
    
    Returns:
        str: The difficulty of the recipe
    """
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
    """
    Read a JSON file and return the contents as a list.

    Args:
        path (str): The path to the JSON file
    
    Returns:
        list: The contents of the JSON file
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(path, 'r', encoding="utf8") as file:
        fileContent = file.read()
        fileContent = fileContent.replace('}\n{', '},{')
        fileContent = f"[{fileContent}]"
        return json.loads(fileContent)

def setupRecipes(connection: sqlite3.Connection):
    """
    Set up the recipes table in the database by creating it if it doesn't exist with the required columns.

    Args:
        connection (sqlite3.Connection): The connection to the database
    """
    cursor = connection.cursor()
    try:
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
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to create table: {e}")

def addRecipe(cursor: sqlite3.Cursor, name: str, ingredients: str, url: str, image: str, cookTime: str, recipeYield: str, datePublished: str, prepTime: str, description: str):
    """
    Add a recipe to the database.
    
    Args:
        cursor (sqlite3.Cursor): The cursor to the database
        name (str): The name of the recipe
        ingredients (str): The ingredients of the recipe
        url (str): The URL of the recipe
        image (str): The image of the recipe
        cookTime (str): The cook time of the recipe
        recipeYield (str): The recipe yield
        datePublished (str): The date the recipe was published
        prepTime (str): The prep time of the recipe
        description (str): The description of the recipe
    """
    try:
        cursor.execute('''
            INSERT INTO recipes (name , ingredients, url, image, cookTime, recipeYield, datePublished, prepTime, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, ingredients, url, image, cookTime, recipeYield, datePublished, prepTime, description
        ))
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to add recipe: {e}")

def loadRecipes(connection: sqlite3.Connection, recipes: list):
    """
    Load a list of recipes into the database.

    Args:
        connection (sqlite3.Connection): The connection to the database
        recipes (list): The list of recipes to load
    """
    cursor = connection.cursor()
    for recipe in recipes:
        addRecipe( cursor, recipe['name'], recipe['ingredients'], recipe['url'], recipe['image'], recipe['cookTime'], recipe['recipeYield'], recipe['datePublished'], recipe['prepTime'], recipe['description'])
    connection.commit()

def updateDifficulty(connection: sqlite3.Connection, recipes: list):
    """
    Update the difficulty of chili recipes in the database by adding a difficulty column and updating the difficulty of each recipe.

    Args:
        connection (sqlite3.Connection): The connection to the database
        recipes (list): The list of chili recipes
    """
    cursor = connection.cursor()
    try:
        cursor.execute('''
            ALTER TABLE recipes
            ADD COLUMN difficulty TEXT
        ''')
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to add column: {e}")

    for recipe in recipes:
        try:
            cursor.execute('''
                UPDATE recipes
                SET difficulty = ?
                WHERE name = ?
            ''', (recipe['difficulty'], recipe['name']))
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to update difficulty: {e}")
    connection.commit()

def write_to_csv(recipes: list):
    """
    Write a list of recipes to a CSV file.

    Args:
        recipes (list): The list of recipes to write
    """
    try:
        df = pd.DataFrame(recipes)
        df.to_csv('recipes.csv', index=False)
    except Exception as e:
        raise RuntimeError(f"Failed to write to CSV: {e}")

def main():
    """Load recipes from a JSON file and determine the difficulty of chili recipes."""
    try:
        connection = sqlite3.connect('recipes.db')
    except Exception as e:
        raise RuntimeError(f"Failed to connect to database: {e}")

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
    dbPath = 'recipes.db'
    if os.path.exists(dbPath):
        os.remove(dbPath)

if __name__ == '__main__':
    main()