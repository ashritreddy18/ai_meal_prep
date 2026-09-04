
import json
import os
import hashlib

def generate_recipe_id(name: str, region: str) -> str:
    unique_str = f"{name.lower().strip()}-{region.lower().strip()}"
    return hashlib.md5(unique_str.encode()).hexdigest()[:12]

INGREDIENT_MACROS = {
    "chicken": {"calories": 165, "protein_g": 31, "fat_g": 3.6, "carbs_g": 0},
    "mutton": {"calories": 294, "protein_g": 25, "fat_g": 21, "carbs_g": 0},
    "pork": {"calories": 242, "protein_g": 27, "fat_g": 14, "carbs_g": 0},
    "fish": {"calories": 105, "protein_g": 20, "fat_g": 2.7, "carbs_g": 0},
    "prawns": {"calories": 99, "protein_g": 24, "fat_g": 0.3, "carbs_g": 0.2},
    "moong dal": {"calories": 347, "protein_g": 24, "fat_g": 1.2, "carbs_g": 63},
    "fennel": {"calories": 345, "protein_g": 16, "fat_g": 15, "carbs_g": 52},
    "egg": {"calories": 155, "protein_g": 13, "fat_g": 11, "carbs_g": 1.1},
    "paneer": {"calories": 265, "protein_g": 18, "fat_g": 20, "carbs_g": 3.4},
    "mixed vegetables": {"calories": 65, "protein_g": 3, "fat_g": 0.5, "carbs_g": 13},
    "potato": {"calories": 77, "protein_g": 2, "fat_g": 0.1, "carbs_g": 17},
    "soya chunks": {"calories": 345, "protein_g": 52, "fat_g": 0.5, "carbs_g": 33},
    "mushroom": {"calories": 22, "protein_g": 3.1, "fat_g": 0.3, "carbs_g": 3.3},
    "rice": {"calories": 130, "protein_g": 2.7, "fat_g": 0.3, "carbs_g": 28},
    "basmati rice": {"calories": 130, "protein_g": 2.7, "fat_g": 0.3, "carbs_g": 28},
    "wheat flour": {"calories": 340, "protein_g": 13.2, "fat_g": 2.5, "carbs_g": 72},
    "gram flour": {"calories": 387, "protein_g": 22, "fat_g": 6.7, "carbs_g": 58},
    "rice flour": {"calories": 366, "protein_g": 5.9, "fat_g": 1.4, "carbs_g": 80},
    "sorghum flour": {"calories": 339, "protein_g": 11, "fat_g": 3.3, "carbs_g": 75},
    "maize flour": {"calories": 365, "protein_g": 9.4, "fat_g": 4.7, "carbs_g": 74},
    "lentils": {"calories": 116, "protein_g": 9, "fat_g": 0.4, "carbs_g": 20},
    "toor dal": {"calories": 343, "protein_g": 22, "fat_g": 1.5, "carbs_g": 63},
    "urad dal": {"calories": 341, "protein_g": 25, "fat_g": 1.6, "carbs_g": 59},
    "chickpeas": {"calories": 164, "protein_g": 8.9, "fat_g": 2.6, "carbs_g": 27},
    "black chickpeas": {"calories": 164, "protein_g": 8.9, "fat_g": 2.6, "carbs_g": 27},
    "kidney beans": {"calories": 127, "protein_g": 8.7, "fat_g": 0.5, "carbs_g": 22},
    "bengal gram": {"calories": 360, "protein_g": 19, "fat_g": 6, "carbs_g": 60},
    "onion": {"calories": 40, "protein_g": 1.1, "fat_g": 0.1, "carbs_g": 9.3},
    "tomato": {"calories": 18, "protein_g": 0.9, "fat_g": 0.2, "carbs_g": 3.9},
    "tomato puree": {"calories": 38, "protein_g": 1.5, "fat_g": 0.2, "carbs_g": 9},
    "spinach": {"calories": 23, "protein_g": 2.9, "fat_g": 0.4, "carbs_g": 3.6},
    "mustard leaves": {"calories": 27, "protein_g": 2.9, "fat_g": 0.4, "carbs_g": 4.7},
    "capsicum": {"calories": 20, "protein_g": 0.9, "fat_g": 0.2, "carbs_g": 4.6},
    "cauliflower": {"calories": 25, "protein_g": 1.9, "fat_g": 0.3, "carbs_g": 5},
    "eggplant": {"calories": 25, "protein_g": 1, "fat_g": 0.2, "carbs_g": 6},
    "ladyfinger": {"calories": 33, "protein_g": 1.9, "fat_g": 0.2, "carbs_g": 7.5},
    "corn": {"calories": 86, "protein_g": 3.2, "fat_g": 1.2, "carbs_g": 19},
    "bamboo shoot": {"calories": 27, "protein_g": 2.6, "fat_g": 0.3, "carbs_g": 5.2},
    "green chilli": {"calories": 40, "protein_g": 2, "fat_g": 0.4, "carbs_g": 9},
    "king chilli": {"calories": 40, "protein_g": 2, "fat_g": 0.4, "carbs_g": 9},
    "garlic": {"calories": 149, "protein_g": 6.4, "fat_g": 0.5, "carbs_g": 33},
    "oil": {"calories": 884, "protein_g": 0, "fat_g": 100, "carbs_g": 0},
    "mustard oil": {"calories": 884, "protein_g": 0, "fat_g": 100, "carbs_g": 0},
    "sesame oil": {"calories": 884, "protein_g": 0, "fat_g": 100, "carbs_g": 0},
    "coconut oil": {"calories": 862, "protein_g": 0, "fat_g": 100, "carbs_g": 0},
    "ghee": {"calories": 900, "protein_g": 0, "fat_g": 100, "carbs_g": 0},
    "butter": {"calories": 717, "protein_g": 0.8, "fat_g": 81, "carbs_g": 0.1},
    "cream": {"calories": 345, "protein_g": 2, "fat_g": 37, "carbs_g": 2.8},
    "curd": {"calories": 98, "protein_g": 11, "fat_g": 4.3, "carbs_g": 3.4},
    "milk": {"calories": 42, "protein_g": 3.4, "fat_g": 1, "carbs_g": 5},
    "coconut milk": {"calories": 230, "protein_g": 2.3, "fat_g": 24, "carbs_g": 6},
    "coconut": {"calories": 354, "protein_g": 3.3, "fat_g": 33, "carbs_g": 15},
    "cashews": {"calories": 553, "protein_g": 18, "fat_g": 44, "carbs_g": 30},
    "peanuts": {"calories": 567, "protein_g": 26, "fat_g": 49, "carbs_g": 16},
    "sesame seeds": {"calories": 573, "protein_g": 17, "fat_g": 49, "carbs_g": 23},
    "poppy seeds": {"calories": 525, "protein_g": 18, "fat_g": 41, "carbs_g": 28},
    "tamarind": {"calories": 239, "protein_g": 2.8, "fat_g": 0.6, "carbs_g": 62},
    "jaggery": {"calories": 383, "protein_g": 0.4, "fat_g": 0.1, "carbs_g": 98},
    "vinegar": {"calories": 18, "protein_g": 0, "fat_g": 0, "carbs_g": 0},
    "poha": {"calories": 346, "protein_g": 6.6, "fat_g": 1.2, "carbs_g": 77},
    "tapioca pearls": {"calories": 358, "protein_g": 0.2, "fat_g": 0.02, "carbs_g": 89},
    "semolina": {"calories": 360, "protein_g": 12.6, "fat_g": 1.0, "carbs_g": 72},
    "noodles": {"calories": 138, "protein_g": 4.5, "fat_g": 2.1, "carbs_g": 25},
    "ginger garlic paste": {"calories": 70, "protein_g": 2.5, "fat_g": 0.5, "carbs_g": 15},
    "banana leaf": {"calories": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0}
}

def calculate_macros(ingredients):
    total_cal = 0.0
    total_pro = 0.0
    total_fat = 0.0
    total_car = 0.0
    total_fib = 0.0
    for item in ingredients:
        name = item["name"].lower()
        qty = item["quantity"]
        if name in INGREDIENT_MACROS:
            ratio = qty / 100.0
            total_cal += INGREDIENT_MACROS[name]["calories"] * ratio
            total_pro += INGREDIENT_MACROS[name]["protein_g"] * ratio
            total_fat += INGREDIENT_MACROS[name]["fat_g"] * ratio
            total_car += INGREDIENT_MACROS[name]["carbs_g"] * ratio
            total_fib += INGREDIENT_MACROS[name].get("fiber_g", 0.0) * ratio
        else:
            print(f"Warning: Macro data missing for '{item['name']}'")
    return {
        "calories": round(total_cal),
        "protein_g": round(total_pro, 1),
        "fat_g": round(total_fat, 1),
        "carbs_g": round(total_car, 1),
        "fiber_g": round(total_fib, 1)
    }

