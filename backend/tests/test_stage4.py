import os
import sys
os.environ["OPENROUTER_API_KEY"] = "test_key"
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from schemas import MealRequest
from agent import check_recipe_constraints
from rag import search_recipes

def test_hard_constraints_allergies():
    request = MealRequest(
        goal="fat loss",
        diet="vegetarian",
        time="flexible",
        allergies=["peanuts", "dairy"]
    )
    b = {"name": "Peanut Butter Toast", "prep_minutes": 5, "diets": ["vegetarian"], "ingredients": [{"name": "peanuts"}]}
    l = {"name": "Dal", "prep_minutes": 15, "diets": ["vegetarian"], "ingredients": [{"name": "lentils"}]}
    d = {"name": "Roti", "prep_minutes": 10, "diets": ["vegetarian"], "ingredients": [{"name": "wheat"}]}
    
    errors, warnings = check_recipe_constraints(b, l, d, request, 60)
    assert any("allergy" in e.lower() for e in errors)
    assert len(warnings) == 0

def test_soft_constraints_cuisine():
    request = MealRequest(
        goal="fat loss",
        diet="vegetarian",
        time="flexible",
        preferred_cuisine="South Indian"
    )
    b = {"name": "Idli", "cuisine": "South Indian", "prep_minutes": 5, "diets": ["vegetarian"], "ingredients": []}
    l = {"name": "Dal", "cuisine": "North Indian", "prep_minutes": 15, "diets": ["vegetarian"], "ingredients": []}
    d = {"name": "Roti", "cuisine": "North Indian", "prep_minutes": 10, "diets": ["vegetarian"], "ingredients": []}
    
    errors, warnings = check_recipe_constraints(b, l, d, request, 60)
    assert len(errors) == 0
    assert any("does not match preferred cuisine" in w.lower() for w in warnings)

def test_rag_allergy_filtering():
    # Allergy should be filtered out by search_recipes
    results = search_recipes("paneer", limit=10, allergies=["paneer"])
    for r in results:
        assert "paneer" not in r["name"].lower()
        for ing in r["ingredients"]:
            assert "paneer" not in ing["name"].lower()
