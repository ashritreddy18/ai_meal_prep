from pydantic import BaseModel
from typing import List, Optional

class MealRequest(BaseModel):
    goal: str
    diet: str
    time: str
    allergies: List[str] = []
    calorie_target: int = 0
    protein_target: int = 0
    preferred_cuisine: str = ""
    disliked_ingredients: List[str] = []
    preferred_ingredients: List[str] = []

class NutritionInfo(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float

class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str

class MealDetails(BaseModel):
    name: str
    description: str
    region: str
    cuisine: str
    calories: int
    protein_g: float
    prep_minutes: int
    cook_minutes: int
    spice_level: str
    servings: int
    tags: List[str]
    ingredients: List[Ingredient]
    nutrition: NutritionInfo
    instructions: List[str]

class DailyMeals(BaseModel):
    breakfast: MealDetails
    lunch: MealDetails
    dinner: MealDetails

class MealPlanResponse(BaseModel):
    summary: str
    meals: DailyMeals
    tips: List[str]
    shopping_focus: List[str]

# --- Tool Calling & Agentic Workflow Schemas ---

class SearchRecipesInput(BaseModel):
    diet: str
    max_prep_time: int
    keywords: str
    meal_type: str

class SubmitMealPlanInput(BaseModel):
    breakfast_recipe_name: str
    lunch_recipe_name: str
    dinner_recipe_name: str

class QualityBreakdown(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    cuisine: Optional[float] = None
    preferred_ingredients: Optional[float] = None
    disliked_ingredients: Optional[float] = None
    meal_suitability: Optional[float] = None
    diversity: Optional[float] = None

class HardConstraintsResult(BaseModel):
    passed: bool
    errors: List[str]

class EvaluationResult(BaseModel):
    hard_constraints: HardConstraintsResult
    quality_score: int
    quality_band: str
    breakdown: QualityBreakdown
    improvements: List[str]