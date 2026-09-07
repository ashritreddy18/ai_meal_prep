import os
import sys
os.environ["OPENROUTER_API_KEY"] = "test_key"
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from schemas import MealRequest
from agent import check_hard_constraints
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
    
    errors = check_hard_constraints(b, l, d, request, 60)
    assert any("allergy" in e.lower() for e in errors)

def test_soft_constraints_cuisine():
    from agent import calculate_cuisine_score
    request = MealRequest(
        goal="fat loss",
        diet="vegetarian",
        time="flexible",
        preferred_cuisine="South Indian"
    )
    b = {"name": "Idli", "cuisine": "South Indian", "prep_minutes": 5, "diets": ["vegetarian"], "ingredients": []}
    l = {"name": "Dal", "cuisine": "North Indian", "prep_minutes": 15, "diets": ["vegetarian"], "ingredients": []}
    d = {"name": "Roti", "cuisine": "North Indian", "prep_minutes": 10, "diets": ["vegetarian"], "ingredients": []}
    
    score, possible = calculate_cuisine_score([b, l, d], request.preferred_cuisine)
    assert score == 5.0

def test_rag_allergy_filtering():
    # Allergy should be filtered out by search_recipes
    results = search_recipes("paneer", limit=10, allergies=["paneer"])
    for r in results:
        assert "paneer" not in r["name"].lower()
        for ing in r["ingredients"]:
            assert "paneer" not in ing["name"].lower()