raw_recipes = [{'name': 'Masala Dosa', 'region': 'Karnataka', 'cuisine': 'South Indian', 'meal_type': 'Breakfast', 'prep_minutes': 20, 'cook_minutes': 15, 'spice_level': 'Medium', 'ingredients': [('Rice', 100), ('Urad Dal', 25), ('Potato', 100), ('Onion', 50), ('Oil', 15)], 'instructions': ['Soak rice and urad dal overnight, then grind into a smooth batter.', 'Boil and mash the potatoes, then sauté with onions, mustard seeds, and turmeric.', 'Spread the batter thinly on a hot griddle, drizzle with oil, and cook until crisp.', 'Place the potato masala in the center and fold the dosa over it.'], 'tags': ['dosa', 'crispy', 'staple']}, {'name': 'Idli Sambar', 'region': 'Tamil Nadu', 'cuisine': 'South Indian', 'meal_type': 'Breakfast', 'prep_minutes': 15, 'cook_minutes': 30, 'spice_level': 'Medium', 'ingredients': [('Rice', 100), ('Urad Dal', 30), ('Toor Dal', 50), ('Mixed Vegetables', 100), ('Tamarind', 10)], 'instructions': ['Ferment rice and dal batter, then steam in idli molds for 10-12 minutes.', 'Boil toor dal with turmeric until soft and mushy.', 'Cook mixed vegetables in tamarind extract with sambar powder.', 'Mix the cooked dal with the vegetables, temper with mustard seeds and curry leaves, and serve with hot idlis.'], 'tags': ['steamed', 'healthy', 'lentils']}, {'name': 'Pesarattu', 'region': 'Andhra Pradesh', 'cuisine': 'South Indian', 'meal_type': 'Breakfast', 'prep_minutes': 10, 'cook_minutes': 10, 'spice_level': 'High', 'ingredients': [('Moong Dal', 150), ('Onion', 50), ('Oil', 10)], 'instructions': ['Soak whole green moong dal overnight and grind with green chilies and ginger.', 'Finely chop onions and mix them into the batter or sprinkle on top.', 'Spread the batter on a hot tawa like a dosa.', 'Cook until crisp on both sides using a little oil.'], 'tags': ['protein-rich', 'crepe', 'spicy']}, {'name': 'Ven Pongal', 'region': 'Tamil Nadu', 'cuisine': 'South Indian', 'meal_type': 'Breakfast', 'prep_minutes': 5, 'cook_minutes': 25, 'spice_level': 'Mild', 'ingredients': [('Rice', 100), ('Moong Dal', 50), ('Ghee', 20), ('Cashews', 15)], 'instructions': ['Dry roast moong dal slightly, then wash it with rice.', 'Pressure cook rice and dal with enough water until very soft and mushy.', 'In a pan, heat ghee and temper cumin seeds, black peppercorns, curry leaves, and cashews.', 'Pour the tempering over the cooked rice-dal mixture and mix well.'], 'tags': ['comfort-food', 'ghee', 'mushy']}, {'name': 'Appam with Vegetable Stew', 'region': 'Kerala', 'cuisine': 'South Indian', 'meal_type': 'Breakfast', 'prep_minutes': 20, 'cook_minutes': 25, 'spice_level': 'Mild', 'ingredients': [('Rice', 100), ('Coconut', 50), ('Mixed Vegetables', 150), ('Coconut Oil', 10)], 'instructions': ['Blend soaked rice and grated coconut with a little yeast to make appam batter.', 'Allow batter to ferment, then cook in an appachatti to get lacey edges and a soft center.', 'For the stew, boil mixed vegetables (carrots, potatoes, peas) gently.', 'Simmer the vegetables in coconut milk with ginger, green chilies, and whole spices, then temper with coconut oil.'], 'tags': ['coconut', 'lacey', 'stew']}, {'name': 'Bisi Bele Bath', 'region': 'Karnataka', 'cuisine': 'South Indian', 'meal_type': 'Lunch', 'prep_minutes': 15, 'cook_minutes': 40, 'spice_level': 'Medium', 'ingredients': [('Rice', 100), ('Toor Dal', 75), ('Mixed Vegetables', 150), ('Tamarind', 20), ('Ghee', 15)], 'instructions': ['Cook rice and toor dal together until very soft.', 'Boil vegetables in tamarind water along with freshly ground bisi bele bath masala.', 'Combine the cooked rice, dal, and vegetable mixture, simmering until well blended.', 'Temper with mustard seeds, curry leaves, and cashews in generous amounts of ghee.'], 'tags': ['one-pot', 'spicy', 'lentils']}, {'name': 'Andhra Chilli Chicken', 'region': 'Andhra Pradesh', 'cuisine': 'South Indian', 'meal_type': 'Dinner', 'prep_minutes': 15, 'cook_minutes': 30, 'spice_level': 'High', 'ingredients': [('Chicken', 250), ('Onion', 100), ('Oil', 20), ('Ginger Garlic Paste', 15)], 'instructions': ['Marinate chicken pieces with turmeric, salt, and ginger garlic paste.', 'Heat oil and sauté finely chopped onions and slit green chilies until golden.', 'Add the marinated chicken and cook on high heat to sear.', 'Add freshly ground green chili paste, cover, and simmer until the chicken is tender and coated in the spicy green masala.'], 'tags': ['spicy', 'chicken', 'dry-fry']}, {'name': 'Hyderabadi Chicken Biryani', 'region': 'Telangana', 'cuisine': 'South Indian', 'meal_type': 'Dinner', 'prep_minutes': 60, 'cook_minutes': 45, 'spice_level': 'High', 'ingredients': [('Chicken', 300), ('Basmati Rice', 200), ('Onion', 100), ('Curd', 100), ('Ghee', 30)], 'instructions': ['Marinate raw chicken with yogurt, fried onions, mint, coriander, and biryani spices for at least an hour.', 'Partially boil basmati rice with whole spices until 70% cooked.', 'Layer the partially cooked rice over the raw marinated chicken in a heavy-bottomed pot.', 'Seal the pot with dough (dum) and cook on very low heat for 45 minutes until the chicken and rice are fully cooked together.'], 'tags': ['dum', 'fragrant', 'festive']}, {'name': 'Kerala Fish Curry (Meen Curry)', 'region': 'Kerala', 'cuisine': 'South Indian', 'meal_type': 'Dinner', 'prep_minutes': 15, 'cook_minutes': 25, 'spice_level': 'High', 'ingredients': [('Fish', 250), ('Onion', 50), ('Tomato', 50), ('Tamarind', 15), ('Coconut Oil', 15)], 'instructions': ['Soak kokum (kudampuli) or tamarind in warm water.', 'In an earthen pot, heat coconut oil and temper mustard seeds and fenugreek.', 'Sauté shallots, ginger, garlic, and curry leaves, then add red chili powder and coriander powder.', 'Add the tamarind water, bring to a boil, gently slide in the fish pieces, and simmer until cooked.'], 'tags': ['tangy', 'spicy', 'seafood']}, {'name': 'Gongura Mutton', 'region': 'Andhra Pradesh', 'cuisine': 'South Indian', 'meal_type': 'Dinner', 'prep_minutes': 20, 'cook_minutes': 60, 'spice_level': 'High', 'ingredients': [('Mutton', 300), ('Spinach', 100), ('Onion', 100), ('Oil', 20), ('Ginger Garlic Paste', 15)], 'instructions': ['Wash and pluck gongura (sorrel) leaves and sauté them until they melt into a paste.', 'Pressure cook mutton pieces with onions, turmeric, and ginger garlic paste until tender.', 'In a separate pan, heat oil, sauté onions, add the cooked mutton, and fry with spicy red chili powder.', 'Mix in the sour gongura paste and simmer until the oil separates on top.'], 'tags': ['tangy', 'meat', 'leafy']}, {'name': 'Avial', 'region': 'Kerala', 'cuisine': 'South Indian', 'meal_type': 'Lunch', 'prep_minutes': 15, 'cook_minutes': 20, 'spice_level': 'Mild', 'ingredients': [('Mixed Vegetables', 200), ('Coconut', 50), ('Curd', 50), ('Coconut Oil', 10)], 'instructions': ['Cut vegetables like yam, ash gourd, carrots, and drumsticks into long batons and boil with turmeric.', 'Grind grated coconut, green chilies, and cumin seeds into a coarse paste.', 'Add the coconut paste to the cooked vegetables and simmer gently.', 'Turn off the heat, mix in sour curd, and finish with a drizzle of raw coconut oil and fresh curry leaves.'], 'tags': ['coconut', 'healthy', 'festive']}, {'name': 'Chettinad Chicken', 'region': 'Tamil Nadu', 'cuisine': 'South Indian', 'meal_type': 'Dinner', 'prep_minutes': 20, 'cook_minutes': 35, 'spice_level': 'High', 'ingredients': [('Chicken', 250), ('Onion', 100), ('Tomato', 50), ('Coconut', 30), ('Oil', 20)], 'instructions': ['Dry roast coriander seeds, dried red chilies, fennel, and black stone flower, then grind with fresh coconut into a paste.', 'Heat oil and sauté onions, tomatoes, and ginger garlic paste.', 'Add the chicken pieces and fry until they change color.', 'Stir in the freshly ground Chettinad masala paste, add water, and simmer until the chicken is tender and the gravy is thick.'], 'tags': ['peppery', 'complex-spices', 'chicken']}, {'name': 'Medu Vada', 'region': 'Tamil Nadu', 'cuisine': 'South Indian', 'meal_type': 'Snack', 'prep_minutes': 10, 'cook_minutes': 20, 'spice_level': 'Medium', 'ingredients': [('Urad Dal', 150), ('Onion', 30), ('Oil', 30)], 'instructions': ['Soak urad dal for a few hours, then grind it with very little water into a thick, fluffy batter.', 'Mix finely chopped onions, green chilies, ginger, and curry leaves into the batter.', 'Wet your hands, take a portion of batter, make a hole in the center to form a doughnut shape.', 'Deep fry in hot oil until golden brown and crispy on the outside.'], 'tags': ['crispy', 'deep-fried', 'classic']}, {'name': 'Lemon Rice', 'region': 'Karnataka', 'cuisine': 'South Indian', 'meal_type': 'Lunch', 'prep_minutes': 10, 'cook_minutes': 15, 'spice_level': 'Medium', 'ingredients': [('Rice', 150), ('Peanuts', 30), ('Oil', 15), ('Onion', 30)], 'instructions': ['Cook the rice so the grains remain separate and let it cool.', 'Heat oil, temper mustard seeds, urad dal, chana dal, and roast the peanuts until crunchy.', 'Add turmeric, slit green chilies, and curry leaves.', 'Turn off the heat, squeeze fresh lemon juice, and gently fold in the cooked rice.'], 'tags': ['tangy', 'quick', 'travel-food']}, {'name': 'Curd Rice', 'region': 'Tamil Nadu', 'cuisine': 'South Indian', 'meal_type': 'Lunch', 'prep_minutes': 5, 'cook_minutes': 10, 'spice_level': 'Mild', 'ingredients': [('Rice', 100), ('Curd', 150), ('Milk', 50), ('Oil', 10)], 'instructions': ['Cook rice until it is very soft and slightly mushy, then mash it lightly.', 'Mix the cooled rice with fresh curd and a little milk to prevent it from turning too sour.', 'Heat oil and temper mustard seeds, urad dal, finely chopped ginger, and curry leaves.', 'Pour the tempering over the curd rice and mix well, garnishing with coriander leaves.'], 'tags': ['cooling', 'comfort-food', 'summer']}, {'name': 'Chole Bhature', 'region': 'Punjab', 'cuisine': 'North Indian', 'meal_type': 'Lunch', 'prep_minutes': 30, 'cook_minutes': 40, 'spice_level': 'Medium', 'ingredients': [('Chickpeas', 150), ('Wheat Flour', 150), ('Onion', 100), ('Tomato Puree', 50), ('Oil', 30)], 'instructions': ['Soak chickpeas overnight and pressure cook with a tea bag and whole spices until tender.', 'Sauté chopped onions, ginger garlic paste, and tomato puree, then add chole masala.', 'Add the boiled chickpeas and simmer until the gravy thickens.', 'Knead a soft dough from refined flour and yogurt, roll out disks, and deep fry until they puff up (bhature).'], 'tags': ['heavy', 'festive', 'popular']}, {'name': 'Dal Makhani', 'region': 'Punjab', 'cuisine': 'North Indian', 'meal_type': 'Dinner', 'prep_minutes': 20, 'cook_minutes': 120, 'spice_level': 'Mild', 'ingredients': [('Urad Dal', 100), ('Kidney Beans', 25), ('Tomato Puree', 100), ('Cream', 50), ('Butter', 30)], 'instructions': ['Soak whole black urad dal and rajma overnight, then pressure cook until completely soft.', 'In a heavy pot, melt butter, sauté ginger garlic paste and tomato puree until oil separates.', 'Add the cooked dal, mash it slightly, and simmer on very low heat for at least an hour.', 'Finish by stirring in fresh cream and a generous dollop of butter.'], 'tags': ['creamy', 'rich', 'lentils']}, {'name': 'Butter Chicken', 'region': 'Punjab', 'cuisine': 'North Indian', 'meal_type': 'Dinner', 'prep_minutes': 30, 'cook_minutes': 40, 'spice_level': 'Mild', 'ingredients': [('Chicken', 300), ('Tomato Puree', 150), ('Cream', 50), ('Butter', 40), ('Cashews', 20)], 'instructions': ['Marinate chicken in yogurt and spices, then grill or pan-fry until slightly charred (tikka).', 'Sauté pureed tomatoes with ginger, garlic, and cashew paste until reduced and fragrant.', 'Add generous amounts of butter and kasuri methi (dried fenugreek leaves) to the gravy.', 'Toss the grilled chicken pieces into the creamy tomato sauce and finish with heavy cream.'], 'tags': ['creamy', 'popular', 'sweet-tangy']}, {'name': 'Palak Paneer', 'region': 'North Indian', 'cuisine': 'North Indian', 'meal_type': 'Dinner', 'prep_minutes': 15, 'cook_minutes': 20, 'spice_level': 'Medium', 'ingredients': [('Spinach', 200), ('Paneer', 150), ('Onion', 50), ('Tomato', 50), ('Oil', 15)], 'instructions': ['Blanch spinach leaves in boiling water, shock in ice water, and puree into a smooth paste.', 'Sauté finely chopped onions and tomatoes with cumin, garlic, and green chilies.', 'Stir in the spinach puree and simmer gently for a few minutes (do not overcook to retain green color).', 'Add cubed paneer and finish with a splash of cream or butter.'], 'tags': ['healthy', 'leafy', 'iron-rich']}, {'name': 'Aloo Paratha', 'region': 'Punjab', 'cuisine': 'North Indian', 'meal_type': 'Breakfast', 'prep_minutes': 20, 'cook_minutes': 20, 'spice_level': 'Medium', 'ingredients': [('Wheat Flour', 150), ('Potato', 200), ('Ghee', 20), ('Onion', 30)], 'instructions': ['Boil and mash potatoes, then mix with chopped onions, green chilies, coriander, and spices.', 'Knead whole wheat flour into a soft dough and let it rest.', 'Roll out a small dough circle, place a generous scoop of potato filling, seal, and roll it out flat.', 'Cook the paratha on a hot tawa, applying ghee on both sides until crispy and golden brown.'], 'tags': ['stuffed-bread', 'comfort-food', 'filling']}, {'name': 'Rajma Chawal', 'region': 'North Indian', 'cuisine': 'North Indian', 'meal_type': 'Lunch', 'prep_minutes': 15, 'cook_minutes': 45, 'spice_level': 'Medium', 'ingredients': [('Kidney Beans', 150), ('Basmati Rice', 100), ('Onion', 100), ('Tomato Puree', 100), ('Oil', 20)], 'instructions': ['Soak kidney beans (rajma) overnight and pressure cook until soft.', 'In a pan, fry onions until brown, add ginger garlic paste, tomato puree, and spices to make a rich masala.', 'Mix the boiled rajma into the masala and simmer until the gravy thickens and coats the beans.', 'Serve the spicy rajma curry hot over steamed basmati rice.'], 'tags': ['comfort-food', 'beans', 'staple']}, {'name': 'Kadhai Paneer', 'region': 'North Indian', 'cuisine': 'North Indian', 'meal_type': 'Dinner', 'prep_minutes': 15, 'cook_minutes': 25, 'spice_level': 'High', 'ingredients': [('Paneer', 200), ('Capsicum', 100), ('Onion', 100), ('Tomato Puree', 100), ('Oil', 20)], 'instructions': ['Dry roast coriander seeds and dried red chilies, then crush them to make kadhai masala.', 'Cube the paneer, capsicum, and onions.', 'Sauté the onions and capsicum with tomato puree and the freshly ground kadhai masala.', 'Toss the paneer cubes in the spicy, thick gravy and cook for a few minutes until coated.'], 'tags': ['spicy', 'restaurant-style', 'stir-fry']}, {'name': 'Mutton Rogan Josh', 'region': 'Kashmir', 'cuisine': 'North Indian', 'meal_type': 'Dinner', 'prep_minutes': 15, 'cook_minutes': 60, 'spice_level': 'Medium', 'ingredients': [('Mutton', 300), ('Curd', 100), ('Oil', 20), ('Onion', 50), ('Ginger Garlic Paste', 15)], 'instructions': ['Heat oil and brown the mutton pieces along with whole spices.', 'Whisk curd with Kashmiri red chili powder, fennel powder, and dry ginger powder.', 'Add the spiced curd mixture to the mutton and stir continuously until it boils.', 'Cover and simmer on low heat for about an hour until the meat is tender and a red oil layer floats on top.'], 'tags': ['aromatic', 'kashmiri', 'slow-cooked']}, {'name': 'Aloo Gobi', 'region': 'North Indian', 'cuisine': 'North Indian', 'meal_type': 'Dinner', 'prep_minutes': 15, 'cook_minutes': 25, 'spice_level': 'Medium', 'ingredients': [('Potato', 150), ('Cauliflower', 150), ('Onion', 50), ('Tomato', 50), ('Oil', 15)], 'instructions': ['Cut potatoes into cubes and cauliflower into florets, and optionally shallow fry them.', 'Heat oil and temper cumin seeds, then sauté chopped onions, ginger, and garlic.', 'Add chopped tomatoes, turmeric, and coriander powder, cooking until soft.', 'Add the potatoes and cauliflower, cover, and cook until tender. Garnish with fresh coriander.'], 'tags': ['dry-curry', 'homestyle', 'everyday']}, {'name': 'Bhindi Masala', 'region': 'North Indian', 'cuisine': 'North Indian', 'meal_type': 'Lunch', 'prep_minutes': 10, 'cook_minutes': 20, 'spice_level': 'Medium', 'ingredients': [('Ladyfinger', 200), ('Onion', 100), ('Tomato', 50), ('Oil', 20)], 'instructions': ['Wash, completely dry, and chop the ladyfingers (okra) to prevent sliminess.', 'Heat oil and sauté the okra until slightly crispy, then remove from the pan.', 'In the same pan, fry sliced onions, tomatoes, and dry spices until the masala is cooked.', 'Add the fried okra back in, mix gently, and cook for 5 more minutes.'], 'tags': ['dry-curry', 'okra', 'homestyle']}, {'name': 'Misal Pav', 'region': 'Maharashtra', 'cuisine': 'Maharashtrian', 'meal_type': 'Breakfast', 'prep_minutes': 15, 'cook_minutes': 30, 'spice_level': 'High', 'ingredients': [('Mixed Vegetables', 150), ('Onion', 100), ('Tomato', 50), ('Oil', 20)], 'instructions': ['Sprout moth beans or matki and pressure cook them lightly.', 'Prepare a very spicy, watery gravy (kat/tarri) using a fiery red masala paste made of roasted onions and coconut.', 'Combine the sprouts with the spicy gravy.', 'Serve in a bowl topped with crunchy farsan/sev, raw onions, and a squeeze of lemon, with soft pav (bread) on the side.'], 'tags': ['spicy', 'street-food', 'sprouts']}, {'name': 'Vada Pav', 'region': 'Maharashtra', 'cuisine': 'Maharashtrian', 'meal_type': 'Snack', 'prep_minutes': 15, 'cook_minutes': 20, 'spice_level': 'High', 'ingredients': [('Potato', 200), ('Gram Flour', 100), ('Oil', 30), ('Onion', 20)], 'instructions': ['Mash boiled potatoes and temper with mustard seeds, curry leaves, garlic, and green chilies.', 'Form the potato mixture into balls, dip them in a thick gram flour batter, and deep fry until golden.', 'Slice a soft pav (bun) in half and smear with spicy garlic chutney and green chutney.', 'Place the hot fried potato vada inside the pav and serve immediately.'], 'tags': ['street-food', 'burger', 'fried']}, {'name': 'Poha', 'region': 'Maharashtra', 'cuisine': 'Maharashtrian', 'meal_type': 'Breakfast', 'prep_minutes': 5, 'cook_minutes': 15, 'spice_level': 'Medium', 'ingredients': [('Poha', 100), ('Onion', 50), ('Peanuts', 30), ('Potato', 50), ('Oil', 15)], 'instructions': ['Rinse flattened rice (poha) in a colander until soft but not mushy, and drain well.', 'Heat oil, temper mustard seeds, and roast the peanuts.', 'Add chopped onions, diced potatoes, green chilies, and turmeric, cooking until potatoes are soft.', 'Gently fold in the softened poha, cover for 2 minutes, and garnish with fresh coriander and lemon juice.'], 'tags': ['quick', 'light', 'breakfast']}, {'name': 'Dhokla', 'region': 'Gujarat', 'cuisine': 'Gujarati', 'meal_type': 'Snack', 'prep_minutes': 15, 'cook_minutes': 20, 'spice_level': 'Mild', 'ingredients': [('Gram Flour', 150), ('Curd', 50), ('Oil', 10), ('Mixed Vegetables', 10)], 'instructions': ['Mix gram flour (besan), curd, ginger-green chili paste, and water into a smooth batter.', 'Add fruit salt (Eno) just before cooking to make the batter frothy, then pour into a greased pan.', 'Steam for 15-20 minutes until a toothpick comes out clean, then let it cool and cut into squares.', 'Temper mustard seeds, sesame seeds, and green chilies in oil with a little water and sugar, and pour over the dhokla.'], 'tags': ['steamed', 'spongy', 'sweet-salty']}, {'name': 'Thepla', 'region': 'Gujarat', 'cuisine': 'Gujarati', 'meal_type': 'Breakfast', 'prep_minutes': 15, 'cook_minutes': 20, 'spice_level': 'Medium', 'ingredients': [('Wheat Flour', 150), ('Spinach', 50), ('Curd', 30), ('Oil', 15)], 'instructions': ['Finely chop fenugreek leaves (methi) or spinach and mix with whole wheat flour.', 'Add turmeric, chili powder, a little curd, and oil, then knead into a firm dough.', 'Roll out small portions into thin flatbreads.', 'Cook on a hot tawa with oil until brown spots appear on both sides.'], 'tags': ['flatbread', 'travel-friendly', 'healthy']}, {'name': 'Laal Maas', 'region': 'Rajasthan', 'cuisine': 'Rajasthani', 'meal_type': 'Dinner', 'prep_minutes': 20, 'cook_minutes': 60, 'spice_level': 'High', 'ingredients': [('Mutton', 300), ('Onion', 100), ('Curd', 50), ('Ghee', 30)], 'instructions': ['Make a fiery red paste using soaked Mathania red chilies (or Kashmiri chilies) and garlic.', 'Heat ghee in a heavy pot, brown the mutton pieces, and sauté with sliced onions.', 'Add the red chili paste and whisked curd, stirring well to combine.', 'Simmer on low heat for an hour until the mutton is exceptionally tender and engulfed in the spicy red gravy.'], 'tags': ['fiery', 'mutton', 'royal']}, {'name': 'Dal Baati', 'region': 'Rajasthan', 'cuisine': 'Rajasthani', 'meal_type': 'Lunch', 'prep_minutes': 20, 'cook_minutes': 45, 'spice_level': 'Medium', 'ingredients': [('Wheat Flour', 150), ('Toor Dal', 100), ('Ghee', 40), ('Onion', 50)], 'instructions': ['Knead a stiff dough of coarse wheat flour and ghee, form into round balls (baati), and bake or roast until hard and golden.', 'Pressure cook a mix of lentils (Panchmel dal) until soft.', 'Temper the dal with ghee, cumin, garlic, onions, and tomatoes.', 'Crush the hot baked baatis, pour generous amounts of ghee over them, and serve with the spicy mixed dal.'], 'tags': ['heavy', 'baked', 'ghee']}, {'name': 'Bharli Vangi', 'region': 'Maharashtra', 'cuisine': 'Maharashtrian', 'meal_type': 'Dinner', 'prep_minutes': 20, 'cook_minutes': 30, 'spice_level': 'Medium', 'ingredients': [('Eggplant', 250), ('Peanuts', 50), ('Coconut', 30), ('Onion', 50), ('Oil', 20)], 'instructions': ['Slit small, tender eggplants into four sections keeping the stem intact.', 'Roast and grind peanuts, dry coconut, sesame seeds, Goda masala, and jaggery to make a stuffing.', 'Stuff the spice mixture tightly inside the slit eggplants.', 'Heat oil, temper mustard seeds, place the stuffed eggplants in the pan, add a little water, cover, and steam until soft.'], 'tags': ['stuffed', 'peanut-base', 'sweet-spicy']}, {'name': 'Kosha Mangsho', 'region': 'West Bengal', 'cuisine': 'Bengali', 'meal_type': 'Dinner', 'prep_minutes': 30, 'cook_minutes': 90, 'spice_level': 'Medium', 'ingredients': [('Mutton', 300), ('Onion', 150), ('Mustard Oil', 30), ('Curd', 50), ('Potato', 100)], 'instructions': ['Marinate mutton in mustard oil, yogurt, turmeric, and ginger garlic paste.', 'Heat mustard oil in a heavy-bottomed pan (kadai) until it smokes, then fry large chunks of potato and set aside.', 'Sauté finely chopped onions slowly until they caramelize and turn deep brown.', 'Add the marinated mutton and slow-roast (kosha) on low heat for over an hour, adding the potatoes near the end, until the gravy is dark and thick.'], 'tags': ['slow-cooked', 'rich', 'festive']}, {'name': 'Shorshe Ilish', 'region': 'West Bengal', 'cuisine': 'Bengali', 'meal_type': 'Lunch', 'prep_minutes': 10, 'cook_minutes': 15, 'spice_level': 'High', 'ingredients': [('Fish', 250), ('Mustard Oil', 20), ('Onion', 20), ('Mixed Vegetables', 10)], 'instructions': ['Soak yellow and black mustard seeds with green chilies and grind into a smooth, pungent paste.', 'Lightly marinate Hilsa fish pieces with turmeric and salt.', 'Heat mustard oil, add nigella seeds (kalonji) and slit green chilies.', 'Add the mustard paste, a little water, and gently simmer the fish for a few minutes until cooked (do not boil vigorously to avoid bitterness).'], 'tags': ['pungent', 'mustard', 'seafood']}, {'name': 'Aloo Posto', 'region': 'West Bengal', 'cuisine': 'Bengali', 'meal_type': 'Lunch', 'prep_minutes': 15, 'cook_minutes': 20, 'spice_level': 'Mild', 'ingredients': [('Potato', 250), ('Mustard Oil', 20), ('Onion', 50), ('Mixed Vegetables', 20)], 'instructions': ['Soak poppy seeds (posto) in warm water and grind into a smooth paste with green chilies.', 'Cut potatoes into small cubes.', 'Heat mustard oil, temper with nigella seeds, and fry the potato cubes until golden.', 'Stir in the poppy seed paste, add a little water, and cook until the potatoes are tender and coated in the thick white paste.'], 'tags': ['poppy-seeds', 'comfort', 'mild']}, {'name': 'Litti Chokha', 'region': 'Bihar', 'cuisine': 'Bihari', 'meal_type': 'Lunch', 'prep_minutes': 30, 'cook_minutes': 40, 'spice_level': 'Medium', 'ingredients': [('Wheat Flour', 150), ('Gram Flour', 100), ('Eggplant', 100), ('Tomato', 100), ('Ghee', 30)], 'instructions': ['Mix roasted gram flour (sattu) with garlic, ginger, chilies, lemon juice, and pickle spices to make the filling.', 'Stuff the filling into whole wheat dough balls and roast them over an open fire or bake until crisp.', 'For the chokha, fire-roast eggplants and tomatoes, peel them, and mash with raw mustard oil, garlic, and onions.', 'Dip the hot roasted litti in melted ghee and serve with the mashed chokha.'], 'tags': ['roasted', 'rustic', 'sattu']}, {'name': 'Dalma', 'region': 'Odisha', 'cuisine': 'Odia', 'meal_type': 'Lunch', 'prep_minutes': 15, 'cook_minutes': 30, 'spice_level': 'Mild', 'ingredients': [('Toor Dal', 100), ('Mixed Vegetables', 150), ('Coconut', 20), ('Ghee', 15)], 'instructions': ['Boil toor dal with chunks of raw papaya, eggplant, pumpkin, and plantain until soft.', 'Add turmeric, salt, and grated coconut while boiling.', 'Prepare a tempering of ghee, cumin, mustard, and dry red chilies.', 'Pour the tempering over the dal and vegetable mix, and sprinkle roasted cumin-chili powder on top.'], 'tags': ['healthy', 'vegetable-rich', 'no-onion-garlic']}]

