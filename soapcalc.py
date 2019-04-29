import math
import numpy as np
import json

quantities = {
    "olive_oil": 0,
    "palm_oil": 0,
    "lard": 0,
    "coconut_oil": 0,
    "castor_oil": 0,
    "avocado_oil": 0,
    "almond_oil": 0,
    "ricebran_oil": 0
}

desired_soap = {
    "hardness": 45,
    "cleansing": 18,
    "condition": 55,
    "bubbly": 25,
    "creamy": 30,
    "iodine": 55,
    "ins": 160,
    "price": 3
}

#Read JSON data into the ingredients dict
filename = 'ingredients.json'
if filename:
    with open(filename, 'r') as f:
        ingredients = json.loads(f.read())

increment = 0.001


def rms_error(soap):
    error = 0.0
    for property, value in soap.items():
        # Here I don't care about optimizing the price so I don't want it to have any impact on the error
        if property == "price":
            error = error
        else:
            error = error + (value - desired_soap[property]) ** 2

    return math.sqrt(error/len(desired_soap))


def largest_diff(soap, ingrs_to_remove):
    diff = 0.0
    prop = ""
    diffs = {}
    for property, value in soap.items():
        if property not in ingrs_to_remove:
            diffs.update({property: math.fabs((value - desired_soap[property]))})
            d = math.fabs((value - desired_soap[property]))
            if d > diff:
                diff = d
                prop = property
    #print("Diffs:", diffs)
    return prop, diff


def property_calc():
    resulting_soap = {"hardness": 0,"cleansing": 0,"condition": 0,"bubbly": 0,"creamy": 0,"iodine": 0,"ins": 0,"price": 0}
    for ingredient, properties in ingredients.items():
        for property, value in ingredients[ingredient].items():
            resulting_soap.update({property: resulting_soap[property] + (value * quantities[ingredient])})
    return resulting_soap


def find_ingredient_highest_lowest(property):
    high_value = 0.0
    high_ingr = ""
    low_value = 100
    low_ingr = ""
    for ingredient, properties in ingredients.items():
        if properties[property] > high_value:
            high_value = properties[property]
            high_ingr = ingredient
        if properties[property] < low_value:
            low_value = properties[property]
            low_ingr = ingredient

    return low_ingr, high_ingr

# Start with random proportions for each ingredient by using a Dirichlet distribution
quantity = np.random.dirichlet(np.ones(len(ingredients)),size=1).tolist()[0]
counter = 0
for q in quantities:
    quantities.update({q: quantity[counter]})
    counter = counter + 1

ingrs_to_remove = []

while True:
    # Calculate properties
    soap = property_calc()
    # Store RMS error value
    error = rms_error(soap)
    #print("RMS Error:", error)
    # Find the property with the largest differential
    ingr_largest_diff = largest_diff(soap, ingrs_to_remove)
    #print("Property with biggest differential:", ingr_largest_diff)
    # Find ingredients with the lowest and highest values for that property
    lowest_highest = find_ingredient_highest_lowest(ingr_largest_diff[0])
    #print("Ingredients with the lowest and highest values for that property:", lowest_highest)
    # Add and Subtract the quantities for those ingredients by the increment
    if (quantities[lowest_highest[0]] - increment) < 0:
        # If the quantity left for an ingredient is inferior to 0
        quantities.update({lowest_highest[1]: round(quantities[lowest_highest[1]] + quantities[lowest_highest[0]], 3)})
        quantities.update({lowest_highest[0]: 0})
        # Remove from ingredients list
        del ingredients[lowest_highest[0]]
    else:
        quantities.update({lowest_highest[0]: round(quantities[lowest_highest[0]] - increment, 3)})
        quantities.update({lowest_highest[1]: round(quantities[lowest_highest[1]] + increment, 3)})
    #print(quantities)
    # Recalculate properties and RMS error
    # If the RMS error is lower than the stored value, loop
    if(rms_error(property_calc()) >= error):
        # Try optimizing the next best diff property
        ingrs_to_remove.append(ingr_largest_diff[0])
        if len(ingrs_to_remove) == 6:
            break


# If the RMS error is higher than the stored value, stop and print quantities and resulting soap
print("Soap characteristics:", soap)
print("RMS Error:", rms_error(soap))
print("Soap recipe:", quantities)