# =============================================================================
# Streamlit with MealDB API and ChatBot
# =============================================================================

import streamlit as st
import pandas as pd
import requests
import ollama
from langchain_community.llms import Ollama

# Function to generate response using gemma:2b model
def generate_response_gemma(prompt):
    try:
        response = ollama.generate(model='gemma:2b', prompt=prompt)
        return response['response']
    except Exception as e:
        return f"An error occurred: {e}"

# Function to generate response using llama2 model
def generate_response_llama(prompt):
    try:
        llm = Ollama(model="llama2")
        response = llm.invoke(prompt)
        return response
    except Exception as e:
        return f"An error occurred: {e}"

# Function to fetch the list of recognized ingredients from TheMealDB API
def fetch_ingredient_list():
    url = 'https://www.themealdb.com/api/json/v1/1/list.php?i=list'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()['meals']
        except ValueError:
            st.error("Error decoding JSON response")
            return None
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

# Function to fetch the list of meal categories from TheMealDB API
def fetch_category_list():
    url = 'https://www.themealdb.com/api/json/v1/1/categories.php'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return [category['strCategory'] for category in response.json()['categories']]
        except ValueError:
            st.error("Error decoding JSON response")
            return None
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

# Function to fetch the list of meal areas from TheMealDB API
def fetch_area_list():
    url = 'https://www.themealdb.com/api/json/v1/1/list.php?a=list'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return [area['strArea'] for area in response.json()['meals']]
        except ValueError:
            st.error("Error decoding JSON response")
            return None
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

# Function to search recipes using TheMealDB API
def search_recipes_by_ingredients(ingredients):
    results = []
    for ingredient in ingredients:
        url = f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}'
        response = requests.get(url)
        if response.status_code == 200:
            try:
                json_response = response.json()
                if json_response['meals']:
                    results.extend(json_response['meals'])
            except ValueError:
                st.error("Error decoding JSON response")
                st.text(response.text)
                return None
        else:
            st.error(f"API request failed with status code {response.status_code}")
            st.text(response.text)
            return None
    return results

# Function to search recipes by category and area
def search_recipes_by_category_and_area(category, area):
    url = f'https://www.themealdb.com/api/json/v1/1/filter.php?c={category}&a={area}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()['meals']
        except ValueError:
            st.error("Error decoding JSON response")
            return None
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

# Function to load items from Excel
def load_items(file_path):
    return pd.read_excel(file_path)

# Function to normalize ingredient names
def normalize_ingredients(product_names, recognized_ingredients):
    recognized_ingredient_names = [ingredient['strIngredient'] for ingredient in recognized_ingredients]
    normalized_names = [name for name in product_names if name in recognized_ingredient_names]
    not_recognized_names = [name for name in product_names if name not in recognized_ingredient_names]
    return normalized_names, not_recognized_names

# Function to get full details of a recipe by ID
def get_recipe_details(recipe_id):
    url = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={recipe_id}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()['meals'][0]
        except (ValueError, KeyError):
            st.error("Error decoding JSON response")
            return None
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

# Main function for the Streamlit app
def main():
    # Setting up the Streamlit app's title with centered CSS
    st.markdown("<h1 style='text-align: center;'>Lumine Application</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Chat with Chef 🤖", "Your Recipe Haven 🏠", "Recipe Roulette 🎲", "Magic Recipe Mixer 🍲"])

    with tab1:
        chatbot_tab()

    with tab2:
        upload_products_tab()

    with tab3:
        select_filters_tab()

    with tab4:
        recipe_page()

# ChatBot tab function
def chatbot_tab():
    st.title("Lumine AI ChatBot")

    st.markdown("""
    This AI Chatbot is your kitchen sidekick! From researching recipes to detailed step-by-step instructions, it's got you covered. Want to explore wild food combos? Just ask! Boost your culinary game with tips on ingredients, techniques, and more. Get ready to cook up some fun! 🍳👩‍🍳🔪
    """)

    # Initialize session state to keep track of the conversation
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""


    # Model selection
    model_choice = st.selectbox(
        "Choose a Chef:",
        ("Chef De-Code", "Chef App-etizer")
    )

    # User input with pre-written text
    default_text = "Could you suggest me a recipe with chicken, potatoes and vegetables?"
    user_input = st.text_input("Aspiring Chef:", value=default_text, key="input", on_change=lambda: st.session_state.update(user_input=st.session_state.input))

    # Generate response when the user submits input
    if st.button("Let's Cook"):
        if user_input:
            # Clear previous conversation
            st.session_state.history = []

            # Append user input to history
            st.session_state.history.append(f"Aspiring Chef: {user_input}")

            # Show loading spinner and status message
            with st.spinner("Lumine's cooking up a response... Almost ready! 🍳✨"):
                # Generate response based on the selected model
                if model_choice == "gemma:2b":
                    bot_response = generate_response_gemma(user_input)
                else:
                    bot_response = generate_response_llama(user_input)

            # Append bot response to history
            st.session_state.history.append(f"Culinary Luminary: {bot_response}")

            # Clear input
            st.session_state.user_input = ""

    # Display the conversation history
    for message in st.session_state.history:
        if message.startswith("Aspiring Chef:"):
            st.write(message)
        elif message.startswith("Culinary Luminary:"):
            st.success(message)