new_curated_recipes = [
    {
        "name": "Bagara Baingan", "region": "Telangana", "cuisine": "Hyderabadi", "meal_type": "Dinner",
        "prep_minutes": 15, "cook_minutes": 30, "spice_level": "High",
        "ingredients": [("Eggplant", 200), ("Peanuts", 30), ("Sesame Seeds", 15), ("Tamarind", 10), ("Onion", 50), ("Oil", 20)],
        "instructions": ["Slit baby eggplants and shallow fry until tender.", "Dry roast peanuts, sesame seeds, and desiccated coconut, then grind into a paste.", "Sauté onions and ginger-garlic paste, add the ground peanut-sesame paste and cook until oil separates.", "Add tamarind extract and the fried eggplants, simmering until the gravy is thick."],
        "tags": ["nutty", "tangy", "stuffed"]
    },
    {
        "name": "Mirchi Ka Salan", "region": "Telangana", "cuisine": "Hyderabadi", "meal_type": "Lunch",
        "prep_minutes": 15, "cook_minutes": 25, "spice_level": "High",
        "ingredients": [("Green Chilli", 100), ("Peanuts", 30), ("Sesame Seeds", 20), ("Tamarind", 15), ("Oil", 20)],
        "instructions": ["Slit large green chilies and shallow fry them until blistered.", "Roast peanuts, sesame seeds, and coconut, and blend to a smooth paste.", "Sauté onions, mustard seeds, and curry leaves, then add the ground paste.", "Stir in tamarind paste, add the fried chilies, and simmer until rich and oily."],
        "tags": ["spicy", "accompaniment", "nutty"]
    },
    {
        "name": "Neer Dosa", "region": "Karnataka", "cuisine": "Mangalorean", "meal_type": "Breakfast",
        "prep_minutes": 120, "cook_minutes": 15, "spice_level": "Mild",
        "ingredients": [("Rice", 150), ("Coconut", 30), ("Oil", 10)],
        "instructions": ["Soak rice for a few hours and grind it with fresh grated coconut into a very smooth, watery batter.", "Heat a pan and pour the thin batter, swirling it to form a lace-like crepe.", "Cover and cook on one side only until the edges lift.", "Fold gently and serve hot with chutney or chicken curry."],
        "tags": ["crepe", "soft", "light"]
    },
    {
        "name": "Puttu", "region": "Kerala", "cuisine": "Kerala", "meal_type": "Breakfast",
        "prep_minutes": 10, "cook_minutes": 15, "spice_level": "Mild",
        "ingredients": [("Rice Flour", 150), ("Coconut", 50), ("Water", 100)],
        "instructions": ["Mix roasted rice flour with a little water and salt until it resembles coarse breadcrumbs.", "Layer the damp flour and fresh grated coconut alternately in a cylindrical puttu maker.", "Steam for 5-7 minutes until steam escapes freely from the top.", "Push out the cylindrical rice cake and serve warm with kadala curry or bananas."],
        "tags": ["steamed", "breakfast", "coconut"]
    },
    {
        "name": "Kadala Curry", "region": "Kerala", "cuisine": "Kerala", "meal_type": "Breakfast",
        "prep_minutes": 15, "cook_minutes": 40, "spice_level": "Medium",
        "ingredients": [("Black Chickpeas", 150), ("Coconut", 50), ("Onion", 100), ("Coconut Oil", 20), ("Tomato", 50)],
        "instructions": ["Soak black chickpeas overnight and pressure cook until tender.", "Roast grated coconut with coriander seeds and dry red chilies until dark brown, then grind to a paste.", "Sauté onions, tomatoes, and ginger-garlic paste in coconut oil.", "Add the cooked chickpeas and roasted coconut paste, simmering until the gravy thickens."],
        "tags": ["protein", "roasted-coconut", "staple"]
    },
    {
        "name": "Meen Pollichathu", "region": "Kerala", "cuisine": "Kerala", "meal_type": "Dinner",
        "prep_minutes": 20, "cook_minutes": 25, "spice_level": "High",
        "ingredients": [("Fish", 250), ("Onion", 100), ("Tomato", 50), ("Coconut Oil", 20), ("Banana Leaf", 1)],
        "instructions": ["Marinate a whole fish (like pearl spot) in spices and shallow fry lightly.", "Prepare a thick, spicy masala base by sautéing onions, tomatoes, ginger, garlic, and curry leaves.", "Place the fish on a wilted banana leaf, coat it generously with the masala on both sides.", "Wrap the leaf securely and pan-roast or steam it for a few minutes to let flavors penetrate."],
        "tags": ["seafood", "banana-leaf", "spicy"]
    },
    {
        "name": "Ennai Kathirikai", "region": "Tamil Nadu", "cuisine": "Chettinad", "meal_type": "Lunch",
        "prep_minutes": 15, "cook_minutes": 30, "spice_level": "High",
        "ingredients": [("Eggplant", 200), ("Tamarind", 15), ("Onion", 50), ("Tomato", 50), ("Sesame Oil", 25)],
        "instructions": ["Slit baby eggplants in a cross shape and fry in sesame oil until the skin blisters.", "Roast coriander seeds, chana dal, urad dal, and red chilies, then grind to a powder.", "Sauté chopped onions and tomatoes, add the ground spice powder and tamarind extract.", "Simmer the fried eggplants in the tangy, spicy gravy until the oil floats on top."],
        "tags": ["tangy", "eggplant", "spicy"]
    },
    {
        "name": "Zunka Bhakar", "region": "Maharashtra", "cuisine": "Maharashtrian", "meal_type": "Lunch",
        "prep_minutes": 10, "cook_minutes": 20, "spice_level": "High",
        "ingredients": [("Gram Flour", 100), ("Onion", 100), ("Garlic", 15), ("Oil", 20), ("Sorghum Flour", 150)],
        "instructions": ["For Zunka: Heat oil, temper mustard seeds and lots of chopped garlic and green chilies.", "Add chopped onions and sauté until translucent, then slowly sprinkle gram flour (besan).", "Add a splash of water, mix continuously to avoid lumps, and cook until it forms a dry, crumbly texture.", "Serve hot with thick Sorghum (Jowar) flatbreads (Bhakar) and raw onion."],
        "tags": ["rustic", "village-food", "quick"]
    },
    {
        "name": "Sabudana Khichdi", "region": "Maharashtra", "cuisine": "Maharashtrian", "meal_type": "Breakfast",
        "prep_minutes": 15, "cook_minutes": 15, "spice_level": "Medium",
        "ingredients": [("Tapioca Pearls", 150), ("Peanuts", 50), ("Potato", 100), ("Ghee", 20), ("Green Chilli", 10)],
        "instructions": ["Soak sago (sabudana) overnight until pearls are soft but separate.", "Dry roast peanuts, peel, and crush them coarsely, then mix into the soaked sago.", "Heat ghee, temper cumin seeds and chopped green chilies, and fry diced potatoes until soft.", "Fold in the sago-peanut mixture, season with salt and sugar, and cook until pearls turn translucent."],
        "tags": ["fasting", "chewy", "breakfast"]
    },
    {
        "name": "Pav Bhaji", "region": "Maharashtra", "cuisine": "Maharashtrian", "meal_type": "Snack",
        "prep_minutes": 20, "cook_minutes": 30, "spice_level": "Medium",
        "ingredients": [("Mixed Vegetables", 250), ("Potato", 150), ("Onion", 100), ("Tomato", 150), ("Butter", 50)],
        "instructions": ["Boil potatoes, peas, cauliflower, and carrots until very soft, then mash them completely.", "In a large flat pan, melt butter and sauté finely chopped onions, capsicum, and tomatoes.", "Add a generous amount of Pav Bhaji masala and the mashed vegetables, simmering with water.", "Serve the thick, spicy vegetable mash with butter-toasted soft bread rolls (pav) and lemon."],
        "tags": ["street-food", "buttery", "mash"]
    },
    {
        "name": "Khandvi", "region": "Gujarat", "cuisine": "Gujarati", "meal_type": "Snack",
        "prep_minutes": 10, "cook_minutes": 15, "spice_level": "Mild",
        "ingredients": [("Gram Flour", 100), ("Curd", 100), ("Coconut", 20), ("Oil", 10)],
        "instructions": ["Whisk gram flour, curd, water, ginger paste, turmeric, and salt into a smooth, thin batter.", "Cook the batter on a stovetop, stirring continuously until it thickens and leaves the sides of the pan.", "Quickly spread the hot mixture thinly onto a flat surface or inverted plates.", "Once cooled, cut into strips, roll tightly into cylinders, and garnish with a tempering of mustard seeds and fresh coconut."],
        "tags": ["steamed", "rolls", "snack"]
    },
    {
        "name": "Undhiyu", "region": "Gujarat", "cuisine": "Gujarati", "meal_type": "Lunch",
        "prep_minutes": 40, "cook_minutes": 50, "spice_level": "Medium",
        "ingredients": [("Mixed Vegetables", 300), ("Gram Flour", 50), ("Coconut", 30), ("Peanuts", 30), ("Oil", 30)],
        "instructions": ["Prepare Muthiyas (fried dumplings) using fenugreek leaves, gram flour, and spices.", "Make a green masala paste with fresh coriander, coconut, green chilies, and sesame seeds.", "Stuff small eggplants and potatoes with the green masala.", "Slow cook the stuffed vegetables, purple yam, and surti papdi beans with the remaining masala, adding the fried muthiyas towards the end."],
        "tags": ["winter", "mixed-veg", "elaborate"]
    },
    {
        "name": "Gatte Ki Sabzi", "region": "Rajasthan", "cuisine": "Rajasthani", "meal_type": "Dinner",
        "prep_minutes": 20, "cook_minutes": 30, "spice_level": "Medium",
        "ingredients": [("Gram Flour", 150), ("Curd", 100), ("Oil", 30), ("Onion", 50)],
        "instructions": ["Knead gram flour with yogurt, oil, and spices into a stiff dough and roll into cylindrical logs.", "Boil the logs in water until they float and develop bubbles, then cool and cut into small discs (gatte).", "Prepare a yogurt-based gravy by sautéing onions, ginger-garlic paste, and whisked spiced yogurt.", "Simmer the gatte in the gravy until the oil separates and the dumplings absorb the flavors."],
        "tags": ["gram-flour", "yogurt-gravy", "comfort"]
    },
    {
        "name": "Sarson Ka Saag", "region": "Punjab", "cuisine": "Punjabi", "meal_type": "Lunch",
        "prep_minutes": 20, "cook_minutes": 45, "spice_level": "Medium",
        "ingredients": [("Mustard Leaves", 200), ("Spinach", 100), ("Maize Flour", 20), ("Ghee", 30), ("Onion", 50)],
        "instructions": ["Clean and chop mustard greens, spinach, and bathua, and boil them until soft.", "Coarsely blend or hand-mash the cooked greens, adding a little maize flour to thicken.", "Temper heavily with ghee, chopped garlic, ginger, onions, and green chilies.", "Simmer the mashed greens for a few minutes and serve hot with a dollop of white butter."],
        "tags": ["winter", "leafy", "buttery"]
    },
    {
        "name": "Kadhi Pakora", "region": "Punjab", "cuisine": "Punjabi", "meal_type": "Lunch",
        "prep_minutes": 15, "cook_minutes": 40, "spice_level": "Medium",
        "ingredients": [("Curd", 200), ("Gram Flour", 100), ("Onion", 50), ("Oil", 30), ("Mustard Seeds", 5)],
        "instructions": ["Make a thin, lump-free batter of sour yogurt, gram flour, turmeric, and water.", "Simmer the yogurt batter on low heat, stirring continuously, until it thickens and loses its raw smell.", "Prepare soft onion fritters (pakoras) using a thick gram flour batter and deep fry them.", "Submerge the fried pakoras in the hot kadhi, and finish with a tempering of dry red chilies and cumin."],
        "tags": ["yogurt", "tangy", "dumplings"]
    },
    {
        "name": "Awadhi Biryani", "region": "Uttar Pradesh", "cuisine": "Awadhi", "meal_type": "Dinner",
        "prep_minutes": 30, "cook_minutes": 60, "spice_level": "Medium",
        "ingredients": [("Mutton", 300), ("Basmati Rice", 200), ("Onion", 100), ("Ghee", 40), ("Milk", 30)],
        "instructions": ["Marinate mutton in yogurt, raw papaya paste, and fragrant spices, then partially cook it (yakhni).", "Boil basmati rice with whole spices until 70% cooked and drain.", "Layer the partially cooked meat and rice in a heavy-bottomed pot (handi).", "Sprinkle saffron milk, fried onions, and kewra water, seal the pot with dough, and cook on dum (slow steam) for 30 minutes."],
        "tags": ["aromatic", "royal", "dum-cooked"]
    },
    {
        "name": "Chingri Malai Curry", "region": "West Bengal", "cuisine": "Bengali", "meal_type": "Dinner",
        "prep_minutes": 15, "cook_minutes": 25, "spice_level": "Mild",
        "ingredients": [("Prawns", 250), ("Coconut Milk", 150), ("Onion", 50), ("Mustard Oil", 20)],
        "instructions": ["Marinate large prawns with turmeric and salt, and lightly fry in mustard oil.", "Sauté onion paste, ginger-garlic paste, and green chilies until the raw smell goes away.", "Pour in thick coconut milk, season with sugar and salt, and bring to a gentle simmer.", "Add the fried prawns and cook for a few minutes until the sauce is creamy and coats the prawns."],
        "tags": ["creamy", "seafood", "mild"]
    },
    {
        "name": "Macher Jhol", "region": "West Bengal", "cuisine": "Bengali", "meal_type": "Lunch",
        "prep_minutes": 15, "cook_minutes": 25, "spice_level": "Medium",
        "ingredients": [("Fish", 250), ("Potato", 100), ("Tomato", 50), ("Mustard Oil", 20)],
        "instructions": ["Marinate fish pieces (like Rohu or Katla) with salt and turmeric, then fry until golden.", "In the same mustard oil, temper nigella seeds (kalonji) and fry long potato wedges.", "Add chopped tomatoes, ginger paste, cumin powder, and water to form a thin, soupy broth.", "Add the fried fish and simmer until the potatoes are cooked and the broth absorbs the fish flavor."],
        "tags": ["light-broth", "everyday", "fish"]
    },
    {
        "name": "Goan Fish Curry", "region": "Goa", "cuisine": "Goan", "meal_type": "Dinner",
        "prep_minutes": 15, "cook_minutes": 20, "spice_level": "High",
        "ingredients": [("Fish", 250), ("Coconut", 50), ("Tamarind", 15), ("Onion", 50), ("Coconut Oil", 20)],
        "instructions": ["Grind grated coconut, dried red Kashmiri chilies, coriander seeds, and turmeric to a very fine paste.", "Heat oil, sauté finely chopped onions and green chilies until translucent.", "Add the ground coconut spice paste and tamarind extract, bringing the curry to a boil.", "Gently slide in the fish pieces and simmer until cooked through. Serve with steamed rice."],
        "tags": ["coconut", "tangy", "coastal"]
    },
    {
        "name": "Pork Vindaloo", "region": "Goa", "cuisine": "Goan", "meal_type": "Dinner",
        "prep_minutes": 30, "cook_minutes": 60, "spice_level": "High",
        "ingredients": [("Pork", 300), ("Onion", 100), ("Garlic", 20), ("Vinegar", 30), ("Oil", 20)],
        "instructions": ["Grind dry red chilies, garlic, ginger, cloves, cinnamon, and cumin with Goan palm vinegar into a smooth paste.", "Marinate the pork pieces in the vindaloo paste for at least a few hours, ideally overnight.", "Fry sliced onions until caramelized, then add the marinated pork and sauté.", "Add a little water and slow cook until the pork is extremely tender and the gravy is intensely flavorful and tangy."],
        "tags": ["tangy", "spicy", "vinegar"]
    },
    {
        "name": "Eromba", "region": "Manipur", "cuisine": "Manipuri", "meal_type": "Lunch",
        "prep_minutes": 15, "cook_minutes": 25, "spice_level": "High",
        "ingredients": [("Potato", 150), ("Bamboo Shoot", 50), ("Fish", 30), ("King Chilli", 5)],
        "instructions": ["Boil potatoes, seasonal vegetables (like bamboo shoots or beans), and fiery king chilies until completely soft.", "Roast or fry fermented fish (Ngari) until aromatic.", "Mash the roasted fermented fish into a paste.", "Combine and thoroughly mash the boiled vegetables and chilies with the fermented fish paste, garnish with fresh coriander and serve at room temperature."],
        "tags": ["pungent", "mashed", "fermented"]
    },
    {
        "name": "Thukpa", "region": "Sikkim", "cuisine": "Northeast", "meal_type": "Dinner",
        "prep_minutes": 15, "cook_minutes": 30, "spice_level": "Medium",
        "ingredients": [("Noodles", 150), ("Chicken", 100), ("Mixed Vegetables", 100), ("Onion", 30), ("Oil", 15)],
        "instructions": ["Boil noodles until al dente and set aside.", "Sauté ginger, garlic, onions, and shredded chicken or vegetables in a large pot.", "Pour in chicken or vegetable stock and season with soy sauce and black pepper, simmering until cooked.", "Place noodles in a bowl, pour the hot, flavorful soup over them, and garnish with spring onions."],
        "tags": ["noodle-soup", "comfort", "winter"]
    },
    {
        "name": "Smoked Pork with Bamboo Shoot", "region": "Nagaland", "cuisine": "Naga", "meal_type": "Dinner",
        "prep_minutes": 10, "cook_minutes": 45, "spice_level": "High",
        "ingredients": [("Pork", 300), ("Bamboo Shoot", 100), ("King Chilli", 10), ("Garlic", 15)],
        "instructions": ["Cut smoked pork into bite-sized pieces and boil in water for 15 minutes.", "Add fermented bamboo shoots, crushed garlic, and fiery Naga king chilies (Bhut Jolokia) to the pot.", "Do not use oil; allow the pork fat to render and flavor the broth.", "Simmer until the pork is tender and the liquid is reduced to a thick, intensely flavorful glaze."],
        "tags": ["smoked", "fiery", "fermented"]
    },
    {
        "name": "Bhutte Ka Kees", "region": "Madhya Pradesh", "cuisine": "Indori", "meal_type": "Snack",
        "prep_minutes": 15, "cook_minutes": 20, "spice_level": "Medium",
        "ingredients": [("Corn", 200), ("Milk", 50), ("Ghee", 20), ("Coconut", 20)],
        "instructions": ["Grate fresh sweet corn cobs to get a coarse paste.", "Heat ghee, temper with mustard seeds, green chilies, and asafoetida (hing).", "Add the grated corn and roast well until it loses its raw smell and turns slightly dry.", "Add milk, simmer until absorbed, and garnish generously with grated coconut and coriander."],
        "tags": ["sweet-spicy", "corn", "street-food"]
    },
    {
        "name": "Chicken Xacuti", "region": "Goa", "cuisine": "Goan", "meal_type": "Dinner",
        "prep_minutes": 20, "cook_minutes": 45, "spice_level": "High",
        "ingredients": [("Chicken", 300), ("Coconut", 50), ("Onion", 100), ("Oil", 20), ("Poppy Seeds", 10)],
        "instructions": ["Dry roast poppy seeds, dry red chilies, nutmeg, star anise, and grated coconut until deeply browned.", "Grind the roasted spices and coconut into a thick, smooth paste.", "Sauté onions in oil until translucent, then add chicken pieces and fry until sealed.", "Add the ground Xacuti masala, simmer with water until the chicken is tender and the gravy is thick and complex."],
        "tags": ["complex-spices", "roasted-coconut", "coastal"]
    },
    {
        "name": "Kori Rotti", "region": "Karnataka", "cuisine": "Mangalorean", "meal_type": "Dinner",
        "prep_minutes": 20, "cook_minutes": 40, "spice_level": "High",
        "ingredients": [("Chicken", 250), ("Coconut Milk", 100), ("Onion", 50), ("Rice Flour", 100)],
        "instructions": ["Make a fiery red curry base using Byadagi chilies, coriander seeds, and coconut.", "Cook chicken in the red spice paste until tender.", "Pour in thick coconut milk to finish the rich curry (Kori).", "Serve by crushing crisp, dry rice wafers (Rotti) onto a plate and pouring the hot chicken curry generously over them until they soften."],
        "tags": ["crispy-soft", "coconut-milk", "fiery"]
    },
    {
        "name": "Amritsari Kulcha", "region": "Punjab", "cuisine": "Punjabi", "meal_type": "Breakfast",
        "prep_minutes": 30, "cook_minutes": 20, "spice_level": "Medium",
        "ingredients": [("Wheat Flour", 150), ("Potato", 150), ("Onion", 30), ("Butter", 30)],
        "instructions": ["Knead a soft dough using refined flour, curd, and a pinch of baking soda.", "Mash boiled potatoes with chopped onions, green chilies, anardana (pomegranate seeds), and coriander.", "Stuff the dough balls with the potato filling and roll out into flatbreads.", "Bake in a tandoor or on a hot tawa until crisp, crush lightly with hands, and slather with butter. Serve with chole."],
        "tags": ["stuffed-bread", "crispy", "buttery"]
    },
    {
        "name": "Mutton Dakbungalow", "region": "West Bengal", "cuisine": "Bengali", "meal_type": "Dinner",
        "prep_minutes": 20, "cook_minutes": 60, "spice_level": "High",
        "ingredients": [("Mutton", 300), ("Egg", 100), ("Potato", 100), ("Mustard Oil", 30), ("Onion", 100)],
        "instructions": ["Boil eggs and potatoes, fry them lightly in mustard oil, and set aside.", "Sauté sliced onions, ginger, and garlic in mustard oil until brown.", "Add mutton pieces along with a special roasted spice blend and cook until browned.", "Simmer with water until mutton is tender, adding the fried potatoes and eggs in the last 15 minutes to absorb the rich gravy."],
        "tags": ["colonial-era", "egg-and-meat", "rich"]
    },
    {
        "name": "Champaran Mutton", "region": "Bihar", "cuisine": "Bihari", "meal_type": "Dinner",
        "prep_minutes": 20, "cook_minutes": 90, "spice_level": "High",
        "ingredients": [("Mutton", 300), ("Onion", 200), ("Mustard Oil", 50), ("Garlic", 30)],
        "instructions": ["Marinate mutton with roughly chopped onions, whole garlic bulbs, raw mustard oil, and whole spices.", "Place the marinated meat inside an earthen pot (handi).", "Seal the pot with dough to trap the steam (dum).", "Cook slowly over charcoal or low heat without stirring for over an hour, occasionally shaking the pot, until the meat is meltingly tender."],
        "tags": ["earthen-pot", "slow-cooked", "mustard-oil"]
    },
    {
        "name": "Puran Poli", "region": "Maharashtra", "cuisine": "Maharashtrian", "meal_type": "Snack",
        "prep_minutes": 30, "cook_minutes": 30, "spice_level": "Mild",
        "ingredients": [("Wheat Flour", 150), ("Bengal Gram", 100), ("Jaggery", 100), ("Ghee", 30)],
        "instructions": ["Boil chana dal (Bengal gram) until soft, drain water, and mash it.", "Cook the mashed dal with jaggery, cardamom, and nutmeg until it forms a dry, sweet stuffing (Puran).", "Stuff the sweet filling into a small ball of wheat dough and roll it out carefully.", "Roast the flatbread on a hot tawa, applying generous amounts of ghee until golden spots appear."],
        "tags": ["sweet-flatbread", "festive", "lentil-stuffed"]
    }
]


