import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from rag import search_recipes, initialize_database, client

def test_rag_indexing():
    # Force initialization
    initialize_database()
    col = client.get_collection("recipes")
    assert col.count() >= 120, f"ChromaDB only indexed {col.count()} recipes"

def test_retrieval_south_indian_veg_breakfast():
    results = search_recipes("quick South Indian vegetarian breakfast", max_prep_time=60, diet="vegetarian", meal_type="breakfast")
    assert len(results) > 0
    for r in results:
        assert any(d.lower() == "vegetarian" for d in r["diets"])
        assert r["meal_type"].lower() == "breakfast"
        assert r["prep_minutes"] + r.get("cook_minutes", 0) <= 60

def test_retrieval_high_protein_veg_dinner():
    results = search_recipes("high protein vegetarian dinner", max_prep_time=120, diet="vegetarian", meal_type="dinner")
    assert len(results) > 0
    for r in results:
        assert any(d.lower() == "vegetarian" for d in r["diets"])
        assert r["meal_type"].lower() == "dinner"

def test_retrieval_vegan_lunch():
    results = search_recipes("vegan Indian lunch", max_prep_time=120, diet="vegan", meal_type="lunch")
    assert len(results) > 0
    for r in results:
        assert any(d.lower() == "vegan" for d in r["diets"])
        assert r["meal_type"].lower() == "lunch"

def test_retrieval_andhra_nonveg_dinner():
    results = search_recipes("Andhra non vegetarian dinner", max_prep_time=120, diet="non-vegetarian", meal_type="dinner")
    assert len(results) > 0
    for r in results:
        assert any(d.lower() == "non-vegetarian" for d in r["diets"])
        assert r["meal_type"].lower() == "dinner"

def test_retrieval_kerala_fish_curry():
    results = search_recipes("Kerala fish curry", max_prep_time=120, diet="non-vegetarian", meal_type="")
    assert len(results) > 0
    # Allow lunch or dinner or unspecified

def test_retrieval_north_indian_breakfast():
    results = search_recipes("North Indian breakfast", max_prep_time=120, diet="", meal_type="breakfast")
    assert len(results) > 0
    for r in results:
        assert r["meal_type"].lower() == "breakfast"

def test_retrieval_high_protein_chicken_meal():
    results = search_recipes("high protein Indian chicken meal", max_prep_time=120, diet="non-vegetarian", meal_type="")
    assert len(results) > 0
    for r in results:
        assert any(d.lower() == "non-vegetarian" for d in r["diets"])