# Upload products tab function
def upload_products_tab():
    st.title("Ready to showcase your discounted products?")
    st.write("""
    Simply upload your Excel file with the column 'Product Name' populated with all your bargain buys. Let's celebrate those smart shopping successes together! Minimize waste, maximize savings!
    """)

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx", key="uploader")

    if uploaded_file:
        df = load_items(uploaded_file)
        st.write("### Your Purchased Discounted Products")
        st.write(df)

        # Extract product names
        product_names = df['Product Name'].unique().tolist()

        # Fetch recognized ingredients from TheMealDB API
        with st.spinner("Fetching recognized Lumine's ingredients..."):
            recognized_ingredients = fetch_ingredient_list()

        if recognized_ingredients:
            # Normalize ingredient names
            normalized_names, not_recognized_names = normalize_ingredients(product_names, recognized_ingredients)

            if st.button("Let's Spice Things Up", key="upload_get_recipes"):
                with st.spinner("Fetching Lumine's recipes..."):
                    recipes = search_recipes_by_ingredients(normalized_names)

                if recipes:
                    st.success("Recipes unlocked! Head to the 'Recipe Generator' tab for the perfect match.")

                    # Find the recipe with the most matching ingredients
                    best_recipe = None
                    best_match_count = 0
                    for recipe in recipes:
                        recipe_details = get_recipe_details(recipe['idMeal'])
                        if recipe_details:
                            match_count = sum(1 for i in range(1, 21) if recipe_details.get(f'strIngredient{i}') in normalized_names)
                            if match_count > best_match_count:
                                best_match_count = match_count
                                best_recipe = recipe_details

                    if best_recipe:
                        st.session_state['best_recipe'] = best_recipe
                    else:
                        st.write("Oops! No recipes found with those ingredients. Time to get creative or try a different combo!")
                else:
                    st.write("No recipes found. Time to get creative in the kitchen!")

# Select filters tab function
def select_filters_tab():
    st.title("Feeling indecisive about your culinary cravings?")
    st.write("""
    Let's roll the dice and spice up your day with a randomly delicious dish! Choose your food category and area to surprise your taste buds today!
    """)
    # Fetch categories and areas for the filters
    with st.spinner("Fetching lumine's food categories and areas..."):
        categories = fetch_category_list()
        areas = fetch_area_list()

    selected_category = st.selectbox("Choose a food category", ["All"] + categories)
    selected_area = st.selectbox("Choose an area", ["All"] + areas)

    if st.button("Let's Spice Things Up", key="filter_get_recipes"):
        with st.spinner("Fetching Lumine's 'recipes..."):
            if selected_category != "All" or selected_area != "All":
                recipes = search_recipes_by_category_and_area(selected_category, selected_area)
            else:
                st.error("Pick a Food Category or Area for Recommendations.")
                return

        if recipes:
            st.success("Recipes unlocked! Head to the 'Recipe Generator' tab for the perfect match.")

            # Find the best matching recipe
            best_recipe = recipes[0] if recipes else None
            if best_recipe:
                st.session_state['best_recipe'] = get_recipe_details(best_recipe['idMeal'])
        else:
            st.write("Oops! No recipes found with those ingredients. Time to get creative or try a different combo!")

# Recipe page function
def recipe_page():
    best_recipe = st.session_state.get('best_recipe')
    if best_recipe:
        st.title(best_recipe['strMeal'])
        col1, col2 = st.columns([1, 0.5])
        with col1:
            st.image(best_recipe['strMealThumb'], width=450)
        with col2:
            st.write("### Ingredients")
            ingredients = []
            for i in range(1, 21):
                ingredient = best_recipe.get(f'strIngredient{i}')
                measure = best_recipe.get(f'strMeasure{i}')
                if ingredient and measure:
                    ingredients.append(f"{measure} {ingredient}")
            # Using markdown to list ingredients with bullet points
            st.markdown("\n".join([f"- {ingredient}" for ingredient in ingredients]))

        st.write("### Instructions")
        st.write(best_recipe['strInstructions'])

        st.write("### Source")
        st.write(f"[{best_recipe.get('strSource', 'No link available')}]({best_recipe.get('strSource', '#')})")
    else:
        st.write("No recipe selected! Head back to the Home tab for some culinary inspiration.")

if __name__ == "__main__":
    main()