for n in new_curated_recipes:
    raw_recipes.append(n)


additional_recipes = [
    {
        "name": "Chicken Chettinad",
        "region": "Tamil Nadu",
        "cuisine": "Chettinad",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 40,
        "spice_level": "High",
        "ingredients": [
            [
                "Chicken",
                300
            ],
            [
                "Coconut",
                50
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                50
            ],
            [
                "Sesame Oil",
                20
            ]
        ],
        "instructions": [
            "Dry roast a generous amount of black pepper, fennel, cumin, dry red chilies, and coconut.",
            "Grind the roasted spices into a fine paste with a little water.",
            "Saut\u00e9 chopped onions, tomatoes, and curry leaves in sesame oil until soft.",
            "Add chicken and the ground spice paste, simmer until cooked and the oil floats to the top."
        ],
        "tags": [
            "spicy",
            "peppery",
            "roasted-spices"
        ]
    },
    {
        "name": "Chicken Tikka Masala",
        "region": "Punjab",
        "cuisine": "Punjabi",
        "meal_type": "Dinner",
        "prep_minutes": 30,
        "cook_minutes": 40,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Chicken",
                300
            ],
            [
                "Curd",
                50
            ],
            [
                "Tomato Puree",
                150
            ],
            [
                "Cream",
                30
            ],
            [
                "Butter",
                20
            ]
        ],
        "instructions": [
            "Marinate chicken chunks in yogurt and spices, then grill or roast them until slightly charred.",
            "Prepare a gravy by saut\u00e9ing onions, ginger-garlic paste, and tomato puree until the oil separates.",
            "Add the grilled chicken pieces to the gravy and simmer for a few minutes.",
            "Finish with fresh cream and kasuri methi (dried fenugreek leaves)."
        ],
        "tags": [
            "creamy",
            "popular",
            "grilled"
        ]
    },
    {
        "name": "Paneer Tikka Masala",
        "region": "Punjab",
        "cuisine": "Punjabi",
        "meal_type": "Dinner",
        "prep_minutes": 30,
        "cook_minutes": 30,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Paneer",
                250
            ],
            [
                "Capsicum",
                50
            ],
            [
                "Tomato Puree",
                150
            ],
            [
                "Cream",
                30
            ],
            [
                "Butter",
                20
            ]
        ],
        "instructions": [
            "Marinate paneer cubes and capsicum in spiced yogurt and grill them in an oven or tandoor.",
            "Cook a rich gravy using butter, onions, cashew paste, and tomato puree.",
            "Add the grilled paneer and capsicum to the boiling gravy.",
            "Simmer briefly and garnish with a drizzle of cream and fresh coriander."
        ],
        "tags": [
            "vegetarian",
            "rich",
            "restaurant-style"
        ]
    },
    {
        "name": "Aloo Matar",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Lunch",
        "prep_minutes": 10,
        "cook_minutes": 20,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Potato",
                150
            ],
            [
                "Mixed Vegetables",
                100
            ],
            [
                "Onion",
                50
            ],
            [
                "Tomato",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Heat oil and temper cumin seeds, then saut\u00e9 chopped onions until golden.",
            "Add ginger-garlic paste, chopped tomatoes, and dry spice powders, cooking until mushy.",
            "Add diced potatoes and green peas (matar), mixing well with the masala.",
            "Pour in a little water, cover, and simmer until the potatoes are tender."
        ],
        "tags": [
            "comfort",
            "everyday",
            "homestyle"
        ]
    },
    {
        "name": "Rajma Masala",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Lunch",
        "prep_minutes": 15,
        "cook_minutes": 45,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Kidney Beans",
                150
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                100
            ],
            [
                "Ghee",
                20
            ]
        ],
        "instructions": [
            "Soak rajma (kidney beans) overnight and pressure cook until completely soft.",
            "In a separate pan, prepare a base by frying finely chopped onions, tomatoes, and ginger-garlic paste in ghee.",
            "Mix the cooked beans and their boiling water into the masala.",
            "Simmer on low heat until the gravy thickens and the beans absorb the flavors."
        ],
        "tags": [
            "staple",
            "beans",
            "comfort"
        ]
    },
    {
        "name": "Chana Masala",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Lunch",
        "prep_minutes": 15,
        "cook_minutes": 40,
        "spice_level": "High",
        "ingredients": [
            [
                "Chickpeas",
                150
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                100
            ],
            [
                "Oil",
                20
            ]
        ],
        "instructions": [
            "Soak chickpeas overnight and pressure cook with tea leaves or amla for a dark color.",
            "Saut\u00e9 onions, tomatoes, and ginger-garlic paste with a robust blend of dry spices (chana masala).",
            "Add the cooked chickpeas and simmer until the gravy coats the beans.",
            "Garnish with fresh coriander, slit green chilies, and serve with bhature or rice."
        ],
        "tags": [
            "spicy",
            "popular",
            "protein"
        ]
    },
    {
        "name": "Jeera Rice",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Lunch",
        "prep_minutes": 5,
        "cook_minutes": 15,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Basmati Rice",
                150
            ],
            [
                "Ghee",
                20
            ],
            [
                "Mixed Vegetables",
                0
            ]
        ],
        "instructions": [
            "Wash and soak basmati rice for 20 minutes.",
            "Heat ghee in a pan and temper a generous amount of cumin seeds (jeera) until they crackle.",
            "Add the soaked, drained rice and saut\u00e9 gently for a minute.",
            "Add water and salt, cover, and cook until the rice is fluffy and water is absorbed."
        ],
        "tags": [
            "staple",
            "aromatic",
            "side-dish"
        ]
    },
    {
        "name": "Dal Tadka",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Lunch",
        "prep_minutes": 10,
        "cook_minutes": 25,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Toor Dal",
                100
            ],
            [
                "Onion",
                50
            ],
            [
                "Tomato",
                50
            ],
            [
                "Ghee",
                20
            ],
            [
                "Garlic",
                15
            ]
        ],
        "instructions": [
            "Boil yellow lentils (toor/arhar dal) with turmeric and salt until mushy.",
            "In a small pan, heat ghee and temper cumin seeds, dry red chilies, and lots of chopped garlic.",
            "Add chopped onions and tomatoes to the tempering and saut\u00e9 until soft.",
            "Pour the hot, sizzling tempering (tadka) over the boiled dal right before serving."
        ],
        "tags": [
            "staple",
            "comfort",
            "lentils"
        ]
    },
    {
        "name": "Sambar",
        "region": "South Indian",
        "cuisine": "South Indian",
        "meal_type": "Lunch",
        "prep_minutes": 15,
        "cook_minutes": 30,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Toor Dal",
                100
            ],
            [
                "Mixed Vegetables",
                150
            ],
            [
                "Tamarind",
                15
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Boil toor dal until soft and mash it.",
            "Cook mixed vegetables (drumsticks, carrots, pumpkin) in tamarind water along with freshly ground sambar powder.",
            "Combine the cooked vegetables with the mashed dal and bring to a boil.",
            "Temper with mustard seeds, fenugreek seeds, dry red chilies, and curry leaves in oil."
        ],
        "tags": [
            "tangy",
            "lentils",
            "staple"
        ]
    },
    {
        "name": "Rasam",
        "region": "South Indian",
        "cuisine": "South Indian",
        "meal_type": "Lunch",
        "prep_minutes": 10,
        "cook_minutes": 15,
        "spice_level": "High",
        "ingredients": [
            [
                "Tomato",
                100
            ],
            [
                "Tamarind",
                10
            ],
            [
                "Garlic",
                10
            ],
            [
                "Ghee",
                10
            ]
        ],
        "instructions": [
            "Crush garlic, black pepper, and cumin seeds coarsely.",
            "Boil chopped tomatoes with tamarind extract, turmeric, and the crushed spices in water.",
            "Simmer until the raw smell goes away and the soup is aromatic.",
            "Temper with mustard seeds and curry leaves in a little ghee and pour over the rasam."
        ],
        "tags": [
            "soup",
            "tangy",
            "digestive"
        ]
    },
    {
        "name": "Vegetable Korma",
        "region": "South Indian",
        "cuisine": "South Indian",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 25,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Mixed Vegetables",
                200
            ],
            [
                "Coconut",
                50
            ],
            [
                "Cashews",
                20
            ],
            [
                "Onion",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Boil a mix of chopped vegetables (carrots, beans, potatoes) until just tender.",
            "Grind fresh coconut, cashews, green chilies, and fennel seeds into a smooth paste.",
            "Saut\u00e9 onions and ginger-garlic paste, then add the boiled vegetables.",
            "Stir in the coconut-cashew paste and simmer gently until the gravy is thick and creamy."
        ],
        "tags": [
            "creamy",
            "mild",
            "vegetable-rich"
        ]
    },
    {
        "name": "Chicken Korma",
        "region": "North Indian",
        "cuisine": "Awadhi",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 40,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Chicken",
                300
            ],
            [
                "Curd",
                50
            ],
            [
                "Onion",
                100
            ],
            [
                "Cashews",
                20
            ],
            [
                "Oil",
                30
            ]
        ],
        "instructions": [
            "Deep fry thinly sliced onions until brown and crispy, then crush them to a paste.",
            "Marinate chicken in yogurt and spices.",
            "Cook the chicken with whole spices, adding cashew paste for richness.",
            "Mix in the crushed fried onions and simmer until the chicken is tender and the gravy is fragrant."
        ],
        "tags": [
            "rich",
            "royal",
            "nutty"
        ]
    },
    {
        "name": "Mutton Korma",
        "region": "North Indian",
        "cuisine": "Mughlai",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 60,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Mutton",
                300
            ],
            [
                "Curd",
                50
            ],
            [
                "Onion",
                100
            ],
            [
                "Ghee",
                30
            ],
            [
                "Cashews",
                15
            ]
        ],
        "instructions": [
            "Brown thinly sliced onions in ghee, remove, and crush them into a coarse paste.",
            "In the same ghee, add whole spices and brown the mutton pieces.",
            "Add whisked yogurt and cashew paste, simmering until the meat is halfway cooked.",
            "Stir in the crushed brown onions and a few drops of kewra water, and slow cook until the meat falls off the bone."
        ],
        "tags": [
            "royal",
            "slow-cooked",
            "aromatic"
        ]
    },
    {
        "name": "Upma",
        "region": "South Indian",
        "cuisine": "South Indian",
        "meal_type": "Breakfast",
        "prep_minutes": 10,
        "cook_minutes": 15,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Semolina",
                150
            ],
            [
                "Onion",
                50
            ],
            [
                "Mixed Vegetables",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Dry roast semolina (rava) until lightly golden and set aside.",
            "Heat oil, temper mustard seeds, urad dal, curry leaves, and green chilies.",
            "Saut\u00e9 chopped onions and a few mixed vegetables, then add water and bring to a boil.",
            "Slowly pour the roasted semolina into the boiling water while stirring continuously to prevent lumps, cover and cook for 2 minutes."
        ],
        "tags": [
            "quick",
            "breakfast",
            "savory"
        ]
    },
    {
        "name": "Gobi Manchurian",
        "region": "General Indian",
        "cuisine": "Indo-Chinese",
        "meal_type": "Snack",
        "prep_minutes": 20,
        "cook_minutes": 25,
        "spice_level": "High",
        "ingredients": [
            [
                "Cauliflower",
                200
            ],
            [
                "Wheat Flour",
                30
            ],
            [
                "Onion",
                50
            ],
            [
                "Capsicum",
                50
            ],
            [
                "Oil",
                30
            ]
        ],
        "instructions": [
            "Blanch cauliflower florets, dip them in a spiced flour batter, and deep fry until crispy.",
            "In a wok, heat oil on high and stir-fry finely chopped garlic, ginger, onions, and capsicum.",
            "Add soy sauce, chili sauce, and a splash of vinegar to make a tangy, spicy sauce.",
            "Toss the fried cauliflower in the sauce until evenly coated and garnish with spring onions."
        ],
        "tags": [
            "indo-chinese",
            "crispy",
            "street-food"
        ]
    },
    {
        "name": "Chilli Chicken",
        "region": "General Indian",
        "cuisine": "Indo-Chinese",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 25,
        "spice_level": "High",
        "ingredients": [
            [
                "Chicken",
                250
            ],
            [
                "Onion",
                100
            ],
            [
                "Capsicum",
                100
            ],
            [
                "Oil",
                30
            ],
            [
                "Garlic",
                20
            ]
        ],
        "instructions": [
            "Marinate boneless chicken cubes in soy sauce, egg, and flour, then deep fry until golden.",
            "Saut\u00e9 loads of minced garlic, green chilies, large onion, and capsicum chunks in a wok.",
            "Add a mixture of soy sauce, chili sauce, and a little cornstarch slurry.",
            "Toss the fried chicken in the thick, glossy sauce and serve hot."
        ],
        "tags": [
            "indo-chinese",
            "spicy",
            "popular"
        ]
    },
    {
        "name": "Egg Curry",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Dinner",
        "prep_minutes": 10,
        "cook_minutes": 25,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Egg",
                150
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Hard boil eggs, peel them, make small slits, and shallow fry them until the outer skin is slightly blistered and golden.",
            "In the same oil, saut\u00e9 finely chopped onions until brown, then add ginger-garlic paste.",
            "Add tomato puree and spice powders, cooking until the masala releases oil.",
            "Add a little water to form a gravy, drop in the fried eggs, and simmer for 5 minutes."
        ],
        "tags": [
            "protein",
            "everyday",
            "homestyle"
        ]
    },
    {
        "name": "Egg Bhurji",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Breakfast",
        "prep_minutes": 5,
        "cook_minutes": 10,
        "spice_level": "High",
        "ingredients": [
            [
                "Egg",
                150
            ],
            [
                "Onion",
                50
            ],
            [
                "Tomato",
                50
            ],
            [
                "Oil",
                10
            ],
            [
                "Green Chilli",
                5
            ]
        ],
        "instructions": [
            "Heat oil and saut\u00e9 finely chopped onions and green chilies until translucent.",
            "Add chopped tomatoes and a pinch of turmeric, cooking until soft.",
            "Crack eggs directly into the pan, season with salt and pepper, and scramble vigorously.",
            "Cook until the eggs are completely set and dry, and garnish with fresh coriander."
        ],
        "tags": [
            "quick",
            "scrambled",
            "breakfast"
        ]
    },
    {
        "name": "Prawn Masala",
        "region": "South Indian",
        "cuisine": "Kerala",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 20,
        "spice_level": "High",
        "ingredients": [
            [
                "Prawns",
                250
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                50
            ],
            [
                "Coconut Oil",
                20
            ]
        ],
        "instructions": [
            "Marinate cleaned prawns with turmeric, red chili powder, and salt.",
            "Heat coconut oil, temper mustard seeds and curry leaves, and fry chopped onions until golden.",
            "Add ginger-garlic paste and tomatoes, cooking until the oil separates.",
            "Toss the prawns into the spicy masala and cook for a few minutes until they curl and turn pink. Do not overcook."
        ],
        "tags": [
            "seafood",
            "spicy",
            "coastal"
        ]
    },
    {
        "name": "Fish Molee",
        "region": "Kerala",
        "cuisine": "Kerala",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Fish",
                250
            ],
            [
                "Coconut Milk",
                150
            ],
            [
                "Onion",
                50
            ],
            [
                "Coconut Oil",
                20
            ]
        ],
        "instructions": [
            "Marinate firm white fish slices with turmeric, salt, and pepper, and shallow fry them lightly.",
            "Saut\u00e9 sliced onions, ginger, garlic, green chilies, and curry leaves in coconut oil.",
            "Pour in thin coconut milk and gently slide the fried fish in to simmer.",
            "Finish by pouring thick coconut milk on top and turning off the heat immediately to prevent curdling."
        ],
        "tags": [
            "mild",
            "creamy",
            "seafood"
        ]
    },
    {
        "name": "Aloo Gobi",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Lunch",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Potato",
                150
            ],
            [
                "Cauliflower",
                150
            ],
            [
                "Onion",
                50
            ],
            [
                "Oil",
                20
            ]
        ],
        "instructions": [
            "Cut potatoes into wedges and cauliflower into florets, and optionally par-boil or shallow fry them.",
            "Heat oil, temper cumin seeds, and saut\u00e9 chopped onions, ginger, and garlic.",
            "Add turmeric and coriander powder, then toss in the potatoes and cauliflower.",
            "Cover and cook on low heat until tender, allowing the vegetables to roast slightly at the bottom of the pan."
        ],
        "tags": [
            "dry-curry",
            "homestyle",
            "everyday"
        ]
    },
    {
        "name": "Baingan Bharta",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Dinner",
        "prep_minutes": 10,
        "cook_minutes": 30,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Eggplant",
                250
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                100
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Roast a large eggplant directly over an open flame until the skin is charred and the inside is completely soft.",
            "Peel the charred skin off and mash the smoky eggplant flesh.",
            "Saut\u00e9 chopped onions, garlic, and tomatoes with dry spices until the oil separates.",
            "Stir the mashed eggplant into the masala and cook for a few minutes to combine flavors."
        ],
        "tags": [
            "smoky",
            "roasted",
            "mashed"
        ]
    },
    {
        "name": "Palak Paneer",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 20,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Spinach",
                200
            ],
            [
                "Paneer",
                150
            ],
            [
                "Onion",
                50
            ],
            [
                "Tomato",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Blanch spinach leaves in boiling water, shock in cold water, and blend into a smooth puree.",
            "Saut\u00e9 finely chopped onions and tomatoes with cumin, garlic, and green chilies.",
            "Stir the bright green spinach puree into the masala and simmer gently for a few minutes.",
            "Fold in cubes of paneer and finish with a splash of fresh cream or butter."
        ],
        "tags": [
            "healthy",
            "leafy",
            "iron-rich"
        ]
    },
    {
        "name": "Aloo Paratha",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Breakfast",
        "prep_minutes": 20,
        "cook_minutes": 20,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Wheat Flour",
                150
            ],
            [
                "Potato",
                200
            ],
            [
                "Ghee",
                20
            ],
            [
                "Onion",
                30
            ]
        ],
        "instructions": [
            "Boil and mash potatoes, mixing them with chopped onions, green chilies, coriander, and spices.",
            "Knead whole wheat flour into a soft, pliable dough and let it rest.",
            "Roll a small dough circle, place a generous scoop of the potato filling in the center, seal, and carefully roll it out flat.",
            "Cook the stuffed paratha on a hot tawa, smearing ghee on both sides until crispy and golden brown."
        ],
        "tags": [
            "stuffed-bread",
            "comfort",
            "filling"
        ]
    },
    {
        "name": "Chole Bhature",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Lunch",
        "prep_minutes": 30,
        "cook_minutes": 40,
        "spice_level": "High",
        "ingredients": [
            [
                "Chickpeas",
                150
            ],
            [
                "Wheat Flour",
                150
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato Puree",
                50
            ],
            [
                "Oil",
                30
            ]
        ],
        "instructions": [
            "Soak chickpeas overnight and pressure cook with a tea bag and whole spices until tender.",
            "Saut\u00e9 chopped onions, ginger garlic paste, and tomato puree, then add chole masala and the boiled chickpeas.",
            "Knead a soft dough from refined flour (maida) and yogurt, and let it rest to ferment slightly.",
            "Roll out dough disks and deep fry them in hot oil until they puff up completely (bhature), serving hot with the spicy chickpeas."
        ],
        "tags": [
            "heavy",
            "festive",
            "popular"
        ]
    },
    {
        "name": "Soya Chunks Curry",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 20,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Soya Chunks",
                100
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                100
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Boil soya chunks in salted water, squeeze out all the water thoroughly, and lightly fry them.",
            "Saut\u00e9 finely chopped onions and tomatoes with ginger, garlic, and everyday spices to make a masala base.",
            "Add the fried soya chunks to the masala and stir well to coat.",
            "Add water to make a gravy and simmer until the soya chunks absorb the flavors and become juicy."
        ],
        "tags": [
            "protein-rich",
            "vegan-meat",
            "homestyle"
        ]
    },
    {
        "name": "Keema Matar",
        "region": "North Indian",
        "cuisine": "Mughlai",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 40,
        "spice_level": "High",
        "ingredients": [
            [
                "Mutton",
                250
            ],
            [
                "Mixed Vegetables",
                50
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                50
            ],
            [
                "Oil",
                20
            ]
        ],
        "instructions": [
            "Heat oil and temper whole spices, then fry finely chopped onions until brown.",
            "Add minced mutton (keema) and roast it continuously on high heat until it changes color.",
            "Stir in ginger-garlic paste, tomato puree, and dry spices, cooking until the oil separates.",
            "Add green peas (matar) and a little water, covering the pan to simmer until the mince and peas are tender."
        ],
        "tags": [
            "minced-meat",
            "spicy",
            "rich"
        ]
    },
    {
        "name": "Poriyal",
        "region": "Tamil Nadu",
        "cuisine": "South Indian",
        "meal_type": "Lunch",
        "prep_minutes": 10,
        "cook_minutes": 15,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Mixed Vegetables",
                200
            ],
            [
                "Coconut",
                30
            ],
            [
                "Oil",
                10
            ]
        ],
        "instructions": [
            "Finely chop vegetables like beans, carrots, or cabbage.",
            "Heat a little oil, temper mustard seeds, urad dal, dried red chilies, and curry leaves.",
            "Add the chopped vegetables and stir-fry, sprinkling a little water to steam them until cooked but crunchy.",
            "Turn off the heat and mix in a generous amount of freshly grated coconut."
        ],
        "tags": [
            "dry-veg",
            "healthy",
            "side-dish"
        ]
    },
    {
        "name": "Kootu",
        "region": "Tamil Nadu",
        "cuisine": "South Indian",
        "meal_type": "Lunch",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Mixed Vegetables",
                150
            ],
            [
                "Toor Dal",
                50
            ],
            [
                "Coconut",
                30
            ],
            [
                "Oil",
                10
            ]
        ],
        "instructions": [
            "Boil lentils (moong or toor dal) along with chopped vegetables like ash gourd or snake gourd.",
            "Grind coconut, cumin seeds, and green chilies to a fine paste.",
            "Mix the coconut paste into the boiled vegetable and lentil mixture, simmering for a few minutes.",
            "Finish with a tempering of mustard seeds, urad dal, and curry leaves in coconut oil."
        ],
        "tags": [
            "stew",
            "mild",
            "comfort"
        ]
    },
    {
        "name": "Fish Fry",
        "region": "South Indian",
        "cuisine": "Coastal",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 15,
        "spice_level": "High",
        "ingredients": [
            [
                "Fish",
                250
            ],
            [
                "Oil",
                20
            ],
            [
                "Garlic",
                10
            ]
        ],
        "instructions": [
            "Make a thick paste of turmeric, red chili powder, pepper, crushed garlic, and a little lemon juice.",
            "Rub the paste generously all over the fish slices or whole small fish.",
            "Let it marinate for 15-30 minutes to absorb the flavors.",
            "Shallow fry in hot oil until the outside is crispy and the inside is cooked and flaky."
        ],
        "tags": [
            "crispy",
            "spicy",
            "seafood"
        ]
    }
]

