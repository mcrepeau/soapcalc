import math
import numpy as np
import json
import matplotlib.pyplot as plt
import getopt
import sys
from tqdm import tqdm

verbose = False


def rms_error(soap, desired_soap):
    error = 0.0
    for property, value in soap.items():
        error = error + ((value - desired_soap[property]) ** 2)

    return round(math.sqrt(error/len(desired_soap)), 6)


def largest_diff(soap, props_to_ignore, desired_soap):
    diff = 0.0
    prop = ""
    debug_print("Properties to ignore:" + str(props_to_ignore))
    for property, value in soap.items():
        if property not in props_to_ignore:
            d = math.fabs((value - desired_soap[property]))
            if d > diff:
                diff = d
                prop = property
    return prop, diff


def property_calc(ingredients, quantities):
    resulting_soap = {"hardness": 0, "cleansing": 0, "condition": 0, "bubbly": 0, "creamy": 0, "iodine": 0, "ins": 0,
                      "price": 0}
    for ingredient, properties in ingredients.items():
        for property, value in ingredients[ingredient].items():
            resulting_soap.update({property: round(resulting_soap[property] + (value * quantities[ingredient]),2)})

    return resulting_soap


def find_ingredient_highest_lowest(property, ingredients):
    high_value = 0.0
    high_ingr = ""
    low_value = 100
    low_ingr = ""
    for ingredient, properties in ingredients.items():
        if properties[property] >= high_value:
            high_value = properties[property]
            high_ingr = ingredient
        if properties[property] <= low_value:
            low_value = properties[property]
            low_ingr = ingredient

    return low_ingr, high_ingr


def adjust_recipe(ingredients, prop_largest_diff, quantities, increment):
    # Find ingredients with the lowest and highest values for that property
    lowest_highest = find_ingredient_highest_lowest(prop_largest_diff, ingredients)

    debug_print("Ingredients with the lowest and highest values for that property:" + str(lowest_highest))

    # Add and Subtract the quantities for those ingredients by the increment
    if (quantities[lowest_highest[0]] - increment) < 0:
        # If the quantity left for an ingredient is inferior to 0
        quantities.update({lowest_highest[1]: round(quantities[lowest_highest[1]] + quantities[lowest_highest[0]], 3)})
        quantities.update({lowest_highest[0]: 0})
        # Remove from ingredients list
        debug_print("Removing ingredient:" + str(lowest_highest[0]))
        del ingredients[lowest_highest[0]]
    else:
        quantities.update({lowest_highest[0]: round(quantities[lowest_highest[0]] - increment, 3)})
        quantities.update({lowest_highest[1]: round(quantities[lowest_highest[1]] + increment, 3)})

    return quantities


def debug_print(debug):
    if verbose:
        print(debug)


