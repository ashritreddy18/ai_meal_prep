import json
import os
import random
import re
import socket
import time

# Ensure fast IPv4 resolution on macOS to prevent IPv6 connection timeouts
_old_getaddrinfo = socket.getaddrinfo
def _getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _old_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _getaddrinfo_ipv4

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas import MealRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import generate_agentic_meal_plan, ImpossibleConstraintsError

app = FastAPI(title="AI Meal Planner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rich Indian Meal Database for Instant Generation (< 50ms)
MEAL_CATALOG = {
    "vegetarian": {
        "breakfast": [
            {
                "name": "Moong Dal & Paneer Cheela",
                "description": "High-protein savory lentil pancake filled with spiced grated paneer and herbs.",
                "prep_minutes": 15,
                "base_cal": 380, "base_prot": 22, "base_carb": 40, "base_fat": 14, "base_fib": 7,
                "ingredients": [
                    {"name": "Moong Dal (soaked)", "quantity_g": 80},
                    {"name": "Paneer (grated)", "quantity_g": 60},
                    {"name": "Spinach & Chillies", "quantity_g": 30},
                    {"name": "Oil / Ghee", "quantity_g": 8}
                ],
                "instructions": [
                    "Blend soaked moong dal into a smooth batter with green chillies.",
                    "Pour batter onto a hot tawa and spread thinly in circles.",
                    "Top with grated paneer and spinach, cook until golden crisp on both sides."
                ]
            },
            {
                "name": "Sprouted Moong & Oats Upma",
                "description": "Nutritious fiber-rich upma cooked with sprouted mung beans and fresh coriander.",
                "prep_minutes": 12,
                "base_cal": 340, "base_prot": 16, "base_carb": 48, "base_fat": 8, "base_fib": 9,
                "ingredients": [
                    {"name": "Rolled Oats", "quantity_g": 60},
                    {"name": "Sprouted Moong", "quantity_g": 60},
                    {"name": "Onion & Carrots", "quantity_g": 40},
                    {"name": "Mustard Seeds & Curry Leaves", "quantity_g": 5}
                ],
                "instructions": [
                    "Temper mustard seeds, curry leaves, and onions in 1 tsp oil.",
                    "Add sprouted moong, chopped carrots, and 1 cup water; boil for 3 mins.",
                    "Stir in rolled oats and cook until soft and fragrant."
                ]
            },
            {
                "name": "Besan Chilla with Mint Chutney",
                "description": "Quick savory chickpea flour pancake spiced with ajwain, onions, and tomatoes.",
                "prep_minutes": 10,
                "base_cal": 330, "base_prot": 15, "base_carb": 44, "base_fat": 9, "base_fib": 6,
                "ingredients": [
                    {"name": "Besan (Gram Flour)", "quantity_g": 70},
                    {"name": "Onion & Tomato", "quantity_g": 40},
                    {"name": "Fresh Mint Chutney", "quantity_g": 20},
                    {"name": "Oil", "quantity_g": 7}
                ],
                "instructions": [
                    "Whisk besan with water, salt, ajwain, chopped onion, and tomato into a medium batter.",
                    "Pour onto a greased pan and cook both sides until golden brown.",
                    "Serve fresh with homemade mint-coriander chutney."
                ]
            }
        ],
        "lunch": [
            {
                "name": "Chana Masala with Brown Rice & Dahi",
                "description": "Rich chickpea curry simmered in onion-tomato masala with brown basmati rice.",
                "prep_minutes": 25,
                "base_cal": 560, "base_prot": 24, "base_carb": 78, "base_fat": 12, "base_fib": 12,
                "ingredients": [
                    {"name": "Kabuli Chana (boiled)", "quantity_g": 130},
                    {"name": "Brown Basmati Rice", "quantity_g": 140},
                    {"name": "Fresh Low-fat Curd", "quantity_g": 100},
                    {"name": "Tomato Onion Masala", "quantity_g": 50}
                ],
                "instructions": [
                    "Sauté onions, ginger-garlic paste, and tomato puree with chana masala spices.",
                    "Add boiled chickpeas with a splash of water and simmer for 10-12 minutes.",
                    "Serve hot alongside steamed brown rice and fresh cooling curd."
                ]
            },
            {
                "name": "Rajma Masala with Multigrain Phulka",
                "description": "Classic North Indian red kidney bean curry paired with whole wheat phulkas.",
                "prep_minutes": 25,
                "base_cal": 540, "base_prot": 22, "base_carb": 74, "base_fat": 11, "base_fib": 11,
                "ingredients": [
                    {"name": "Rajma (boiled)", "quantity_g": 140},
                    {"name": "Multigrain Roti", "quantity_g": 60},
                    {"name": "Cucumber & Tomato Salad", "quantity_g": 80},
                    {"name": "Ghee", "quantity_g": 5}
                ],
                "instructions": [
                    "Prepare spicy tomato gravy with cumin, coriander, and garam masala.",
                    "Add cooked kidney beans and simmer until gravy turns thick and aromatic.",
                    "Serve warm with 2 soft multigrain phulkas and fresh salad."
                ]
            }
        ],
        "dinner": [
            {
                "name": "Paneer Bhurji with Bajra Roti",
                "description": "Crumble paneer sautéed with bell peppers, tomatoes, and pearl millet rotis.",
                "prep_minutes": 18,
                "base_cal": 490, "base_prot": 26, "base_carb": 38, "base_fat": 22, "base_fib": 7,
                "ingredients": [
                    {"name": "Fresh Paneer", "quantity_g": 120},
                    {"name": "Capsicum & Tomatoes", "quantity_g": 60},
                    {"name": "Bajra Roti", "quantity_g": 50},
                    {"name": "Oil / Butter", "quantity_g": 8}
                ],
                "instructions": [
                    "Sauté chopped onions, green chillies, and capsicum in 1 tsp oil.",
                    "Add spices, tomatoes, and crumbled paneer; cook for 4-5 minutes.",
                    "Serve hot with freshly roasted bajra rotis."
                ]
            },
            {
                "name": "Tofu & Vegetable Curry with Moong Dal",
                "description": "High-protein tofu cubes cooked with broccoli and carrots alongside yellow dal.",
                "prep_minutes": 20,
                "base_cal": 440, "base_prot": 25, "base_carb": 40, "base_fat": 16, "base_fib": 8,
                "ingredients": [
                    {"name": "Tofu Cubes", "quantity_g": 120},
                    {"name": "Broccoli & Peppers", "quantity_g": 100},
                    {"name": "Moong Dal (cooked)", "quantity_g": 100},
                    {"name": "Olive Oil", "quantity_g": 6}
                ],
                "instructions": [
                    "Pan-sear tofu cubes until light golden.",
                    "Toss vegetables and tofu with turmeric, cumin, and chaat masala.",
                    "Enjoy as a light, protein-dense dinner bowl with moong dal."
                ]
            }
        ]
    },
    "non-vegetarian": {
        "breakfast": [
            {
                "name": "Masala Egg Scramble & Whole Grain Toast",
                "description": "Spiced 3-egg bhurji cooked with onions, green chillies, and toasted whole grain bread.",
                "prep_minutes": 10,
                "base_cal": 420, "base_prot": 26, "base_carb": 30, "base_fat": 18, "base_fib": 4,
                "ingredients": [
                    {"name": "Whole Eggs", "quantity_g": 150},
                    {"name": "Whole Grain Bread", "quantity_g": 60},
                    {"name": "Onion & Chillies", "quantity_g": 30},
                    {"name": "Butter", "quantity_g": 7}
                ],
                "instructions": [
                    "Whisk eggs with chopped onions, tomatoes, coriander, and red chili powder.",
                    "Scramble in melted butter over medium heat for 3-4 minutes.",
                    "Serve hot with toasted whole grain bread slices."
                ]
            },
            {
                "name": "Egg White Omelette with Spinach & Mushroom",
                "description": "Fluffy 4-egg white omelette folded with sautéed spinach and button mushrooms.",
                "prep_minutes": 12,
                "base_cal": 310, "base_prot": 28, "base_carb": 18, "base_fat": 9, "base_fib": 4,
                "ingredients": [
                    {"name": "Egg Whites", "quantity_g": 160},
                    {"name": "Spinach & Mushrooms", "quantity_g": 60},
                    {"name": "Brown Toast", "quantity_g": 35},
                    {"name": "Olive Oil", "quantity_g": 6}
                ],
                "instructions": [
                    "Sauté mushrooms and spinach in 1 tsp olive oil until tender.",
                    "Pour beaten egg whites over vegetables and cook until firm.",
                    "Fold and serve alongside warm brown toast."
                ]
            }
        ],
        "lunch": [
            {
                "name": "Chicken Tikka & Basmati Rice Bowl",
                "description": "Tandoori spiced grilled chicken breast served over fluffy rice with mint curd.",
                "prep_minutes": 22,
                "base_cal": 610, "base_prot": 44, "base_carb": 64, "base_fat": 14, "base_fib": 5,
                "ingredients": [
                    {"name": "Chicken Breast Cubes", "quantity_g": 180},
                    {"name": "Basmati Rice (cooked)", "quantity_g": 160},
                    {"name": "Cucumber Mint Raita", "quantity_g": 80},
                    {"name": "Tikka Spice Marinade", "quantity_g": 30}
                ],
                "instructions": [
                    "Marinate chicken in curd, tikka masala, garlic, and lemon for 10 minutes.",
                    "Pan-grill on high flame for 8-10 minutes until juicy and charred.",
                    "Serve with steamed basmati rice and fresh mint raita."
                ]
            },
            {
                "name": "Kerala Fish Curry with Whole Wheat Phulka",
                "description": "Tamarind and coconut spiced fish curry served with hot phulkas and green salad.",
                "prep_minutes": 20,
                "base_cal": 520, "base_prot": 36, "base_carb": 46, "base_fat": 15, "base_fib": 6,
                "ingredients": [
                    {"name": "Kingfish / Rohu Fillet", "quantity_g": 160},
                    {"name": "Whole Wheat Roti", "quantity_g": 60},
                    {"name": "Light Coconut Gravy", "quantity_g": 60},
                    {"name": "Green Salad", "quantity_g": 60}
                ],
                "instructions": [
                    "Temper mustard seeds, curry leaves, and garlic in oil.",
                    "Add tamarind juice, chilli powder, and light coconut milk.",
                    "Poach fish fillets for 7 minutes and serve warm with phulkas."
                ]
            }
        ],
        "dinner": [
            {
                "name": "Chicken Sukka & Millet Roti",
                "description": "Dry roasted spiced chicken cooked with curry leaves paired with bajra rotis.",
                "prep_minutes": 20,
                "base_cal": 530, "base_prot": 40, "base_carb": 42, "base_fat": 16, "base_fib": 7,
                "ingredients": [
                    {"name": "Boneless Chicken", "quantity_g": 160},
                    {"name": "Bajra Roti", "quantity_g": 50},
                    {"name": "Onion & Roasted Coconut Spice", "quantity_g": 40},
                    {"name": "Ghee / Oil", "quantity_g": 8}
                ],
                "instructions": [
                    "Sauté onions and chicken with roasted coconut-coriander spice mix.",
                    "Cook uncovered on medium heat until chicken turns tender and dry.",
                    "Serve with warm roasted bajra roti."
                ]
            },
            {
                "name": "Grilled Fish Tikka & Stir-Fried Veggies",
                "description": "Lean grilled fish marinated in ajwain and lemon with sautéed broccoli and peppers.",
                "prep_minutes": 15,
                "base_cal": 420, "base_prot": 38, "base_carb": 18, "base_fat": 13, "base_fib": 5,
                "ingredients": [
                    {"name": "White Fish Fillet", "quantity_g": 170},
                    {"name": "Broccoli & Bell Peppers", "quantity_g": 120},
                    {"name": "Ajwain Lemon Marinade", "quantity_g": 20},
                    {"name": "Olive Oil", "quantity_g": 6}
                ],
                "instructions": [
                    "Coat fish in ajwain, lemon juice, turmeric, and salt.",
                    "Pan-grill fish for 3-4 minutes per side until flaky.",
                    "Serve with lightly sautéed garlic broccoli and peppers."
                ]
            }
        ]
    }
}

# Duplicate eggetarian and vegan aliases for complete coverage
MEAL_CATALOG["eggetarian"] = {
    "breakfast": MEAL_CATALOG["non-vegetarian"]["breakfast"],
    "lunch": MEAL_CATALOG["vegetarian"]["lunch"],
    "dinner": MEAL_CATALOG["non-vegetarian"]["breakfast"] + MEAL_CATALOG["vegetarian"]["dinner"]
}

MEAL_CATALOG["vegan"] = {
    "breakfast": [MEAL_CATALOG["vegetarian"]["breakfast"][1], MEAL_CATALOG["vegetarian"]["breakfast"][2]],
    "lunch": [MEAL_CATALOG["vegetarian"]["lunch"][0], MEAL_CATALOG["vegetarian"]["lunch"][1]],
    "dinner": [MEAL_CATALOG["vegetarian"]["dinner"][1]]
}


def generate_instant_meal_plan(goal: str, diet: str, time_avail: str) -> dict:
    diet_key = diet.strip().lower()
    if diet_key not in MEAL_CATALOG:
        diet_key = "vegetarian"

    cat = MEAL_CATALOG[diet_key]

    b_item = random.choice(cat["breakfast"])
    l_item = random.choice(cat["lunch"])
    d_item = random.choice(cat["dinner"])

    # Macro multipliers based on goal
    goal_key = goal.strip().lower()
    cal_mult = 1.15 if "muscle" in goal_key else (0.85 if "fat" in goal_key or "loss" in goal_key else 1.0)
    prot_mult = 1.25 if "muscle" in goal_key else (1.1 if "fat" in goal_key else 1.0)

    def adjust_meal(meal_dict):
        c = int(meal_dict["base_cal"] * cal_mult)
        p = int(meal_dict["base_prot"] * prot_mult)
        cb = int(meal_dict["base_carb"] * (0.85 if "fat" in goal_key else 1.0))
        f = int(meal_dict["base_fat"] * (1.1 if "muscle" in goal_key else 0.9))
        fb = meal_dict["base_fib"]
        return {
            "name": meal_dict["name"],
            "description": meal_dict["description"],
            "calories": c,
            "protein_g": p,
            "prep_minutes": meal_dict["prep_minutes"],
            "ingredients": meal_dict["ingredients"],
            "nutrition": {
                "calories": c,
                "protein_g": p,
                "carbs_g": cb,
                "fat_g": f,
                "fiber_g": fb
            },
            "instructions": meal_dict["instructions"]
        }

    b_meal = adjust_meal(b_item)
    l_meal = adjust_meal(l_item)
    d_meal = adjust_meal(d_item)

    total_cal = b_meal["calories"] + l_meal["calories"] + d_meal["calories"]
    total_prot = b_meal["protein_g"] + l_meal["protein_g"] + d_meal["protein_g"]

    summary = f"Personalized Indian {diet.capitalize()} plan ({total_cal} kcal, {total_prot}g protein) optimized for {goal}."

    tips_pool = [
        "Drink at least 3 liters of water throughout the day to support metabolism.",
        "Include fresh cucumber or radish salad with lunch for natural fiber.",
        "Maintain regular meal timing and finish dinner at least 2 hours before bed."
    ]

    shopping = [ing["name"] for ing in b_meal["ingredients"][:2] + l_meal["ingredients"][:2] + d_meal["ingredients"][:2]]

    return {
        "summary": summary,
        "meals": {
            "breakfast": b_meal,
            "lunch": l_meal,
            "dinner": d_meal
        },
        "tips": tips_pool,
        "shopping_focus": list(dict.fromkeys(shopping))
    }


@app.get("/")
def read_root():
    return {"message": "AI Meal Planner API is running 🚀"}


@app.get("/health")
def health_check():
    api_key = os.getenv("OPENROUTER_API_KEY")
    return {
        "status": "ok",
        "service": "ai-meal-planner",
        "openrouter_api_key_set": bool(api_key),
    }


@app.post("/generate-meal")
def generate_meal(meal_request: MealRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if api_key:
        try:
            # New Agentic RAG Workflow
            meal_plan_response = generate_agentic_meal_plan(meal_request)
            return {"meal_plan": meal_plan_response.model_dump()}
        except ImpossibleConstraintsError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"Agentic RAG generation failed, falling back: {e}")

    # Sub-10ms instant high-speed generator fallback
    meal_plan = generate_instant_meal_plan(meal_request.goal, meal_request.diet, meal_request.time)
    return {"meal_plan": meal_plan}