for n in additional_recipes:
    raw_recipes.append(n)



final_additional_recipes = [
    {
        "name": "Natu Kodi Pulusu",
        "region": "Andhra Pradesh",
        "cuisine": "Andhra",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 60,
        "spice_level": "High",
        "ingredients": [
            [
                "Chicken",
                300
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                50
            ],
            [
                "Poppy Seeds",
                10
            ],
            [
                "Coconut",
                20
            ],
            [
                "Oil",
                25
            ]
        ],
        "instructions": [
            "Dry roast poppy seeds, coriander seeds, and dry coconut, then grind into a fine paste.",
            "In a large pot, heat oil and saut\u00e9 chopped onions, green chilies, and ginger-garlic paste until brown.",
            "Add the country chicken (natu kodi) and fry until it changes color.",
            "Stir in the ground paste, spicy red chili powder, and water, simmering for an hour until the meat is extremely tender."
        ],
        "tags": [
            "fiery",
            "country-chicken",
            "slow-cooked"
        ]
    },
    {
        "name": "Gongura Mamsam",
        "region": "Andhra Pradesh",
        "cuisine": "Andhra",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 50,
        "spice_level": "High",
        "ingredients": [
            [
                "Mutton",
                300
            ],
            [
                "Spinach",
                100
            ],
            [
                "Onion",
                100
            ],
            [
                "Green Chilli",
                15
            ],
            [
                "Oil",
                25
            ]
        ],
        "instructions": [
            "Wash and pluck fresh Gongura (sorrel) leaves and saut\u00e9 them lightly until they wilt and turn mushy.",
            "In a pressure cooker, saut\u00e9 onions and whole spices, then add mutton and fry until sealed.",
            "Cook the mutton with water and spices until it is mostly tender.",
            "Add the cooked, tangy sorrel leaves to the mutton and simmer together so the meat absorbs the tartness."
        ],
        "tags": [
            "tangy",
            "spicy",
            "sorrel-leaves"
        ]
    },
    {
        "name": "Pesarattu",
        "region": "Andhra Pradesh",
        "cuisine": "Andhra",
        "meal_type": "Breakfast",
        "prep_minutes": 180,
        "cook_minutes": 10,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Lentils",
                150
            ],
            [
                "Rice",
                20
            ],
            [
                "Green Chilli",
                10
            ],
            [
                "Ginger Garlic Paste",
                10
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Soak whole green gram (moong dal) and a handful of rice overnight.",
            "Grind the soaked dal and rice with ginger, green chilies, and salt into a smooth, thick batter.",
            "Pour a ladle of batter onto a hot tawa and spread it into a thin circle.",
            "Drizzle oil, sprinkle finely chopped onions, and cook until crisp. Fold and serve hot with ginger chutney."
        ],
        "tags": [
            "crepe",
            "protein-rich",
            "green-gram"
        ]
    },
    {
        "name": "Appam",
        "region": "Kerala",
        "cuisine": "Kerala",
        "meal_type": "Breakfast",
        "prep_minutes": 180,
        "cook_minutes": 15,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Rice",
                150
            ],
            [
                "Coconut",
                50
            ],
            [
                "Coconut Milk",
                50
            ]
        ],
        "instructions": [
            "Soak raw rice overnight, then grind it with grated coconut and cooked rice into a smooth batter.",
            "Add a little yeast or fermented coconut water (toddy) and let the batter ferment until frothy and doubled.",
            "Pour a ladle of batter into a curved pan (appachatti) and swirl to coat the sides thinly.",
            "Cover and cook on low heat until the center is soft and fluffy, and the laced edges are crisp."
        ],
        "tags": [
            "fermented",
            "bowl-shaped",
            "crepe"
        ]
    },
    {
        "name": "Avial",
        "region": "Kerala",
        "cuisine": "Kerala",
        "meal_type": "Lunch",
        "prep_minutes": 20,
        "cook_minutes": 20,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Mixed Vegetables",
                300
            ],
            [
                "Coconut",
                50
            ],
            [
                "Curd",
                50
            ],
            [
                "Coconut Oil",
                15
            ]
        ],
        "instructions": [
            "Cut vegetables (ash gourd, yam, drumstick, carrots, beans, raw banana) into long batons and boil them with turmeric.",
            "Grind grated coconut, cumin seeds, and green chilies into a coarse paste.",
            "Stir the coconut paste into the boiled vegetables and simmer briefly.",
            "Turn off the heat, mix in sour yogurt, and finish with a generous drizzle of raw coconut oil and curry leaves."
        ],
        "tags": [
            "mixed-veg",
            "coconut-curd",
            "mild"
        ]
    },
    {
        "name": "Bisi Bele Bath",
        "region": "Karnataka",
        "cuisine": "Kannadiga",
        "meal_type": "Lunch",
        "prep_minutes": 20,
        "cook_minutes": 40,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Rice",
                100
            ],
            [
                "Toor Dal",
                100
            ],
            [
                "Mixed Vegetables",
                150
            ],
            [
                "Tamarind",
                15
            ],
            [
                "Ghee",
                30
            ]
        ],
        "instructions": [
            "Pressure cook rice, toor dal, and mixed vegetables (carrots, beans, peas, potatoes) together until mushy.",
            "Dry roast coriander seeds, chana dal, urad dal, dried red chilies, cinnamon, and cloves, then grind into Bisi Bele Bath powder.",
            "Mix tamarind extract and the ground spice powder into the cooked rice-dal-veg mixture.",
            "Simmer until the flavors meld, and finish with a rich tempering of cashews and curry leaves in ghee."
        ],
        "tags": [
            "one-pot",
            "spicy",
            "lentil-rice"
        ]
    },
    {
        "name": "Thalipeeth",
        "region": "Maharashtra",
        "cuisine": "Maharashtrian",
        "meal_type": "Breakfast",
        "prep_minutes": 15,
        "cook_minutes": 20,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Wheat Flour",
                50
            ],
            [
                "Gram Flour",
                50
            ],
            [
                "Sorghum Flour",
                50
            ],
            [
                "Onion",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Mix roasted multi-grain flours (bhajani) with chopped onions, coriander, green chilies, and turmeric.",
            "Knead into a soft dough using water and a little oil.",
            "Wet your hands and pat a small portion of the dough directly onto a damp cloth to form a flatbread.",
            "Carefully transfer to a hot tawa, make small holes in the center, drizzle oil, and cook until crisp on both sides."
        ],
        "tags": [
            "multi-grain",
            "flatbread",
            "healthy"
        ]
    },
    {
        "name": "Handvo",
        "region": "Gujarat",
        "cuisine": "Gujarati",
        "meal_type": "Snack",
        "prep_minutes": 120,
        "cook_minutes": 45,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Rice",
                100
            ],
            [
                "Lentils",
                100
            ],
            [
                "Curd",
                50
            ],
            [
                "Mixed Vegetables",
                100
            ],
            [
                "Oil",
                20
            ]
        ],
        "instructions": [
            "Soak rice and mixed lentils (chana, toor, urad dal) overnight, then grind into a coarse batter and ferment with curd.",
            "Mix grated bottle gourd (lauki), carrots, ginger-green chili paste, turmeric, and salt into the fermented batter.",
            "Heat oil in a heavy pan, temper mustard and sesame seeds, and pour the thick batter over it.",
            "Cover and bake on low heat until the bottom is a deep crusty brown, then flip and cook the other side."
        ],
        "tags": [
            "savory-cake",
            "fermented",
            "baked"
        ]
    },
    {
        "name": "Dum Aloo",
        "region": "Kashmir",
        "cuisine": "Kashmiri",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 40,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Potato",
                250
            ],
            [
                "Curd",
                100
            ],
            [
                "Mustard Oil",
                30
            ],
            [
                "Fennel",
                10
            ]
        ],
        "instructions": [
            "Boil baby potatoes, peel them, prick all over with a fork, and deep fry in mustard oil until golden and crisp.",
            "Whisk yogurt with generous amounts of Kashmiri red chili powder, fennel powder, and dry ginger powder.",
            "Heat a little mustard oil, add whole spices, and pour in the spiced yogurt, stirring constantly until it boils.",
            "Add the fried potatoes, seal the pot, and cook on very low heat (dum) until the potatoes absorb the rich red gravy."
        ],
        "tags": [
            "spicy",
            "yogurt",
            "slow-cooked"
        ]
    },
    {
        "name": "Shukto",
        "region": "West Bengal",
        "cuisine": "Bengali",
        "meal_type": "Lunch",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Mixed Vegetables",
                200
            ],
            [
                "Mustard Oil",
                15
            ],
            [
                "Milk",
                50
            ],
            [
                "Ghee",
                10
            ]
        ],
        "instructions": [
            "Chop mixed vegetables, importantly including bitter gourd (karela), sweet potato, raw banana, and drumsticks.",
            "Fry the bitter gourd and lentil dumplings (bori) lightly in mustard oil.",
            "Saut\u00e9 the rest of the vegetables with a paste of mustard and poppy seeds.",
            "Add water, simmer until tender, pour in a splash of milk to tone down the bitterness, and finish with ghee and roasted radhuni powder."
        ],
        "tags": [
            "bitter-sweet",
            "stew",
            "traditional"
        ]
    },
    {
        "name": "Luchi",
        "region": "West Bengal",
        "cuisine": "Bengali",
        "meal_type": "Breakfast",
        "prep_minutes": 20,
        "cook_minutes": 15,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Wheat Flour",
                150
            ],
            [
                "Oil",
                30
            ],
            [
                "Ghee",
                10
            ]
        ],
        "instructions": [
            "Knead refined flour (maida) with a little ghee and water into a soft, smooth dough.",
            "Divide the dough into small balls and roll them out into thin, perfectly round disks.",
            "Heat oil in a deep kadai and gently slide the rolled dough into the hot oil.",
            "Press lightly so the luchi puffs up into a white, airy balloon, and immediately remove before it browns."
        ],
        "tags": [
            "deep-fried",
            "puffed-bread",
            "soft"
        ]
    },
    {
        "name": "Paneer Bhurji",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Breakfast",
        "prep_minutes": 5,
        "cook_minutes": 15,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Paneer",
                200
            ],
            [
                "Onion",
                50
            ],
            [
                "Tomato",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Crumble fresh paneer into coarse bits.",
            "Heat oil, temper cumin seeds, and saut\u00e9 finely chopped onions and green chilies until pink.",
            "Add chopped tomatoes and dry spices, cooking until mushy and the raw smell disappears.",
            "Add the crumbled paneer, mix gently, and cook for just a couple of minutes to retain moisture. Garnish with coriander."
        ],
        "tags": [
            "scrambled",
            "quick",
            "protein"
        ]
    },
    {
        "name": "Soya Tikka",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Snack",
        "prep_minutes": 20,
        "cook_minutes": 20,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Soya Chunks",
                150
            ],
            [
                "Curd",
                50
            ],
            [
                "Capsicum",
                50
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Boil large soya chunks in salted water, drain, and squeeze out all excess moisture.",
            "Mix thick curd with roasted gram flour, mustard oil, ginger-garlic paste, and tandoori spices to form a marinade.",
            "Coat the boiled soya chunks and diced capsicum in the marinade and let sit for 30 minutes.",
            "Thread onto skewers and roast in an oven, air fryer, or open flame until charred and smoky."
        ],
        "tags": [
            "vegan-meat",
            "grilled",
            "high-protein"
        ]
    },
    {
        "name": "Kuzhi Paniyaram",
        "region": "Tamil Nadu",
        "cuisine": "South Indian",
        "meal_type": "Breakfast",
        "prep_minutes": 10,
        "cook_minutes": 15,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Rice",
                100
            ],
            [
                "Lentils",
                50
            ],
            [
                "Onion",
                30
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Use leftover idli/dosa batter, which is naturally fermented.",
            "Temper mustard seeds, urad dal, chopped onions, green chilies, and curry leaves, and mix into the batter.",
            "Heat a special paniyaram pan (with semi-spherical indentations) and pour a few drops of oil into each hole.",
            "Pour the batter into the holes, cover and cook until the bottom is crisp, then flip using a skewer and cook the other side."
        ],
        "tags": [
            "dumplings",
            "crispy",
            "snack"
        ]
    },
    {
        "name": "Mix Veg Curry",
        "region": "General Indian",
        "cuisine": "General",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Mixed Vegetables",
                250
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                100
            ],
            [
                "Oil",
                20
            ],
            [
                "Garlic",
                15
            ]
        ],
        "instructions": [
            "Chop a variety of vegetables (carrots, beans, peas, cauliflower, potato) into bite-sized pieces.",
            "Saut\u00e9 chopped onions, ginger, and garlic in oil until golden brown.",
            "Add chopped tomatoes, turmeric, coriander powder, and garam masala, cooking until a thick paste forms.",
            "Toss the chopped vegetables into the masala, add a splash of water, cover, and simmer until tender."
        ],
        "tags": [
            "healthy",
            "everyday",
            "adaptable"
        ]
    },
    {
        "name": "Egg Fried Rice",
        "region": "General Indian",
        "cuisine": "Indo-Chinese",
        "meal_type": "Dinner",
        "prep_minutes": 10,
        "cook_minutes": 10,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Basmati Rice",
                150
            ],
            [
                "Egg",
                100
            ],
            [
                "Mixed Vegetables",
                50
            ],
            [
                "Oil",
                20
            ]
        ],
        "instructions": [
            "Cook basmati rice and let it cool completely, or use leftover chilled rice.",
            "Heat oil in a wok on high heat, crack eggs directly in, and scramble them quickly.",
            "Add finely chopped garlic, onions, carrots, and beans, stir-frying rapidly for a minute.",
            "Add the chilled rice, soy sauce, and black pepper, tossing vigorously on high heat until well combined."
        ],
        "tags": [
            "quick",
            "indo-chinese",
            "comfort"
        ]
    },
    {
        "name": "Chicken Biryani",
        "region": "Telangana",
        "cuisine": "Hyderabadi",
        "meal_type": "Dinner",
        "prep_minutes": 45,
        "cook_minutes": 60,
        "spice_level": "High",
        "ingredients": [
            [
                "Chicken",
                300
            ],
            [
                "Basmati Rice",
                200
            ],
            [
                "Onion",
                100
            ],
            [
                "Curd",
                50
            ],
            [
                "Ghee",
                30
            ],
            [
                "Mint Leaves",
                15
            ]
        ],
        "instructions": [
            "Marinate raw chicken with yogurt, ginger-garlic, raw papaya paste, fried onions, and strong spices for several hours.",
            "Boil basmati rice with whole spices until only 50% cooked and drain.",
            "Layer the partially cooked hot rice over the raw marinated chicken in a heavy-bottomed pot.",
            "Pour saffron milk and ghee on top, seal tight with dough, and cook on very low heat (dum) for 45 minutes."
        ],
        "tags": [
            "royal",
            "aromatic",
            "one-pot"
        ]
    },
    {
        "name": "Fish Tikka",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Snack",
        "prep_minutes": 20,
        "cook_minutes": 15,
        "spice_level": "High",
        "ingredients": [
            [
                "Fish",
                250
            ],
            [
                "Curd",
                50
            ],
            [
                "Gram Flour",
                15
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Cut firm white fish fillets into large cubes.",
            "Prepare a thick marinade using hung curd, roasted gram flour, mustard oil, lemon juice, ajwain (carom seeds), and red chili powder.",
            "Coat the fish gently in the marinade and let sit for 30 minutes.",
            "Skewer the fish cubes and grill or pan-fry on high heat until the exterior is charred and the fish is flaky."
        ],
        "tags": [
            "grilled",
            "appetizer",
            "protein"
        ]
    },
    {
        "name": "Mutton Seekh Kebab",
        "region": "Uttar Pradesh",
        "cuisine": "Mughlai",
        "meal_type": "Snack",
        "prep_minutes": 20,
        "cook_minutes": 15,
        "spice_level": "High",
        "ingredients": [
            [
                "Mutton",
                300
            ],
            [
                "Onion",
                50
            ],
            [
                "Garlic",
                15
            ],
            [
                "Oil",
                15
            ]
        ],
        "instructions": [
            "Mix finely minced mutton (keema) with grated and squeezed onions, ginger-garlic paste, green chilies, and roasted spice powders.",
            "Knead the mince mixture vigorously with your hands until it becomes slightly sticky and binds well.",
            "Wet your hands and mold portions of the mince tightly around long metal skewers to form cylindrical kebabs.",
            "Grill over charcoal or in an oven, basting with oil or butter until browned and cooked through."
        ],
        "tags": [
            "grilled",
            "mince",
            "appetizer"
        ]
    },
    {
        "name": "Dal Dhokli",
        "region": "Gujarat",
        "cuisine": "Gujarati",
        "meal_type": "Lunch",
        "prep_minutes": 20,
        "cook_minutes": 30,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Toor Dal",
                100
            ],
            [
                "Wheat Flour",
                100
            ],
            [
                "Peanuts",
                30
            ],
            [
                "Jaggery",
                15
            ],
            [
                "Ghee",
                15
            ]
        ],
        "instructions": [
            "Boil and mash toor dal, then thin it out into a soupy consistency, adding peanuts, jaggery, tamarind, and spices.",
            "Bring the sweet, spicy, and tangy dal to a rolling boil.",
            "Knead wheat flour with spices into a firm dough, roll it thin, and cut into diamond shapes (dhokli).",
            "Drop the raw dough diamonds into the boiling dal one by one, simmering until they are cooked and the dal thickens."
        ],
        "tags": [
            "one-pot",
            "sweet-tangy",
            "comfort"
        ]
    }
]

