import os
import json
from openai import OpenAI
from pydantic import ValidationError

from schemas import MealRequest, MealPlanResponse, DailyMeals, MealDetails, NutritionInfo, Ingredient
from rag import search_recipes, RECIPES_PATH

class ImpossibleConstraintsError(Exception):
    pass

MAX_REVISION_ATTEMPTS = 6

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def extract_time_minutes(time_str: str) -> int:
    if "30" in time_str and "<=" in time_str:
        return 30
    if "60" in time_str:
        return 60
    return 120

def get_recipe_by_name(name: str):
    with open(RECIPES_PATH, "r") as f:
        recipes = json.load(f)
    for r in recipes:
        if r['name'].lower().strip() == name.lower().strip():
            return r
    return None

def calculate_meal_nutrition(breakfast, lunch, dinner):
    cal = breakfast['nutrition']['calories'] + lunch['nutrition']['calories'] + dinner['nutrition']['calories']
    prot = breakfast['nutrition']['protein_g'] + lunch['nutrition']['protein_g'] + dinner['nutrition']['protein_g']
    return cal, prot

def check_hard_constraints(breakfast, lunch, dinner, request: MealRequest, prep_time_limit: int):
    errors = []
    
    # Check Time (Hard)
    if breakfast['prep_minutes'] + breakfast.get('cook_minutes', 0) > prep_time_limit:
        errors.append(f"Breakfast prep+cook time ({breakfast['prep_minutes']+breakfast.get('cook_minutes', 0)}m) exceeds limit ({prep_time_limit}m).")
    if lunch['prep_minutes'] + lunch.get('cook_minutes', 0) > prep_time_limit:
        errors.append(f"Lunch prep+cook time ({lunch['prep_minutes']+lunch.get('cook_minutes', 0)}m) exceeds limit ({prep_time_limit}m).")
    if dinner['prep_minutes'] + dinner.get('cook_minutes', 0) > prep_time_limit:
        errors.append(f"Dinner prep+cook time ({dinner['prep_minutes']+dinner.get('cook_minutes', 0)}m) exceeds limit ({prep_time_limit}m).")
        
    # Check Diet (Hard)
    req_diet = request.diet.lower()
    if req_diet not in [d.lower() for d in breakfast['diets']]:
        errors.append(f"Breakfast '{breakfast['name']}' is not {req_diet}.")
    if req_diet not in [d.lower() for d in lunch['diets']]:
        errors.append(f"Lunch '{lunch['name']}' is not {req_diet}.")
    if req_diet not in [d.lower() for d in dinner['diets']]:
        errors.append(f"Dinner '{dinner['name']}' is not {req_diet}.")

    # Check Duplicate (Hard)
    names = [breakfast['name'], lunch['name'], dinner['name']]
    if len(set(names)) != 3:
        errors.append("You selected the same recipe for multiple meals.")
        
    # Check Allergies (Hard)
    for meal_name, r in [('Breakfast', breakfast), ('Lunch', lunch), ('Dinner', dinner)]:
        if request.allergies:
            for allergy in request.allergies:
                al = allergy.lower().strip()
                if not al: continue
                if al in r['name'].lower():
                    errors.append(f"{meal_name} '{r['name']}' contains allergy '{allergy}'.")
                    continue
                for ing in r['ingredients']:
                    if al in ing['name'].lower():
                        errors.append(f"{meal_name} '{r['name']}' contains allergy '{allergy}'.")
                        break
    return errors

from typing import Optional, Tuple

def calculate_calorie_score(actual: int, target: int) -> Tuple[Optional[float], float]:
    """
    Evaluates how closely the meal plan matches the daily calorie target.
    Uses a strict target-band approach (max 25 points).
    Excessively high or low calories are penalized.
    - Very close (<= 5% deviation): 25.0 (Maximum score)
    - Small deviation (<= 10% deviation): 20.0 (Gradual reduction)
    - Moderate deviation (<= 20% deviation): 15.0
    - Large deviation (<= 30% deviation): 10.0 (Substantially lower score)
    - Extreme deviation (> 30% deviation): 0.0
    """
    if target <= 0: return None, 25.0
    diff = abs(actual - target) / target
    if diff <= 0.05: return 25.0, 25.0
    elif diff <= 0.10: return 20.0, 25.0
    elif diff <= 0.20: return 15.0, 25.0
    elif diff <= 0.30: return 10.0, 25.0
    else: return 0.0, 25.0

