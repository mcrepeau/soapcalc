import math
import numpy as np
import json
import matplotlib.pyplot as plt

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

#Read JSON data into the ingredients dict
ingredients_filename = 'ingredients.json'
if ingredients_filename:
    with open(ingredients_filename, 'r') as f:
        ingredients = json.loads(f.read())

#Read JSON data into the desired_soap dict
desired_soap_filename = 'desired_soap.json'
if desired_soap_filename:
    with open(desired_soap_filename, 'r') as f:
        desired_soap = json.loads(f.read())

increment = 0.001

def rms_error(soap):
    error = 0.0
    for property, value in soap.items():
        # Here I don't care about optimizing the price so I don't want it to have any impact on the error
        if property == "price":
            error = error
        else:
            error = error + (value - desired_soap[property]) ** 2

    return round(math.sqrt(error/len(desired_soap)), 6)


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
            resulting_soap.update({property: round(resulting_soap[property] + (value * quantities[ingredient]),2)})
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


def adjust_quantities(lowest_highest):
    if (quantities[lowest_highest[0]] - increment) < 0:
        # If the quantity left for an ingredient is inferior to 0
        quantities.update({lowest_highest[1]: round(quantities[lowest_highest[1]] + quantities[lowest_highest[0]], 3)})
        quantities.update({lowest_highest[0]: 0})
        # Remove from ingredients list
        del ingredients[lowest_highest[0]]
    else:
        quantities.update({lowest_highest[0]: round(quantities[lowest_highest[0]] - increment, 3)})
        quantities.update({lowest_highest[1]: round(quantities[lowest_highest[1]] + increment, 3)})


# Start with random proportions for each ingredient by using a Dirichlet distribution
quantity = np.round(np.random.dirichlet(np.ones(len(ingredients)),size=1),4).tolist()[0]
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
    adjust_quantities(lowest_highest)

    #print(quantities)

    # Recalculate properties and RMS error
    # If the RMS error is lower or equal to the stored value, loop
    if(rms_error(property_calc()) >= error):
        # Try optimizing the next best diff property
        ingrs_to_remove.append(ingr_largest_diff[0])
        if len(ingrs_to_remove) == 6:
            break


# If the RMS error is higher than the stored value, stop and print quantities and resulting soap
print("Soap characteristics:", soap)
print("RMS Error:", rms_error(soap))
print("Soap recipe:", quantities)

y1_pos = np.arange(len(quantities))

ax1 = plt.subplot(2,1,1)
plt.xticks(y1_pos, ingredients)
plt.ylabel('Quantity')
plt.xlabel('Ingredients')
plt.title('Cold-process soap recipe')
plt.grid(which='major', axis='y', linestyle=':', alpha=0.5, linewidth=1)
quantities_chart = plt.bar(y1_pos, quantities.values(), align='center', alpha=0.5)
for quantity in quantities_chart:
        height = quantity.get_height()
        ax1.text(quantity.get_x() + quantity.get_width()/2., 1.05*height,'%.1f%%' % float(height*100), ha='center', va='bottom')

y2_pos = np.arange(len(quantities))

ax2 = plt.subplot(2,1,2)
plt.xticks(y2_pos, soap)
plt.ylabel('Value')
plt.title('Soap characteristics')
plt.grid(which='major', axis='y', linestyle=':', alpha=0.5, linewidth=1)
plt.bar(y2_pos, soap.values(), align='center', alpha=0.5, color='g', label='Resulting soap')
plt.bar(y2_pos, desired_soap.values(), align='center', alpha=0.5, color='r', label='Desired soap')
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
plt.text(1, 1.1, "RMS Error: " + str(rms_error(soap)), transform=ax2.transAxes, ha='right', va='top', fontsize=8, bbox=props)

plt.legend()
plt.tight_layout()
plt.show()
