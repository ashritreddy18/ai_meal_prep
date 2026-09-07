import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock

from schemas import MealRequest
from agent import (
    calculate_calorie_score,
    calculate_protein_score,
    calculate_cuisine_score,
    calculate_preferred_ingredient_score,
    calculate_disliked_ingredient_score,
    calculate_meal_suitability_score,
    calculate_diversity_score,
    calculate_quality_score,
    evaluate_meal_plan,
    generate_agentic_meal_plan,
    get_recipe_by_name
)

# ---------------------------------------------------------
# PURE SCORING FUNCTION TESTS
# ---------------------------------------------------------

def test_calorie_score():
    # Exact/Very close (<= 5%)
    score, possible = calculate_calorie_score(2000, 2000)
    assert score == 25.0
    
    # Small deviation (<= 10%)
    score, possible = calculate_calorie_score(1820, 2000) # 9% deviation
    assert score == 20.0
    
    # Moderate deviation (<= 20%)
    score, possible = calculate_calorie_score(2360, 2000) # 18% deviation (too high)
    assert score == 15.0
    
    # Large deviation (<= 30%)
    score, possible = calculate_calorie_score(1440, 2000) # 28% deviation
    assert score == 10.0
    
    # Extreme deviation (> 30%)
    score, possible = calculate_calorie_score(1300, 2000) # 35% deviation
    assert score == 0.0

def test_protein_score():
    # Exact/Very close (<= 5%)
    score, possible = calculate_protein_score(100, 100)
    assert score == 20.0
    
    # Small deviation (<= 10%)
    score, possible = calculate_protein_score(90, 100) # 10% deviation
    assert score == 16.0
    
    # Moderate deviation (<= 20%)
    score, possible = calculate_protein_score(115, 100) # 15% deviation (too high)
    assert score == 10.0
    
    # Large deviation (<= 30%)
    score, possible = calculate_protein_score(130, 100) # 30% deviation (too high)
    assert score == 5.0
    
    # Extreme deviation (> 30%)
    score, possible = calculate_protein_score(50, 100) # 50% deviation
    assert score == 0.0

def test_no_optional_preferences():
    # No optional preferences -> score does not incorrectly become 0
    recipes = [
        {"name": "A", "ingredients": [], "nutrition": {"calories": 500, "protein_g": 20}, "cuisine": "any", "meal_type": ["breakfast"]}, 
        {"name": "B", "ingredients": [], "nutrition": {"calories": 500, "protein_g": 20}, "cuisine": "any", "meal_type": ["lunch"]}, 
        {"name": "C", "ingredients": [], "nutrition": {"calories": 500, "protein_g": 20}, "cuisine": "any", "meal_type": ["dinner"]}
    ]
    req = MealRequest(goal="maintenance", diet="vegetarian", time="Flexible")
    score, band, breakdown, imp = calculate_quality_score(recipes, req)
    
    # Cal, Protein, Cuisine, Pref, Dislike should be None
    assert breakdown["calories"] is None
    assert breakdown["protein"] is None
    assert breakdown["cuisine"] is None
    assert breakdown["preferred_ingredients"] is None
    assert breakdown["disliked_ingredients"] is None
    # Still calculates diversity and suitability
    assert score > 0 # Normalizes out of remaining applicable points
    
def test_cuisine_score():
    recipes = [
        {"cuisine": "South Indian"},
        {"region": "South Indian Region"},
        {"cuisine": "North Indian"}
    ]
    # Match -> higher score
    score, possible = calculate_cuisine_score(recipes, "South Indian")
    assert score == 10.0 # 2 out of 3 match
    
    # Mismatch -> lower score
    score, possible = calculate_cuisine_score(recipes, "Italian")
    assert score == 0.0

def test_preferred_ingredients_score():
    recipes = [
        {"name": "Paneer Tikka", "ingredients": [{"name": "Paneer"}]},
        {"name": "Dal", "ingredients": [{"name": "Lentils"}, {"name": "Spinach"}]}
    ]
    # Match -> higher score
    score, possible = calculate_preferred_ingredient_score(recipes, ["paneer", "spinach"])
    assert score == 10.0
    
    # Partial match
    score, possible = calculate_preferred_ingredient_score(recipes, ["paneer", "chicken"])
    assert score == 5.0

def test_disliked_ingredients_score():
    recipes = [
        {"name": "Paneer Tikka", "ingredients": [{"name": "Paneer"}, {"name": "Onion"}]},
        {"name": "Dal", "ingredients": [{"name": "Lentils"}, {"name": "Garlic"}]}
    ]
    # Absent -> full score
    score, possible = calculate_disliked_ingredient_score(recipes, ["Mushroom"])
    assert score == 10.0
    
    # Present -> reduced score
    score, possible = calculate_disliked_ingredient_score(recipes, ["Onion"])
    assert score < 10.0 and score > 0.0

