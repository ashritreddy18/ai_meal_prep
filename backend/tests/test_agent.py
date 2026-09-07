import os
os.environ["OPENROUTER_API_KEY"] = "test_key"
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock
from schemas import MealRequest, SearchRecipesInput, SubmitMealPlanInput
from agent import (
    search_recipes,
    check_recipe_constraints,
    calculate_meal_nutrition,
    evaluate_meal_plan,
    generate_agentic_meal_plan,
    get_recipe_by_name
)

def test_tool_schemas_valid():
    # 1. Tool schemas are valid
    data = {"diet": "vegetarian", "max_prep_time": 30, "keywords": "protein", "meal_type": "breakfast"}
    obj = SearchRecipesInput(**data)
    assert obj.diet == "vegetarian"
    assert obj.max_prep_time == 30

def test_recipe_search():
    # 2. Recipe search returns valid recipes
    # 3. Diet constraints enforced
    # 4. Cooking-time constraints enforced
    results = search_recipes("paneer", max_prep_time=20, diet="vegetarian", meal_type="dinner")
    for r in results:
        assert r["prep_minutes"] <= 20
        assert "vegetarian" in r["diet"]
        assert "dinner" in r["meal_type"]

def test_calculate_nutrition():
    # 5. Nutrition totals are calculated deterministically
    b = {"nutrition": {"calories": 300, "protein_g": 10}}
    l = {"nutrition": {"calories": 500, "protein_g": 20}}
    d = {"nutrition": {"calories": 400, "protein_g": 15}}
    cal, prot = calculate_meal_nutrition(b, l, d)
    assert cal == 1200
    assert prot == 45

def test_evaluation_invalid_plan():
    # 6. Evaluation detects an invalid meal plan
    req = MealRequest(goal="weight loss", diet="vegan", time="Quick (<=30 min)")
    args = {
        "breakfast_recipe_name": "Nonexistent", 
        "lunch_recipe_name": "Paneer Bhurji with Bajra Roti", 
        "dinner_recipe_name": "Tofu & Vegetable Curry with Moong Dal"
    }
    res = evaluate_meal_plan(args, req, 30)
    assert res["passed"] == False
    assert "not found in knowledge base" in str(res["errors"])

@patch('agent.client.chat.completions.create')
def test_revision_loop_and_schema(mock_create):
    # 7. Planner can revise an invalid plan
    # 8. Final output conforms to Pydantic schema
    
    # Fake response 1: submit invalid plan
    mock_msg_1 = MagicMock()
    mock_msg_1.role = "assistant"
    mock_msg_1.content = None
    mock_tc_1 = MagicMock()
    mock_tc_1.id = "call_1"
    mock_tc_1.function.name = "submit_meal_plan"
    mock_tc_1.function.arguments = '{"breakfast_recipe_name": "Fake Recipe", "lunch_recipe_name": "Fake Recipe", "dinner_recipe_name": "Fake Recipe"}'
    mock_msg_1.tool_calls = [mock_tc_1]
    
    # Fake response 2: submit valid plan
    mock_msg_2 = MagicMock()
    mock_msg_2.role = "assistant"
    mock_msg_2.content = None
    mock_tc_2 = MagicMock()
    mock_tc_2.id = "call_2"
    mock_tc_2.function.name = "submit_meal_plan"
    mock_tc_2.function.arguments = '{"breakfast_recipe_name": "Masala Dosa", "lunch_recipe_name": "Bisi Bele Bath", "dinner_recipe_name": "Palak Paneer"}'
    mock_msg_2.tool_calls = [mock_tc_2]
    
    mock_choice_1 = MagicMock()
    mock_choice_1.message = mock_msg_1
    mock_comp_1 = MagicMock()
    mock_comp_1.choices = [mock_choice_1]
    
    mock_choice_2 = MagicMock()
    mock_choice_2.message = mock_msg_2
    mock_comp_2 = MagicMock()
    mock_comp_2.choices = [mock_choice_2]
    
    mock_create.side_effect = [mock_comp_1, mock_comp_2]
    
    req = MealRequest(goal="maintenance", diet="vegetarian", time="Flexible (~60 min)")
    plan = generate_agentic_meal_plan(req)
    
    assert mock_create.call_count == 2
    assert plan.meals.breakfast.name == "Masala Dosa"
    assert plan.meals.lunch.name == "Bisi Bele Bath"
    assert plan.meals.dinner.name == "Palak Paneer"

from fastapi.testclient import TestClient
from main import app

def test_generate_meal_endpoint():
    # 9. /generate-meal still works
    client = TestClient(app)
    response = client.post(
        "/generate-meal",
        json={"goal": "muscle gain", "diet": "vegetarian", "time": "Flexible (~60 min)"}
    )
    assert response.status_code == 200
    assert "meal_plan" in response.json()
    assert "breakfast" in response.json()["meal_plan"]["meals"]

def test_empty_search_query():
    # Empty query should not crash ChromaDB and should return results based on constraints
    results = search_recipes("", max_prep_time=20, diet="vegetarian", meal_type="dinner")
    assert isinstance(results, list)

@patch('agent.client.chat.completions.create')
def test_termination_impossible_constraints(mock_create):
    # LLM searches, gets no results, and calls terminate_plan
    
    # Fake response: call terminate_plan
    mock_msg = MagicMock()
    mock_msg.role = "assistant"
    mock_msg.content = None
    mock_tc = MagicMock()
    mock_tc.id = "call_1"
    mock_tc.function.name = "terminate_plan"
    mock_tc.function.arguments = '{"reason": "No vegan breakfast available under 10 mins"}'
    mock_msg.tool_calls = [mock_tc]
    
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_comp = MagicMock()
    mock_comp.choices = [mock_choice]
    
    mock_create.return_value = mock_comp
    
    from agent import ImpossibleConstraintsError
    req = MealRequest(goal="weight loss", diet="vegan", time="Quick (<=10 min)")
    
    with pytest.raises(ImpossibleConstraintsError) as excinfo:
        generate_agentic_meal_plan(req)
        
    assert "No vegan breakfast" in str(excinfo.value)