for n in final_additional_recipes:
    raw_recipes.append(n)



extra_10_recipes = [
    {
        "name": "Bhakri",
        "region": "Maharashtra",
        "cuisine": "Maharashtrian",
        "meal_type": "Lunch",
        "prep_minutes": 10,
        "cook_minutes": 10,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Sorghum Flour",
                150
            ],
            [
                "Water",
                100
            ],
            [
                "Salt",
                5
            ]
        ],
        "instructions": [
            "Knead jowar (sorghum) flour with warm water until soft and pliable.",
            "Dust a board with flour and pat the dough out with your palms into a circle.",
            "Transfer to a hot iron tawa, sprinkle water on the top surface, and let it dry slightly.",
            "Flip and roast on direct flame until it puffs up. Serve hot with zunka or thecha."
        ],
        "tags": [
            "flatbread",
            "gluten-free",
            "rustic"
        ]
    },
    {
        "name": "Zunka",
        "region": "Maharashtra",
        "cuisine": "Maharashtrian",
        "meal_type": "Lunch",
        "prep_minutes": 10,
        "cook_minutes": 15,
        "spice_level": "High",
        "ingredients": [
            [
                "Gram Flour",
                100
            ],
            [
                "Onion",
                100
            ],
            [
                "Garlic",
                15
            ],
            [
                "Oil",
                20
            ]
        ],
        "instructions": [
            "Heat oil, temper mustard seeds, cumin, and lots of chopped garlic and green chilies.",
            "Saut\u00e9 chopped onions until golden brown.",
            "Mix gram flour (besan) with a little water and spices, then pour into the pan.",
            "Stir continuously on low heat until it cooks into a thick, dry, crumbly mixture. Serve with bhakri."
        ],
        "tags": [
            "dry-curry",
            "quick",
            "protein"
        ]
    },
    {
        "name": "Gatte Ki Sabzi",
        "region": "Rajasthan",
        "cuisine": "Rajasthani",
        "meal_type": "Lunch",
        "prep_minutes": 20,
        "cook_minutes": 30,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Gram Flour",
                150
            ],
            [
                "Curd",
                100
            ],
            [
                "Oil",
                20
            ],
            [
                "Ghee",
                15
            ]
        ],
        "instructions": [
            "Knead gram flour (besan) with spices and oil into a dough, roll into logs, and boil in water.",
            "Cut the boiled logs into small disks (gatte) and lightly fry them in ghee.",
            "Prepare a spiced yogurt-based gravy by saut\u00e9ing cumin, asafoetida, and dry spices.",
            "Add the fried gatte to the yogurt gravy and simmer until the gravy thickens and the gatte are soft."
        ],
        "tags": [
            "no-vegetable",
            "yogurt",
            "traditional"
        ]
    },
    {
        "name": "Ker Sangri",
        "region": "Rajasthan",
        "cuisine": "Rajasthani",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "High",
        "ingredients": [
            [
                "Mixed Vegetables",
                150
            ],
            [
                "Oil",
                30
            ],
            [
                "Raisins",
                20
            ],
            [
                "Dry Red Chilli",
                10
            ]
        ],
        "instructions": [
            "Soak dried desert berries (ker) and beans (sangri) overnight, then boil until soft.",
            "Heat mustard oil and temper with cumin, fennel, and dry red chilies.",
            "Add the boiled ker and sangri along with dry mango powder (amchur), raisins, and spices.",
            "Cook until the moisture evaporates, creating a dry, tangy, and spicy side dish with a long shelf life."
        ],
        "tags": [
            "desert",
            "tangy",
            "dry"
        ]
    },
    {
        "name": "Macher Jhol",
        "region": "West Bengal",
        "cuisine": "Bengali",
        "meal_type": "Lunch",
        "prep_minutes": 15,
        "cook_minutes": 30,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Fish",
                250
            ],
            [
                "Potato",
                100
            ],
            [
                "Mustard Oil",
                20
            ],
            [
                "Tomato",
                50
            ],
            [
                "Panch Phoron",
                5
            ]
        ],
        "instructions": [
            "Marinate Rui or Katla fish pieces with turmeric and salt, then lightly fry in mustard oil.",
            "In the same oil, fry potato wedges and set aside.",
            "Temper the oil with cumin or panch phoron, saut\u00e9 ginger paste and tomatoes until soft.",
            "Add water to make a thin broth (jhol), slide in the fish and potatoes, and simmer until tender."
        ],
        "tags": [
            "broth",
            "light",
            "fish"
        ]
    },
    {
        "name": "Chicken Sukka",
        "region": "Karnataka",
        "cuisine": "Mangalorean",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 40,
        "spice_level": "High",
        "ingredients": [
            [
                "Chicken",
                300
            ],
            [
                "Coconut",
                50
            ],
            [
                "Onion",
                100
            ],
            [
                "Byadagi Chilli",
                10
            ],
            [
                "Ghee",
                20
            ]
        ],
        "instructions": [
            "Dry roast Byadagi chilies, coriander seeds, cumin, and fenugreek, then grind into a paste.",
            "Coarsely grind fresh grated coconut with a little garlic and turmeric.",
            "Saut\u00e9 onions in ghee, add chicken, and cook with the roasted spice paste.",
            "Once the chicken is almost done, mix in the coarse coconut mixture and roast until it is completely dry (sukka)."
        ],
        "tags": [
            "dry-roast",
            "coconut",
            "coastal"
        ]
    },
    {
        "name": "Paneer Butter Masala",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Paneer",
                200
            ],
            [
                "Tomato Puree",
                150
            ],
            [
                "Cashews",
                30
            ],
            [
                "Cream",
                30
            ],
            [
                "Butter",
                30
            ]
        ],
        "instructions": [
            "Boil tomatoes, onions, and cashews, then blend them into a smooth, silky puree.",
            "Melt butter in a pan, add ginger-garlic paste, and pour in the puree.",
            "Cook until the sauce thickens, adding a little sugar or honey to balance the tanginess.",
            "Add paneer cubes, crushed kasuri methi, and finish with a swirl of fresh cream."
        ],
        "tags": [
            "creamy",
            "sweet-tangy",
            "popular"
        ]
    },
    {
        "name": "Mushroom Do Pyaza",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Dinner",
        "prep_minutes": 15,
        "cook_minutes": 25,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Mushroom",
                200
            ],
            [
                "Onion",
                150
            ],
            [
                "Tomato",
                50
            ],
            [
                "Oil",
                20
            ]
        ],
        "instructions": [
            "Cut mushrooms and dice half of the onions into large squares, separating the petals.",
            "Finely chop the remaining onions and saut\u00e9 them with tomatoes to make a base gravy.",
            "Lightly fry the large onion squares and mushrooms in a separate pan.",
            "Toss the fried onions and mushrooms into the base gravy, simmering until coated in the thick masala."
        ],
        "tags": [
            "onions",
            "dry-curry",
            "restaurant-style"
        ]
    },
    {
        "name": "Undhiyu",
        "region": "Gujarat",
        "cuisine": "Gujarati",
        "meal_type": "Lunch",
        "prep_minutes": 45,
        "cook_minutes": 45,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Mixed Vegetables",
                300
            ],
            [
                "Gram Flour",
                50
            ],
            [
                "Coconut",
                30
            ],
            [
                "Peanuts",
                30
            ],
            [
                "Oil",
                30
            ]
        ],
        "instructions": [
            "Prepare small fried dumplings (muthiyas) using gram flour, fenugreek leaves, and spices.",
            "Stuff baby eggplants and potatoes with a mixture of grated coconut, peanuts, green garlic, and coriander.",
            "Layer the stuffed vegetables, purple yam, and surti papdi (beans) in a heavy-bottomed pot.",
            "Cook slowly, adding the fried muthiyas near the end, until all vegetables are tender and aromatic."
        ],
        "tags": [
            "winter",
            "mixed-veg",
            "festive"
        ]
    },
    {
        "name": "Khamandu",
        "region": "Gujarat",
        "cuisine": "Gujarati",
        "meal_type": "Snack",
        "prep_minutes": 15,
        "cook_minutes": 10,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Gram Flour",
                150
            ],
            [
                "Oil",
                15
            ],
            [
                "Mustard Seeds",
                5
            ],
            [
                "Coconut",
                10
            ]
        ],
        "instructions": [
            "Crumble freshly made khaman dhokla into a bowl.",
            "Heat oil and temper mustard seeds, green chilies, and curry leaves.",
            "Pour the hot tempering over the crumbled dhokla.",
            "Garnish generously with fresh grated coconut, pomegranate seeds, and coriander. Serve with sev."
        ],
        "tags": [
            "crumbled",
            "sweet-salty",
            "snack"
        ]
    }
]