def calculate_protein_score(actual: float, target: float) -> Tuple[Optional[float], float]:
    """
    Evaluates how closely the meal plan matches the daily protein target.
    Uses a strict target-band approach (max 20 points).
    Excessively high protein is also penalized, not just low protein.
    - Very close (<= 5% deviation): 20.0 (Maximum score)
    - Small deviation (<= 10% deviation): 16.0 (Gradual reduction)
    - Moderate deviation (<= 20% deviation): 10.0
    - Large deviation (<= 30% deviation): 5.0 (Substantially lower score)
    - Extreme deviation (> 30% deviation): 0.0
    """
    if target <= 0: return None, 20.0
    diff = abs(actual - target) / target
    if diff <= 0.05: return 20.0, 20.0
    elif diff <= 0.10: return 16.0, 20.0
    elif diff <= 0.20: return 10.0, 20.0
    elif diff <= 0.30: return 5.0, 20.0
    else: return 0.0, 20.0

def calculate_cuisine_score(recipes: list, preferred_cuisine: str) -> Tuple[Optional[float], float]:
    if not preferred_cuisine: return None, 15.0
    pc = preferred_cuisine.lower().strip()
    score = 0.0
    for r in recipes:
        if pc in r.get('cuisine', '').lower() or pc in r.get('region', '').lower():
            score += 5.0
    return score, 15.0

def calculate_preferred_ingredient_score(recipes: list, preferred_ingredients: list) -> Tuple[Optional[float], float]:
    valid_prefs = [p.strip() for p in (preferred_ingredients or []) if p.strip()]
    if not valid_prefs: return None, 10.0
    
    total_found = 0
    for pref in valid_prefs:
        p = pref.lower()
        found = False
        for r in recipes:
            if p in r['name'].lower():
                found = True
                break
            for ing in r['ingredients']:
                if p in ing['name'].lower():
                    found = True
                    break
        if found:
            total_found += 1
            
    score = (total_found / len(valid_prefs)) * 10.0
    return score, 10.0

def calculate_disliked_ingredient_score(recipes: list, disliked_ingredients: list) -> Tuple[Optional[float], float]:
    valid_dislikes = [d.strip() for d in (disliked_ingredients or []) if d.strip()]
    if not valid_dislikes: return None, 10.0
    
    violations = 0
    for r in recipes:
        for dislike in valid_dislikes:
            dl = dislike.lower()
            if dl in r['name'].lower():
                violations += 1
                break
            found = False
            for ing in r['ingredients']:
                if dl in ing['name'].lower():
                    found = True
                    break
            if found:
                violations += 1
                break
                
    score = max(0.0, 10.0 - (violations * 3.334))
    return score, 10.0

def calculate_meal_suitability_score(recipes: list, expected_slots: list) -> Tuple[Optional[float], float]:
    score = 0.0
    for r, slot in zip(recipes, expected_slots):
        m_type = r.get('meal_type', '')
        if isinstance(m_type, str):
            if slot in m_type.lower():
                score += 3.334
        elif isinstance(m_type, list):
            if any(slot in mt.lower() for mt in m_type):
                score += 3.334
    return min(10.0, score), 10.0

def calculate_diversity_score(recipes: list) -> Tuple[Optional[float], float]:
    def get_ing_set(r):
        return set([ing['name'].lower() for ing in r['ingredients']])
    
    sets = [get_ing_set(r) for r in recipes]
    similarities = []
    for i in range(len(sets)):
        for j in range(i+1, len(sets)):
            intersection = len(sets[i].intersection(sets[j]))
            union = len(sets[i].union(sets[j]))
            sim = intersection / union if union > 0 else 0
            similarities.append(sim)
    avg_sim = sum(similarities) / len(similarities) if similarities else 0
    
    if avg_sim > 0.5:
        return 0.0, 10.0
    elif avg_sim > 0.3:
        return 5.0, 10.0
    else:
        return 10.0, 10.0

