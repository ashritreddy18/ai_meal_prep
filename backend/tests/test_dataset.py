import json
import os
import pytest

RECIPES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "indian_recipes.json")

@pytest.fixture
def recipes():
    with open(RECIPES_PATH, "r") as f:
        return json.load(f)

def test_1_required_fields_exist(recipes):
    required = ["recipe_id", "name", "description", "region", "cuisine", "meal_type", "diets", "ingredients", "instructions", "prep_minutes", "cook_minutes", "nutrition", "spice_level", "tags", "servings"]
    for r in recipes:
        for f in required:
            assert f in r, f"Recipe '{r.get('name')}' is missing required field '{f}'"

def test_2_recipe_ids_unique(recipes):
    ids = [r["recipe_id"] for r in recipes]
    assert len(ids) == len(set(ids)), "Recipe IDs are not unique"

def test_3_no_duplicate_names(recipes):
    names = [r["name"].lower().strip() for r in recipes]
    assert len(names) == len(set(names)), "Duplicate recipe names found"

def test_4_diet_classifications_valid(recipes):
    valid = {"Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian"}
    for r in recipes:
        for d in r["diets"]:
            assert d in valid, f"Invalid diet '{d}' in recipe '{r['name']}'"

def test_5_meal_types_valid(recipes):
    valid = {"Breakfast", "Lunch", "Dinner", "Snack"}
    for r in recipes:
        assert r["meal_type"] in valid, f"Invalid meal_type '{r['meal_type']}' in recipe '{r['name']}'"

def test_6_prep_cook_minutes_sensible(recipes):
    for r in recipes:
        assert isinstance(r["prep_minutes"], int) and r["prep_minutes"] >= 0
        assert isinstance(r["cook_minutes"], int) and r["cook_minutes"] >= 0
        assert r["prep_minutes"] + r["cook_minutes"] <= 240, f"Recipe '{r['name']}' takes too long (> 4 hours)"

def test_7_nutrition_values_non_negative_and_not_zero(recipes):
    for r in recipes:
        n = r["nutrition"]
        assert n["calories"] > 0, f"Calories missing for {r['name']}"
        assert n["protein_g"] >= 0
        assert n["carbs_g"] >= 0
        assert n["fat_g"] >= 0
        assert n["fiber_g"] >= 0
        # A real recipe should have some macros
        assert (n["protein_g"] + n["carbs_g"] + n["fat_g"]) > 0, f"Macros missing for {r['name']}"

def test_8_ingredients_not_empty(recipes):
    for r in recipes:
        assert isinstance(r["ingredients"], list)
        assert len(r["ingredients"]) >= 3, f"Recipe '{r['name']}' has suspiciously few ingredients ({len(r['ingredients'])})"
        for i in r["ingredients"]:
            assert "name" in i
            assert "quantity" in i
            assert "unit" in i

def test_9_instructions_not_empty(recipes):
    for r in recipes:
        assert isinstance(r["instructions"], list)
        assert len(r["instructions"]) >= 3, f"Recipe '{r['name']}' has suspiciously few instructions"
        for inst in r["instructions"]:
            # Check for generic boilerplate
            lower_inst = inst.lower()
            assert "cook authentically" not in lower_inst, f"Boilerplate instruction in '{r['name']}'"
            assert "prepare ingredients" not in lower_inst, f"Boilerplate instruction in '{r['name']}'"
            assert len(inst.split()) >= 3, f"Instruction '{inst}' in '{r['name']}' is too short"

def test_10_vegetarian_recipes_no_meat(recipes):
    obvious_meat = ["chicken", "mutton", "fish", "beef", "pork", "prawns"]
    for r in recipes:
        if "Vegetarian" in r["diets"] or "Vegan" in r["diets"]:
            for i in r["ingredients"]:
                assert i["name"].lower() not in obvious_meat, f"Vegetarian recipe '{r['name']}' contains meat '{i['name']}'"

def test_11_vegan_recipes_no_animal_products(recipes):
    obvious_animal = ["chicken", "mutton", "fish", "egg", "paneer", "ghee", "curd", "cream", "milk", "butter", "prawns", "honey"]
    for r in recipes:
        if "Vegan" in r["diets"]:
            for i in r["ingredients"]:
                assert i["name"].lower() not in obvious_animal, f"Vegan recipe '{r['name']}' contains animal product '{i['name']}'"

def test_12_minimum_recipe_count(recipes):
    assert len(recipes) >= 120, f"Expected at least 120 recipes, found {len(recipes)}"

def test_13_no_duplicate_recipe_structures(recipes):
    structures = set()
    for r in recipes:
        # Create a signature based on ingredients
        ings = tuple(sorted([i["name"].lower() for i in r["ingredients"]]))
        assert ings not in structures, f"Recipe '{r['name']}' has identical ingredients to another recipe"
        structures.add(ings)

