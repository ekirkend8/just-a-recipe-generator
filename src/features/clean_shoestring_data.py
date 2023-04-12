"""Initial data cleaning for Gluten Free on a Shoestring blog."""
import re
import copy
from fractions import Fraction
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


def pos_tagging(words):
    """POS tag words"""
    tokenized = nltk.word_tokenize(words)
    tokens_pos = nltk.pos_tag(tokenized)

    return tokens_pos


def recipe_ingredient_dict(recipe_dict):
    recipe_dict_new = {}

    for recipe in recipe_dict:
        try:
            for key in recipe_dict[recipe].keys():
                recipe_dict_new[key] = recipe_dict[recipe][key]["recipeIngredient"]
        except:
            pass

    return recipe_dict_new


def clean_recipe_title(recipe_dict):
    """Clean recipe titles."""
    clean_recipe_dict = {}

    for recipe in list(recipe_dict.keys()):
        if re.sub(r'[^a-zA-Z ]+', '', recipe) != "":
            recipe_new = re.sub(r'[^a-zA-Z ]+', '', recipe)
        else:
            recipe_new = recipe
        clean_recipe_dict[recipe_new] = recipe_dict[recipe]

    return clean_recipe_dict


def clean_recipe_ingredients(recipe_dict):
    clean_recipe_dict = {}
    for recipe in recipe_dict:
        clean_recipe_dict[recipe] = [
            ingredient.split("(")[0].rstrip() for ingredient in recipe_dict[recipe]
        ]

    return clean_recipe_dict


def format_ingredients(recipe_dict):
    """POS tag ingredients and convert numbers to real numbers."""
    ingredients_pos = {}

    for recipe in recipe_dict:
        ingredients_list_pos = []

        # POS tag
        for ingredient in recipe_dict[recipe]:
            ingredients_list_pos.append(pos_tagging(ingredient))

        # Convert numbers to real numbers
        for ingredient in range(0,len(ingredients_list_pos)):
            remove_index = []
            final_nbr = 0
            sum_nbr = 0
            nbr_cd = 0
            # For each POS of an ingredient
            for pos in ingredients_list_pos[ingredient]:
                # If it's a quantity
                if pos[1] == "CD":
                    # Get index of POS to reassign
                    pos_index = ingredients_list_pos[ingredient].index(pos)

                    try:
                        # if multiple numbers related to one ingredient, add them
                        final_nbr += Fraction(pos[0])
                        round_nbr = round(
                            final_nbr.numerator / final_nbr.denominator, 2
                        )
                        new_pos = (round_nbr, "CD")

                        # Set old POS as new
                        ingredients_list_pos[ingredient][pos_index] = new_pos

                        # Track number of POS quantities related to this ingredient
                        nbr_cd += 1
                        # If multiple quantity POS's related to ingredient
                        if nbr_cd > 1:
                            # Remove previous quantity
                            ingredients_list_pos[ingredient].pop(pos_index-1)
                    except:
                        pass

        ingredients_pos[recipe] = ingredients_list_pos

    return ingredients_pos


def pos_tuples_to_list(recipe_dict):
    """Create list of ingredient strings from cleaned POS tagged tuples."""
    recipe_pos = {}

    for recipe in recipe_dict:
        ingredients = []

        for ingredient in recipe_dict[recipe]:
            ingredient_full = []
            for item in ingredient:
                ingredient_full.append(str(item[0]))

            ingredients.append(" ".join(ingredient_full).rstrip())

        recipe_pos[recipe] = ingredients

    return recipe_pos


def clean_shoestring_recipes(recipe_data):
    recipe_dict = recipe_ingredient_dict(recipe_data)
    recipe_dict_clean_titles = clean_recipe_title(recipe_dict)
    recipe_dict_clean_ingredients = clean_recipe_ingredients(recipe_dict_clean_titles)
    recipe_dict_format_ingredients = format_ingredients(recipe_dict_clean_ingredients)
    recipe_dict_ingredients_list = pos_tuples_to_list(recipe_dict_format_ingredients)

    return recipe_dict_ingredients_list