def get_quality_band(score: int) -> str:
    if score >= 90: return "Excellent"
    if score >= 80: return "Good"
    if score >= 70: return "Acceptable"
    return "Needs Improvement"

def calculate_quality_score(recipes, request: MealRequest):
    b, l, d = recipes
    actual_cal, actual_prot = calculate_meal_nutrition(b, l, d)
    
    scores = {
        "calories": calculate_calorie_score(actual_cal, request.calorie_target),
        "protein": calculate_protein_score(actual_prot, request.protein_target),
        "cuisine": calculate_cuisine_score(recipes, request.preferred_cuisine),
        "preferred_ingredients": calculate_preferred_ingredient_score(recipes, request.preferred_ingredients),
        "disliked_ingredients": calculate_disliked_ingredient_score(recipes, request.disliked_ingredients),
        "meal_suitability": calculate_meal_suitability_score(recipes, ["breakfast", "lunch", "dinner"]),
        "diversity": calculate_diversity_score(recipes)
    }
    
    total_earned = 0.0
    total_possible = 0.0
    breakdown = {}
    improvements = []
    
    for key, (earned, possible) in scores.items():
        if earned is not None:
            total_earned += earned
            total_possible += possible
            breakdown[key] = round(earned, 2)
            
            if earned < possible * 0.7:
                if key == "calories":
                    improvements.append("Calories are significantly off from the target.")
                elif key == "protein":
                    improvements.append("Protein is below the target.")
                elif key == "cuisine":
                    improvements.append("The plan does not sufficiently match the preferred region/cuisine.")
                elif key == "preferred_ingredients":
                    improvements.append("The plan contains few preferred ingredients.")
                elif key == "disliked_ingredients":
                    improvements.append("A disliked ingredient appears in the plan.")
                elif key == "meal_suitability":
                    improvements.append("Some meals do not match their intended slot (e.g., breakfast food for dinner).")
                elif key == "diversity":
                    improvements.append("Recipes have high ingredient overlap.")
        else:
            breakdown[key] = None
            
    if total_possible == 0:
        final_score = 100
    else:
        final_score = int((total_earned / total_possible) * 100)
        
    return final_score, get_quality_band(final_score), breakdown, improvements

def analyze_dimensions(breakdown: dict) -> Tuple[list, list]:
    weak = []
    strong = []
    
    if breakdown.get("calories") is not None:
        if breakdown["calories"] < 20: weak.append("Calories")
        else: strong.append("Calories")
        
    if breakdown.get("protein") is not None:
        if breakdown["protein"] < 16: weak.append("Protein")
        else: strong.append("Protein")
        
    if breakdown.get("cuisine") is not None:
        if breakdown["cuisine"] < 10: weak.append("Preferred Cuisine")
        else: strong.append("Preferred Cuisine")
        
    if breakdown.get("preferred_ingredients") is not None:
        if breakdown["preferred_ingredients"] < 5: weak.append("Preferred Ingredients")
        else: strong.append("Preferred Ingredients")
        
    if breakdown.get("disliked_ingredients") is not None:
        if breakdown["disliked_ingredients"] < 5: weak.append("Disliked Ingredients")
        else: strong.append("Disliked Ingredients")
        
    if breakdown.get("meal_suitability") is not None:
        if breakdown["meal_suitability"] < 7: weak.append("Meal Suitability")
        else: strong.append("Meal Suitability")
        
    if breakdown.get("diversity") is not None:
        if breakdown["diversity"] < 7: weak.append("Diversity")
        else: strong.append("Diversity")
        
    return weak, strong

