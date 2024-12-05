# Hello Fresh Internship Assessment

## Description
This repository contains my solution for the Hello Fresh Internship Assessment. The task was to create a simple Python script that extracts chili recipes from a json file and calculates the difficulty of each recipe. The <b>fresh</b>-ly (pun intended) modified data must be stored in a csv file.

## Prerequisites
- Python 3.13
- requirements.txt

All third-party modules are listed in the `requirements.txt` file. To install them, run the following command:
```bash
pip3 install -r recipes-etl/requirements.txt
```

## Running the Application
<span style="color:red;">Important:</span>  The code reads data from a file named ``recipes.json``, placed in the repository root. That is, the json file must be placed outside the `recipes-etl` directory.

```bash
cd recipes-etl
python3 main.py
```
The code will run and produce a csv file with the modified data.

## Functionality

### Requirements
- [x] Reading the recipes:

The program reads the recipes from the `recipes.json` file. Then, it creates an SQL table where the data is stored for easier access & manipulation.

- [x] Extracting every recipe that has the word "Chilies":

The program extracts all recipes that contain the word "Chilies" in their ingredient list by using the fuzzywuzzy library. This checks the similarity between the word "Chilies" and the ingredients in the recipe. If the similarity is above a certain threshold, the recipe is considered to contain chilies. This is so that the program can account for different spellings/grammar mistakes of the word "Chilies". We also check for similarities with the word "Chili" to account for the singular form of the word.

- [x] Calculating the difficulty of each recipe:

The difficulty of each recipe is calculated, as instructed, by adding the prepTime and cookTime values. These are, initially, strings, in a different format so they are converted to "minute" integers. This is okay (with minimal risk of overflow) as recipes are not expected to have values in the order of thousands. The difficulty is then calculated by adding the two values. This is then stored in the SQL table.

- [x] Writing the modified data to a csv file:

The pandas library allows for easy writing of the SQL table to a csv file. The data is written to a file named `recipes.csv`. The file is created in the same directory as the script. The validity of the data was checked by opening the file in a csv reader.

- [x] Cleaning up:

After the data is written, the connection is closed and the SQL table is dropped. This is done to ensure that the program does not leave any unnecessary data behind.


### Further Improvements
The program could be improved by adding more features such as:
- [ ] Nutritional information. The program could include nutritional information for each recipe based on the ingredients used.
- [ ] More detailed difficulty calculation, based on more factors such as the number of ingredients, etc.
- [ ] Any additional data manipulation. The use of a SQL table allows for easy access to the data and further manipulation.

## Contact
    Vlad Ichim | 0681097927 | vladichim17@yahoo.ro