def test_diversity_score():
    # High ingredient overlap -> lower diversity
    recipes_high_overlap = [
        {"ingredients": [{"name": "A"}, {"name": "B"}]},
        {"ingredients": [{"name": "A"}, {"name": "B"}]},
        {"ingredients": [{"name": "A"}, {"name": "C"}]}
    ]
    score, possible = calculate_diversity_score(recipes_high_overlap)
    assert score < 10.0

    # Low ingredient overlap -> higher diversity
    recipes_low_overlap = [
        {"ingredients": [{"name": "A"}, {"name": "B"}]},
        {"ingredients": [{"name": "C"}, {"name": "D"}]},
        {"ingredients": [{"name": "E"}, {"name": "F"}]}
    ]
    score2, possible2 = calculate_diversity_score(recipes_low_overlap)
    assert score2 == 10.0

# ---------------------------------------------------------
# EVALUATOR TESTS
# ---------------------------------------------------------

def test_evaluator_hard_constraint_failure():
    # Hard constraint failure -> plan invalid regardless of score
    # We will pass 3 identical recipes to trigger Duplicate recipe hard failure
    req = MealRequest(goal="maintenance", diet="vegetarian", time="Flexible")
    args = {
        "breakfast_recipe_name": "Masala Dosa",
        "lunch_recipe_name": "Masala Dosa",
        "dinner_recipe_name": "Masala Dosa"
    }
    # Need to make sure Masala Dosa exists in knowledge base
    # (If it doesn't, it will trigger the "not found" error, which is also a hard failure)
    res = evaluate_meal_plan(args, req, 60)
    assert res["hard_constraints"]["passed"] == False
    assert res["quality_score"] == 0
    assert res["quality_band"] == "Invalid"

def test_evaluator_score_bounds():
    # Ensure overall score remains within 0-100
    req = MealRequest(goal="maintenance", diet="vegetarian", time="Flexible")
    args = {
        "breakfast_recipe_name": "Poha",
        "lunch_recipe_name": "Bisi Bele Bath",
        "dinner_recipe_name": "Palak Paneer"
    }
    # Assuming these exist in the dataset
    res = evaluate_meal_plan(args, req, 120)
    if res["hard_constraints"]["passed"]:
        assert 0 <= res["quality_score"] <= 100
        for val in res["breakdown"].values():
            if val is not None:
                assert val >= 0.0

# ---------------------------------------------------------
# AGENT LOOP TESTS
# ---------------------------------------------------------

@patch('agent.client.chat.completions.create')
def test_agent_valid_plan_accepted_immediately(mock_create):
    # Valid plan with score >= threshold -> accepted immediately
    # We will mock the evaluator to return a high score
    
    mock_msg = MagicMock()
    mock_msg.role = "assistant"
    mock_msg.content = None
    mock_tc = MagicMock()
    mock_tc.id = "call_1"
    mock_tc.function.name = "submit_meal_plan"
    mock_tc.function.arguments = '{"breakfast_recipe_name": "Poha", "lunch_recipe_name": "Bisi Bele Bath", "dinner_recipe_name": "Palak Paneer"}'
    mock_msg.tool_calls = [mock_tc]
    
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_comp = MagicMock()
    mock_comp.choices = [mock_choice]
    
    mock_create.return_value = mock_comp
    
    with patch('agent.evaluate_meal_plan') as mock_eval:
        mock_eval.return_value = {
            "hard_constraints": {"passed": True, "errors": []},
            "quality_score": 95,
            "quality_band": "Excellent",
            "breakdown": {},
            "improvements": []
        }
        
        req = MealRequest(goal="maintenance", diet="vegetarian", time="Flexible")
        plan = generate_agentic_meal_plan(req)
        
        # Only 1 iteration should happen
        assert mock_create.call_count == 1
        assert plan.meals.breakfast.name == "Poha"

@patch('agent.client.chat.completions.create')
def test_agent_improvement_path_and_max_attempts(mock_create):
    # Valid plan with score < threshold -> improvement path
    # Maximum improvement attempts are respected
    
    # We will mock the agent to always submit the same plan, but mock the evaluator
    # to always return a low score (70). The agent should loop until max_iterations
    # and then fall back to the best plan seen (the 70 score plan).
    
    mock_msg = MagicMock()
    mock_msg.role = "assistant"
    mock_msg.content = None
    mock_tc = MagicMock()
    mock_tc.id = "call_1"
    mock_tc.function.name = "submit_meal_plan"
    mock_tc.function.arguments = '{"breakfast_recipe_name": "Poha", "lunch_recipe_name": "Bisi Bele Bath", "dinner_recipe_name": "Palak Paneer"}'
    mock_msg.tool_calls = [mock_tc]
    
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_comp = MagicMock()
    mock_comp.choices = [mock_choice]
    
    mock_create.return_value = mock_comp
    
    with patch('agent.evaluate_meal_plan') as mock_eval:
        mock_eval.return_value = {
            "hard_constraints": {"passed": True, "errors": []},
            "quality_score": 70,
            "quality_band": "Acceptable",
            "breakdown": {},
            "improvements": ["Need more protein"]
        }
        
        req = MealRequest(goal="maintenance", diet="vegetarian", time="Flexible")
        
        # Since it always scores 70 (< 80), it will loop 6 times (max_iterations)
        plan = generate_agentic_meal_plan(req)
        
        assert mock_create.call_count == 6
        assert plan.meals.breakfast.name == "Poha"
