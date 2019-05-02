# Soapcalc
This little Python script is used to generate soap recipes based on desired properties and different ingredient's properties. The basic idea here is to generate a random recipe first, calculate its properties and then the deviation from the desired ones. Then try to optimize the recipe.

## How to use
#### 1) Install the requirements
`pip3 install -r requirements.txt`
#### 2) Modify the `ingredients.json` file with the properties you want
#### 3) Run the program
`python3 soapcalc.py [-g] [-i <increment>] [-l <loops>] [-e <ingredient>,...] [-v]`

e.g. 
`python3 soapcalc.py -g -i 0.001 -l 1000 -e palm_oil,ricebran_oil,argan_oil,kukui_nut_oil,grapeseed_oil,babassu_oil,avocado_oil`