def main():
    increment = 0.001
    loops = 100
    excluded_ingrs = []
    enable_graphs = False
    global verbose
    max_price = 3

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hgi:l:e:v", ["graphs", "increment=", "loops=", "excl_ingredients="])
    except getopt.GetoptError:
        print("python3 [-g] [-i <increment>] [-l <loops>] [-e <ingredient>,...] [-v]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("python3 [-g] [-i <increment>] [-l <loops>] [-e <ingredient>,...] [-v]")
            sys.exit()
        elif opt in ("-g", "--graphs"):
            enable_graphs = True
        elif opt in ("-i", "--increment"):
            increment = float(arg)
        elif opt in ("-l", "--loops"):
            loops = int(arg)
        elif opt in ("-e", "--excl_ingredients"):
            excluded_ingrs = arg.split(',')
        elif opt in ("-v", "--verbose"):
            verbose = True

    # Read JSON data into the desired_soap dict
    desired_soap_filename = 'desired_soap.json'
    if desired_soap_filename:
        with open(desired_soap_filename, 'r') as f:
            desired_soap = json.loads(f.read())

    # Read JSON data into the ingredients dict
    ingredients_filename = 'ingredients.json'
    if ingredients_filename:
        with open(ingredients_filename, 'r') as f:
            loaded_ingredients = json.loads(f.read())

    for ingr in excluded_ingrs:
        loaded_ingredients.pop(ingr)

    loop_best_error = 100
    best_quantities = {}

    for i in tqdm(range(loops)):

        ingredients = loaded_ingredients.copy()

        # Start with random proportions for each ingredient by using a Dirichlet distribution
        quantity = np.round(np.random.dirichlet(np.ones(len(ingredients)),size=1),4).tolist()[0]
        quantities = dict(zip(list(ingredients.keys()), quantity))
        debug_print("Quantities:" + str(quantities))

        props_to_ignore = []

        while True:
            # Calculate properties
            soap = property_calc(ingredients, quantities)

            # Store RMS error value
            error = rms_error(soap, desired_soap)
            debug_print("RMS Error:" + str(error))

            # Find the property with the largest differential
            prop_largest_diff = largest_diff(soap, props_to_ignore, desired_soap)
            debug_print("Property with biggest differential:" + str(prop_largest_diff))

            # If there are no property to adjust, we exit the loop
            if prop_largest_diff[0] == '':
                break

            # Otherwise we adjust the recipe to try to narrow the gap
            new_quantities = adjust_recipe(ingredients, prop_largest_diff[0], quantities, increment)
            debug_print("New quantities:" + str(new_quantities))

            # Recalculate properties and RMS error
            new_soap = property_calc(ingredients, new_quantities)
            new_error = rms_error(new_soap, desired_soap)

            debug_print("New RMS Error:" + str(new_error))

            # If the RMS error is higher than or equal to to the error before optimizing, loop
            if new_error >= error:
                # Try optimizing the next best diff property
                debug_print("Removing property:" + str(prop_largest_diff[0]))
                props_to_ignore.append(prop_largest_diff[0])
                if len(props_to_ignore) == (len(desired_soap) -1):
                    # When we're down to too few ingredients, we save the recipe and stop the loop
                    if error <= loop_best_error and soap['price'] <= max_price:
                        loop_best_error = error
                        best_quantities = quantities.copy()
                    break

            # Otherwise, we update the quantities for the next loop
            else:
                quantities = new_quantities

            # If we did better than the best recipe in the for loop error, we save it
            if new_error < loop_best_error and new_soap['price'] <= max_price:
                loop_best_error = new_error
                best_quantities = new_quantities.copy()

    best_soap = property_calc(loaded_ingredients, best_quantities)
    # If the RMS error is higher than the stored value, stop and print quantities and resulting soap
    print("Soap characteristics:", best_soap)
    print("RMS Error:", loop_best_error)
    print("Soap recipe:", best_quantities)

    if enable_graphs:
        plt.figure("Cold-process soap recipe generator")

        y1_pos = np.arange(len(best_quantities))

        ax1 = plt.subplot(2,1,1)
        plt.xticks(y1_pos, best_quantities.keys())
        plt.ylabel('Quantity')
        plt.xlabel('Ingredients')
        plt.title('Soap recipe')
        plt.grid(which='major', axis='y', linestyle=':', alpha=0.5, linewidth=1)
        quantities_chart = plt.bar(y1_pos, best_quantities.values(), align='center', alpha=0.5)
        for quantity in quantities_chart:
                height = quantity.get_height()
                ax1.text(quantity.get_x() + quantity.get_width()/2., 1.05*height,'%.1f%%' % float(height*100), ha='center', va='bottom')

        y2_pos = np.arange(len(soap))

        ax2 = plt.subplot(2,1,2)
        plt.xticks(y2_pos, soap)
        plt.ylabel('Value')
        plt.title('Soap characteristics')
        plt.grid(which='major', axis='y', linestyle=':', alpha=0.5, linewidth=1)
        properties_chart = plt.bar(y2_pos, best_soap.values(), align='center', alpha=0.5, color='g', label='Resulting soap')
        plt.bar(y2_pos, desired_soap.values(), align='center', alpha=0.5, color='r', label='Desired soap')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1, 1.1, "RMS Error: " + str(loop_best_error), transform=ax2.transAxes, ha='right', va='top', fontsize=8, bbox=props)
        height = properties_chart[7].get_height()
        ax2.text(properties_chart[7].get_x() + properties_chart[7].get_width() / 2., 1.05 * height, '$%.2f' % float(height), ha='center', va='bottom')

        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