for n in extra_10_recipes:
    raw_recipes.append(n)



final_3_recipes = [
    {
        "name": "Malai Kofta",
        "region": "North Indian",
        "cuisine": "Mughlai",
        "meal_type": "Dinner",
        "prep_minutes": 25,
        "cook_minutes": 35,
        "spice_level": "Mild",
        "ingredients": [
            [
                "Paneer",
                150
            ],
            [
                "Potato",
                100
            ],
            [
                "Cream",
                50
            ],
            [
                "Cashews",
                30
            ],
            [
                "Tomato Puree",
                100
            ]
        ],
        "instructions": [
            "Mash boiled potatoes and paneer, mix with spices and cornstarch, and form into round balls (koftas).",
            "Deep fry the koftas until golden and set aside.",
            "Saut\u00e9 ginger, garlic, and tomato puree, then blend with soaked cashews for a rich base.",
            "Simmer the creamy tomato-cashew gravy and pour over the fried koftas just before serving."
        ],
        "tags": [
            "rich",
            "dumplings",
            "creamy"
        ]
    },
    {
        "name": "Pav Bhaji",
        "region": "Maharashtra",
        "cuisine": "Maharashtrian",
        "meal_type": "Snack",
        "prep_minutes": 15,
        "cook_minutes": 30,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Mixed Vegetables",
                200
            ],
            [
                "Potato",
                150
            ],
            [
                "Onion",
                100
            ],
            [
                "Tomato",
                100
            ],
            [
                "Butter",
                50
            ]
        ],
        "instructions": [
            "Boil and mash potatoes, cauliflower, peas, and carrots together.",
            "On a large flat tawa, melt a generous amount of butter, saut\u00e9 onions and capsicum, then add chopped tomatoes.",
            "Add the mashed vegetables, a splash of water, and strong pav bhaji masala, mashing everything continuously on the tawa.",
            "Serve the spicy, buttery bhaji with soft pav (bread) toasted in more butter."
        ],
        "tags": [
            "street-food",
            "mashed",
            "buttery"
        ]
    },
    {
        "name": "Sarson Ka Saag",
        "region": "Punjab",
        "cuisine": "Punjabi",
        "meal_type": "Dinner",
        "prep_minutes": 20,
        "cook_minutes": 45,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Spinach",
                250
            ],
            [
                "Wheat Flour",
                30
            ],
            [
                "Ghee",
                30
            ],
            [
                "Garlic",
                20
            ]
        ],
        "instructions": [
            "Boil a mix of mustard leaves (sarson), spinach, and bathua leaves with ginger and garlic.",
            "Blend or mash the boiled greens into a coarse paste, adding a little maize flour (makki atta) to thicken it.",
            "Simmer the greens on low heat for a long time to reduce the bitterness.",
            "Temper heavily with garlic, dry red chilies, and ghee, serving hot with Makki ki Roti."
        ],
        "tags": [
            "winter",
            "leafy",
            "buttery"
        ]
    }
]