def evaluate_meal_plan(candidate_args: dict, request: MealRequest, prep_time_limit: int) -> dict:
    b_name = candidate_args.get("breakfast_recipe_name")
    l_name = candidate_args.get("lunch_recipe_name")
    d_name = candidate_args.get("dinner_recipe_name")
    
    empty_quality = {
        "quality_score": 0,
        "quality_band": "Invalid",
        "breakdown": {},
        "improvements": []
    }
    
    if not b_name or not l_name or not d_name:
        return {"hard_constraints": {"passed": False, "errors": ["Must provide breakfast, lunch, and dinner recipe names."]}, **empty_quality}

    b_recipe = get_recipe_by_name(b_name)
    l_recipe = get_recipe_by_name(l_name)
    d_recipe = get_recipe_by_name(d_name)
    
    errors = []
    if not b_recipe:
        errors.append(f"Breakfast recipe '{b_name}' not found in knowledge base.")
    if not l_recipe:
        errors.append(f"Lunch recipe '{l_name}' not found in knowledge base.")
    if not d_recipe:
        errors.append(f"Dinner recipe '{d_name}' not found in knowledge base.")
        
    if errors:
        return {"hard_constraints": {"passed": False, "errors": errors}, **empty_quality}
        
    constraint_errors = check_hard_constraints(b_recipe, l_recipe, d_recipe, request, prep_time_limit)
    if constraint_errors:
        return {"hard_constraints": {"passed": False, "errors": constraint_errors}, **empty_quality}
        
    recipes = [b_recipe, l_recipe, d_recipe]
    score, band, breakdown, improvements = calculate_quality_score(recipes, request)
    
    return {
        "hard_constraints": {"passed": True, "errors": []},
        "quality_score": score,
        "quality_band": band,
        "breakdown": breakdown,
        "improvements": improvements
    }

def format_recipe(r):
    return {
        "name": r["name"],
        "description": r["description"],
        "region": r.get("region", ""),
        "cuisine": r.get("cuisine", ""),
        "calories": r["nutrition"]["calories"],
        "protein_g": r["nutrition"]["protein_g"],
        "prep_minutes": r["prep_minutes"],
        "cook_minutes": r.get("cook_minutes", 0),
        "spice_level": r.get("spice_level", ""),
        "servings": r.get("servings", 1),
        "tags": r.get("tags", []),
        "ingredients": r["ingredients"],
        "nutrition": r["nutrition"],
        "instructions": r["instructions"]
    }

