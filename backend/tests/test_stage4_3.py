import pytest
from unittest.mock import patch, MagicMock
import json

from schemas import MealRequest
from agent import (
    analyze_dimensions,
    generate_agentic_meal_plan,
    MAX_REVISION_ATTEMPTS,
    ImpossibleConstraintsError
)

def test_analyze_dimensions():
    breakdown = {
        "calories": 22.0,  # strong (>= 20)
        "protein": 12.0,   # weak (< 16)
        "cuisine": 5.0,    # weak (< 10)
        "preferred_ingredients": 8.0, # strong (>= 5)
        "disliked_ingredients": 3.0, # weak (< 5)
        "meal_suitability": 8.0, # strong (>= 7)
        "diversity": 8.0 # strong (>= 7)
    }
    
    weak, strong = analyze_dimensions(breakdown)
    
    assert "Protein" in weak
    assert "Preferred Cuisine" in weak
    assert "Disliked Ingredients" in weak
    assert "Calories" not in weak
    
    assert "Calories" in strong
    assert "Preferred Ingredients" in strong
    assert "Meal Suitability" in strong
    assert "Diversity" in strong
    assert "Protein" not in strong

@patch("agent.search_recipes")
@patch("agent.evaluate_meal_plan")
@patch("agent.client.chat.completions.create")
@patch("agent.get_recipe_by_name")
def test_agent_duplicate_rejection(mock_get_recipe, mock_openai, mock_eval, mock_search):
    # Setup the mock so the LLM sends the exact same candidate twice
    request = MealRequest(
        goal="Weight Loss",
        diet="Vegetarian",
        time="Under 30 mins",
        allergies=[],
        disliked_ingredients=[],
        preferred_cuisine="North Indian",
        preferred_ingredients=[],
        calorie_target=1500,
        protein_target=80
    )
    
    mock_get_recipe.return_value = {
        "name": "Mock Recipe",
        "description": "Mock desc",
        "prep_minutes": 10,
        "diets": ["Vegetarian"],
        "meal_type": "breakfast",
        "nutrition": {"calories": 500, "protein_g": 30, "carbs_g": 50, "fat_g": 10, "fiber_g": 5},
        "ingredients": [],
        "instructions": []
    }
    
    # LLM always returns a tool call to submit the identical meal plan
    def mock_openai_call(*args, **kwargs):
        mock_msg = MagicMock()
        mock_msg.role = "assistant"
        mock_msg.content = None
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "submit_meal_plan"
        mock_tool_call.function.arguments = json.dumps({
            "breakfast_recipe_name": "Idli",
            "lunch_recipe_name": "Roti",
            "dinner_recipe_name": "Dal"
        })
        mock_msg.tool_calls = [mock_tool_call]
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_msg)]
        return mock_response
        
    mock_openai.side_effect = mock_openai_call
    
    # Evaluation returns 75 (so it doesn't immediately exit)
    mock_eval.return_value = {
        "hard_constraints": {"passed": True, "errors": []},
        "quality_score": 75,
        "quality_band": "Acceptable",
        "breakdown": {"calories": 25, "protein": 10},
        "improvements": ["Needs more protein"]
    }
    
    res = generate_agentic_meal_plan(request)
        
    # The agent should fail to reach the threshold after hitting MAX_REVISION_ATTEMPTS,
    # but more importantly, we check that `evaluate_meal_plan` was only called ONCE
    # despite the LLM trying to submit it 6 times, because of duplicate rejection.
    assert mock_eval.call_count == 1
    assert res.meals.breakfast.name == "Mock Recipe"
    
@patch("agent.search_recipes")
@patch("agent.evaluate_meal_plan")
@patch("agent.client.chat.completions.create")
@patch("agent.get_recipe_by_name")
def test_agent_evaluates_regression_and_keeps_best(mock_get_recipe, mock_openai, mock_eval, mock_search):
    request = MealRequest(
        goal="Weight Loss",
        diet="Vegetarian",
        time="Under 30 mins",
        allergies=[],
        disliked_ingredients=[],
        preferred_cuisine="North Indian",
        preferred_ingredients=[],
        calorie_target=1500,
        protein_target=80
    )
    
    mock_get_recipe.return_value = {
        "name": "Mock Recipe",
        "description": "Mock desc",
        "prep_minutes": 10,
        "diets": ["Vegetarian"],
        "meal_type": "breakfast",
        "nutrition": {"calories": 500, "protein_g": 30, "carbs_g": 50, "fat_g": 10, "fiber_g": 5},
        "ingredients": [],
        "instructions": []
    }
    
    # We will simulate the LLM proposing a plan with score 75, then 65.
    
    call_count = 0
    def mock_openai_call(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_msg = MagicMock()
        mock_msg.role = "assistant"
        mock_msg.content = None
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "submit_meal_plan"
        
        if call_count == 1:
            mock_tool_call.function.arguments = json.dumps({
                "breakfast_recipe_name": "PlanA_B",
                "lunch_recipe_name": "PlanA_L",
                "dinner_recipe_name": "PlanA_D"
            })
        else:
            mock_tool_call.function.arguments = json.dumps({
                "breakfast_recipe_name": f"Plan{call_count}_B",
                "lunch_recipe_name": f"Plan{call_count}_L",
                "dinner_recipe_name": f"Plan{call_count}_D"
            })
        
        mock_msg.tool_calls = [mock_tool_call]
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_msg)]
        return mock_response
        
    mock_openai.side_effect = mock_openai_call
    
    def mock_eval_call(args, req, prep_time):
        if args["breakfast_recipe_name"] == "PlanA_B":
            # First plan, score 75
            return {
                "hard_constraints": {"passed": True, "errors": []},
                "quality_score": 75,
                "quality_band": "Acceptable",
                "breakdown": {"calories": 25, "protein": 10},
                "improvements": ["Needs more protein"]
            }
        else:
            # Subsequent plans, score 60
            return {
                "hard_constraints": {"passed": True, "errors": []},
                "quality_score": 60,
                "quality_band": "Needs Improvement",
                "breakdown": {"calories": 15, "protein": 10},
                "improvements": ["Worse"]
            }
            
    mock_eval.side_effect = mock_eval_call
    
    res = generate_agentic_meal_plan(request)
    
    # Since none reached 80, it should fallback to the best candidate (PlanA, score 75)
    # The final output relies on get_recipe_by_name which returns Mock Recipe
    assert res.meals.breakfast.name == "Mock Recipe"
    assert mock_eval.call_count == MAX_REVISION_ATTEMPTS
