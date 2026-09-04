import os
import json
from openai import OpenAI
from pydantic import ValidationError

from schemas import MealRequest, MealPlanResponse, DailyMeals, MealDetails, NutritionInfo, Ingredient
from rag import search_recipes, RECIPES_PATH

class ImpossibleConstraintsError(Exception):
    pass

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

def check_recipe_constraints(breakfast, lunch, dinner, request: MealRequest, prep_time_limit: int):
    errors = []
    
    # Check Time
    if breakfast['prep_minutes'] + breakfast.get('cook_minutes', 0) > prep_time_limit:
        errors.append(f"Breakfast prep+cook time ({breakfast['prep_minutes']+breakfast.get('cook_minutes', 0)}m) exceeds limit ({prep_time_limit}m).")
    if lunch['prep_minutes'] + lunch.get('cook_minutes', 0) > prep_time_limit:
        errors.append(f"Lunch prep+cook time ({lunch['prep_minutes']+lunch.get('cook_minutes', 0)}m) exceeds limit ({prep_time_limit}m).")
    if dinner['prep_minutes'] + dinner.get('cook_minutes', 0) > prep_time_limit:
        errors.append(f"Dinner prep+cook time ({dinner['prep_minutes']+dinner.get('cook_minutes', 0)}m) exceeds limit ({prep_time_limit}m).")
        
    # Check Diet
    req_diet = request.diet.lower()
    if req_diet not in [d.lower() for d in breakfast['diets']]:
        errors.append(f"Breakfast '{breakfast['name']}' is not {req_diet}.")
    if req_diet not in [d.lower() for d in lunch['diets']]:
        errors.append(f"Lunch '{lunch['name']}' is not {req_diet}.")
    if req_diet not in [d.lower() for d in dinner['diets']]:
        errors.append(f"Dinner '{dinner['name']}' is not {req_diet}.")

    # Duplicate check
    names = [breakfast['name'], lunch['name'], dinner['name']]
    if len(set(names)) != 3:
        errors.append("You selected the same recipe for multiple meals.")

    return errors

def evaluate_meal_plan(candidate_args: dict, request: MealRequest, prep_time_limit: int):
    b_name = candidate_args.get("breakfast_recipe_name")
    l_name = candidate_args.get("lunch_recipe_name")
    d_name = candidate_args.get("dinner_recipe_name")
    
    errors = []
    if not b_name or not l_name or not d_name:
        return {"passed": False, "errors": ["Must provide breakfast, lunch, and dinner recipe names."]}

    b_recipe = get_recipe_by_name(b_name)
    l_recipe = get_recipe_by_name(l_name)
    d_recipe = get_recipe_by_name(d_name)
    
    if not b_recipe:
        errors.append(f"Breakfast recipe '{b_name}' not found in knowledge base.")
    if not l_recipe:
        errors.append(f"Lunch recipe '{l_name}' not found in knowledge base.")
    if not d_recipe:
        errors.append(f"Dinner recipe '{d_name}' not found in knowledge base.")
        
    if errors:
        return {"passed": False, "errors": errors}
        
    constraint_errors = check_recipe_constraints(b_recipe, l_recipe, d_recipe, request, prep_time_limit)
    if constraint_errors:
        return {"passed": False, "errors": constraint_errors}
        
    return {"passed": True, "errors": []}

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
        "tags": r.get("tags", []),
        "ingredients": r["ingredients"],
        "nutrition": r["nutrition"],
        "instructions": r["instructions"]
    }

def generate_agentic_meal_plan(request: MealRequest) -> MealPlanResponse:
    prep_time = extract_time_minutes(request.time)
    
    system_prompt = f"""You are an AI meal planning agent.
Your task is to plan 1 breakfast, 1 lunch, and 1 dinner for the user.

USER CONSTRAINTS:
Goal: {request.goal}
Diet: {request.diet}
Max Prep Time Per Meal: {prep_time} mins

RULES:
1. You MUST use the `search_recipes` tool to search our knowledge base for authentic Indian recipes.
2. DO NOT invent recipes. Only use recipes returned by `search_recipes`.
3. Once you have found 3 valid recipes that meet the diet and time constraints, use `submit_meal_plan` to evaluate them.
4. If your plan fails evaluation, you will receive errors. You must then search for different recipes and submit again.
5. If you cannot find valid recipes to meet the constraints after searching, you MUST call `terminate_plan` with a reason. Do not silently relax hard constraints (diet, max prep time).
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please start planning."}
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
    
    max_iterations = 6
    iterations = 0
    final_plan_args = None
    
    while iterations < max_iterations:
        iterations += 1
        
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
        
        # Serialize the message for appending
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
                print(f"Agent Action: Searching for {args.get('meal_type')} ({args.get('keywords')})")
                results = search_recipes(
                    query=args.get("keywords", ""),
                    max_prep_time=args.get("max_prep_time", prep_time),
                    diet=args.get("diet", request.diet),
                    meal_type=args.get("meal_type"),
                    limit=3
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
                
                if not formatted_results:
                    response_content = json.dumps({"error": "No suitable recipes found matching these constraints. Please relax soft constraints or change keywords. If hard constraints cannot be met, call terminate_plan."})
                else:
                    response_content = json.dumps(formatted_results)
                    
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": response_content
                })
                
            elif tool_call.function.name == "submit_meal_plan":
                print(f"Agent Action: Submitting meal plan...")
                eval_result = evaluate_meal_plan(args, request, prep_time)
                
                if eval_result["passed"]:
                    print("Agent Evaluation: PASSED")
                    final_plan_args = args
                    plan_submitted = True
                    # Do not append tool response here, since we are breaking the loop
                    break
                else:
                    print(f"Agent Evaluation: FAILED. {eval_result['errors']}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(eval_result)
                    })
                    messages.append({
                        "role": "user",
                        "content": "Your meal plan failed evaluation. Read the errors above and use search_recipes to find different recipes."
                    })
                    
            elif tool_call.function.name == "terminate_plan":
                print(f"Agent Action: Terminated plan. Reason: {args.get('reason')}")
                raise ImpossibleConstraintsError(args.get("reason", "Impossible constraints"))
        
        if plan_submitted:
            break
            
    if not final_plan_args:
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