for n in final_3_recipes:
    raw_recipes.append(n)



extra_2_recipes = [
    {
        "name": "Aloo Tikki",
        "region": "North Indian",
        "cuisine": "Punjabi",
        "meal_type": "Snack",
        "prep_minutes": 15,
        "cook_minutes": 20,
        "spice_level": "Medium",
        "ingredients": [
            [
                "Potato",
                250
            ],
            [
                "Oil",
                30
            ],
            [
                "Peas",
                50
            ],
            [
                "Green Chilli",
                5
            ]
        ],
        "instructions": [
            "Boil, peel, and mash potatoes thoroughly without leaving lumps.",
            "Mix with boiled peas, chopped green chilies, coriander, and spices.",
            "Form into small, flat patties (tikkis).",
            "Shallow fry on a hot tawa with oil or ghee until golden brown and extremely crisp on both sides."
        ],
        "tags": [
            "crispy",
            "street-food",
            "potato"
        ]
    },
    {
        "name": "Pani Puri",
        "region": "North Indian",
        "cuisine": "North Indian",
        "meal_type": "Snack",
        "prep_minutes": 25,
        "cook_minutes": 0,
        "spice_level": "High",
        "ingredients": [
            [
                "Potato",
                100
            ],
            [
                "Mint Leaves",
                20
            ],
            [
                "Tamarind",
                20
            ],
            [
                "Chickpeas",
                50
            ]
        ],
        "instructions": [
            "Prepare the spicy water (pani) by blending mint, coriander, green chilies, and pani puri masala.",
            "Prepare the sweet water using tamarind extract and jaggery.",
            "Mix boiled, mashed potatoes and black chickpeas with spices for the filling.",
            "Crack a small hole in the center of the hollow, crispy puri, stuff with the filling, dip in both waters, and eat immediately."
        ],
        "tags": [
            "street-food",
            "tangy",
            "crispy"
        ]
    }
]

for n in extra_2_recipes:
    raw_recipes.append(n)


final_recipes = []

for idx, r in enumerate(raw_recipes):
    # Determine diets
    is_vegan = True
    is_veg = True
    for item, qty in r["ingredients"]:
        name = item.lower()
        if name in ["chicken", "mutton", "fish", "beef", "pork", "prawns", "egg"]:
            is_veg = False
            is_vegan = False
        if name in ["paneer", "curd", "cream", "milk", "butter", "ghee", "honey", "buttermilk"]:
            is_vegan = False

    diets = []
    if is_vegan:
        diets.extend(["Vegan", "Vegetarian"])
    elif is_veg:
        diets.append("Vegetarian")
    else:
        # non-veg or eggetarian
        has_meat = any(i[0].lower() in ["chicken", "mutton", "fish", "beef", "pork", "prawns"] for i in r["ingredients"])
        has_egg = any(i[0].lower() == "egg" for i in r["ingredients"])
        if has_meat:
            diets.append("Non-vegetarian")
        elif has_egg:
            diets.append("Eggetarian")

    if not diets:
        diets.append("Non-vegetarian")

    # Format ingredients
    formatted_ing = [{"name": n, "quantity": q, "unit": "g" if n != "Oil" and n != "Mustard Oil" and n != "Sesame Oil" and n != "Coconut Oil" and n != "Milk" and n != "Coconut Milk" and n != "Cream" and n != "Vinegar" else "ml"} for n, q in r["ingredients"]]
    
    # Check if duplicate name
    existing_names = [fr["name"] for fr in final_recipes]
    if r["name"] in existing_names:
        continue # skip exact duplicate names

    # Build standard object
    recipe_obj = {
        "recipe_id": generate_recipe_id(r["name"], r["region"]),
        "name": r["name"],
        "description": f"A delicious {r['name']} from {r['region']}.",
        "region": r["region"],
        "cuisine": r.get("cuisine", "Indian"),
        "meal_type": r["meal_type"],
        "diets": list(set(diets)),
        "prep_minutes": r["prep_minutes"],
        "cook_minutes": r["cook_minutes"],
        "spice_level": r["spice_level"],
        "tags": r["tags"],
        "servings": 2,
        "ingredients": formatted_ing,
        "instructions": r["instructions"],
        "nutrition": calculate_macros(formatted_ing),
        "source_type": "curated"
    }
    final_recipes.append(recipe_obj)

def generate_and_save(output_file="indian_recipes.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, output_file)
    with open(file_path, 'w') as f:
        json.dump(final_recipes, f, indent=4)
    print(f"Generated {len(final_recipes)} highly curated recipes and saved to {file_path}.")

if __name__ == "__main__":
    generate_and_save()