def generate_agentic_meal_plan(request: MealRequest) -> MealPlanResponse:
    prep_time = extract_time_minutes(request.time)
    
    best_candidate = None
    best_candidate_score = -1
    final_plan_args = None
    evaluated_candidates = set()
    
    messages = [
        {"role": "system", "content": "You are an expert AI meal planner. Your goal is to generate a personalized meal plan adhering to hard constraints and optimizing for user preferences. You MUST use the search_recipes tool to find valid recipes, and then use the submit_meal_plan tool. If evaluating a revision, actively correct the weak dimensions while maintaining the strong dimensions."},
        {"role": "user", "content": f"Create a {request.goal} meal plan for a {request.diet} diet. Ensure each recipe prep time is under {prep_time} mins."}
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_recipes",
                "description": "Search the recipe knowledge base.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "diet": {"type": "string"},
                        "max_prep_time": {"type": "integer"},
                        "keywords": {"type": "string"},
                        "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner"]}
                    },
                    "required": ["diet", "max_prep_time", "keywords", "meal_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "submit_meal_plan",
                "description": "Submit candidate recipes to be evaluated. Call this ONLY when you have found valid recipes for all 3 meals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "breakfast_recipe_name": {"type": "string"},
                        "lunch_recipe_name": {"type": "string"},
                        "dinner_recipe_name": {"type": "string"}
                    },
                    "required": ["breakfast_recipe_name", "lunch_recipe_name", "dinner_recipe_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "terminate_plan",
                "description": "Call this tool if you cannot find valid recipes that meet the HARD constraints (diet, max_prep_time) after searching. Do not hallucinate recipes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string", "description": "Explanation of why the plan cannot be completed."}
                    },
                    "required": ["reason"]
                }
            }
        }
    ]
    
    for attempt in range(MAX_REVISION_ATTEMPTS):
        completion = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            tools=tools,
            temperature=0.2,
            extra_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI Meal Planner"
            }
        )
        
        msg = completion.choices[0].message
        
        msg_dict = {"role": msg.role, "content": msg.content or ""}
        if msg.tool_calls:
            msg_dict["tool_calls"] = [{"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}} for t in msg.tool_calls]
        messages.append(msg_dict)
        
        if not msg.tool_calls:
            messages.append({"role": "user", "content": "You must use tools. Search for recipes and then submit a meal plan."})
            continue
            
        plan_submitted = False
        
        for tool_call in msg.tool_calls:
            try:
                args = json.loads(tool_call.function.arguments)
            except Exception:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": "Invalid JSON in tool arguments."})
                })
                continue
                
            if tool_call.function.name == "search_recipes":
                results = search_recipes(
                    query=args.get("keywords", ""),
                    max_prep_time=args.get("max_prep_time", prep_time),
                    diet=args.get("diet", request.diet),
                    meal_type=args.get("meal_type"),
                    limit=3,
                    allergies=request.allergies
                )
                
                formatted_results = []
                for r in results:
                    formatted_results.append({
                        "name": r["name"],
                        "total_time": r["prep_minutes"] + r.get("cook_minutes", 0),
                        "diets": r["diets"],
                        "meal_type": r["meal_type"],
                        "nutrition": r["nutrition"]
                    })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(formatted_results) if formatted_results else json.dumps({"error": "No recipes found."})
                })
                
            elif tool_call.function.name == "submit_meal_plan":
                candidate_sig = f"{args.get('breakfast_recipe_name')}|{args.get('lunch_recipe_name')}|{args.get('dinner_recipe_name')}"
                if candidate_sig in evaluated_candidates:
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"status": "duplicate"})})
                    continue
                evaluated_candidates.add(candidate_sig)
                
                eval_result = evaluate_meal_plan(args, request, prep_time)
                
                if eval_result["hard_constraints"]["passed"]:
                    score = eval_result["quality_score"]
                    is_improvement = not best_candidate or score > best_candidate_score
                    if is_improvement:
                        best_candidate = args
                        best_candidate_score = score
                        
                    if score >= 80:
                        final_plan_args = args
                        plan_submitted = True
                        break
                    else:
                        weak_dims, strong_dims = analyze_dimensions(eval_result["breakdown"])
                        
                        if is_improvement:
                            msg_text = f"Your new plan scored {score}/100, which is an IMPROVEMENT and is now the best valid plan. However, it is still below the threshold (80). Please search for alternatives that specifically improve the weak areas, while preserving the strong areas."
                        else:
                            msg_text = f"Your new plan scored {score}/100, which is LOWER than the current best ({best_candidate_score}/100). The new plan has been rejected. Please review the weak dimensions and search for better alternatives."
                            
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({
                                "status": "passed_but_suboptimal",
                                "quality_score": score,
                                "quality_band": eval_result["quality_band"],
                                "weak_dimensions": weak_dims,
                                "strong_dimensions": strong_dims,
                                "improvements_needed": eval_result["improvements"],
                                "message": msg_text
                            })
                        })
                else:
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(eval_result)})
                    
            elif tool_call.function.name == "terminate_plan":
                raise ImpossibleConstraintsError(args.get("reason", "Impossible constraints"))
        
        if plan_submitted:
            break
            
    if not final_plan_args:
        if best_candidate:
            print(f"Agent failed to reach threshold, falling back to best candidate (score {best_candidate_score})")
            final_plan_args = best_candidate
        else:
            raise Exception("Agent failed to produce a valid meal plan within the maximum number of iterations.")
        
    b_recipe = get_recipe_by_name(final_plan_args["breakfast_recipe_name"])
    l_recipe = get_recipe_by_name(final_plan_args["lunch_recipe_name"])
    d_recipe = get_recipe_by_name(final_plan_args["dinner_recipe_name"])
    
    total_cal, total_prot = calculate_meal_nutrition(b_recipe, l_recipe, d_recipe)
    
    summary = f"Personalized {request.diet} plan ({total_cal} kcal, {total_prot}g protein) optimized for {request.goal}. "
    shopping = [ing["name"] for ing in b_recipe["ingredients"][:2] + l_recipe["ingredients"][:2] + d_recipe["ingredients"][:2]]
    
    final_response = MealPlanResponse(
        summary=summary,
        meals=DailyMeals(
            breakfast=MealDetails(**format_recipe(b_recipe)),
            lunch=MealDetails(**format_recipe(l_recipe)),
            dinner=MealDetails(**format_recipe(d_recipe))
        ),
        tips=["Drink plenty of water", "Stick to your schedule"],
        shopping_focus=list(dict.fromkeys(shopping))
    )
    
    return final_response
