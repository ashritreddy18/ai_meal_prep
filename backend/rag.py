import json
import os
import chromadb

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CHROMA_PATH = os.path.join(DATA_DIR, "chroma")
RECIPES_PATH = os.path.join(DATA_DIR, "indian_recipes.json")

# Initialize ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)

# We use the default local embedding function which is lightweight and fast
# all-MiniLM-L6-v2 model is downloaded and cached automatically.
collection = client.get_or_create_collection(name="recipes")

def initialize_database():
    """Load recipes from JSON and insert them into ChromaDB if empty."""
    # Since we are updating schema, we will wipe the collection if it doesn't match the new size or just wipe it once.
    # We can rely on collection count. We have 159 recipes now. 
    # Let's just always delete and recreate for this stage to ensure clean state.
    try:
        client.delete_collection("recipes")
    except:
        pass
        
    global collection
    collection = client.get_or_create_collection(name="recipes")

    if not os.path.exists(RECIPES_PATH):
        print(f"Warning: Recipe data file not found at {RECIPES_PATH}")
        return

    with open(RECIPES_PATH, "r") as f:
        recipes = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for i, recipe in enumerate(recipes):
        # Create a rich document string for embedding
        doc_text = f"{recipe['name']}. {recipe['description']} Region: {recipe.get('region', '')}. Cuisine: {recipe.get('cuisine', '')}. Meal Type: {recipe.get('meal_type', '')}. Diets: {', '.join(recipe.get('diets', []))}. Tags: {', '.join(recipe.get('tags', []))}"
        documents.append(doc_text)
        
        # Store structured data in metadata for filtering
        meta = {
            "recipe_id": recipe.get("recipe_id", str(i)),
            "name": recipe["name"],
            "prep_minutes": recipe["prep_minutes"],
            "cook_minutes": recipe.get("cook_minutes", 0),
            "calories": recipe["nutrition"]["calories"],
            "protein_g": recipe["nutrition"]["protein_g"],
            "diets": ",".join(recipe["diets"]),
            "meal_type": recipe["meal_type"],
            # Storing complex objects as JSON strings in metadata
            "full_json": json.dumps(recipe)
        }
        metadatas.append(meta)
        ids.append(f"recipe_{i}")

    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Inserted {len(documents)} recipes into ChromaDB.")

# Run initialization on import
initialize_database()

def search_recipes(query: str, max_prep_time: int = 120, diet: str = None, meal_type: str = None, limit: int = 3, allergies: list = None):
    """
    Search for recipes matching the query and constraints.
    """
    query_text = query.strip() if query and query.strip() else "Indian recipe"
    
    results = collection.query(
        query_texts=[query_text],
        n_results=30
    )
    
    valid_recipes = []
    
    if not results['metadatas'] or not results['metadatas'][0]:
        return valid_recipes

    for meta in results['metadatas'][0]:
        total_time = meta['prep_minutes'] + meta.get('cook_minutes', 0)
        if total_time > max_prep_time:
            continue
            
        if diet:
            diet_key = diet.lower()
            diets_list = [d.strip().lower() for d in meta['diets'].split(",")]
            if diet_key not in diets_list:
                continue
                
        if meal_type:
            meal_key = meal_type.lower()
            if meal_key != meta['meal_type'].lower():
                continue
                
        recipe = json.loads(meta['full_json'])
        
        # Hard constraint: Allergies
        if allergies:
            skip = False
            for allergy in allergies:
                allergy_lower = allergy.lower().strip()
                if not allergy_lower:
                    continue
                if allergy_lower in recipe['name'].lower():
                    skip = True
                    break
                for ing in recipe['ingredients']:
                    if allergy_lower in ing['name'].lower():
                        skip = True
                        break
            if skip:
                continue

        # Strip some heavy unneeded data if necessary, or just return it
        valid_recipes.append(recipe)
        
        if len(valid_recipes) == limit:
            break
            
    return valid_recipes
