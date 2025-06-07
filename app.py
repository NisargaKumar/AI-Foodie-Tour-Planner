import streamlit as st 
import requests
import time
import yaml
from julep import Julep
import re
from dotenv import load_dotenv
import os
load_dotenv()


# ==== API KEYS - Replace these ====
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
JULEP_API_KEY = os.getenv("JULEP_API_KEY")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

# --- Set page config ---
st.set_page_config(
    page_title="Creative AI Foodie Tour Planner",
    page_icon="🍽️"
)

# --- Functions ---

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data.get("weather"):
            condition = data["weather"][0]["description"].capitalize()
            temperature = data["main"]["temp"]
            return f"{condition}, {temperature}°C"
        else:
            return "Weather unavailable"
    except:
        return "Weather unavailable"

def get_restaurants_foursquare(city, dish, limit=3):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {"Authorization": FOURSQUARE_API_KEY}
    params = {
        "query": dish,
        "near": city,
        "limit": limit
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        restaurants = []
        for place in data.get("results", []):
            name = place.get("name")
            location_info = place.get("location", {})
            address_parts = [
                location_info.get("address"),
                location_info.get("locality"),
                location_info.get("region"),
                location_info.get("country")
            ]
            full_address = ", ".join([part for part in address_parts if part])
            if not full_address:
                full_address = "Address unavailable"
            restaurants.append({"name": name, "address": full_address})
        return restaurants
    except Exception as e:
        st.error(f"Error fetching restaurants: {e}")
        return []

@st.cache_resource
def get_julep_client():
    return Julep(api_key=JULEP_API_KEY)

@st.cache_resource
def setup_julep_agent_task(_client):
    agent = _client.agents.create(
        name="Creative Foodie Tour Planner",
        model="claude-3.5-sonnet",
        about="Create creative foodie tours including dishes, drinks, trivia, and ambience based on weather and preferences."
    )
    task_yaml = """
    name: Plan a creative foodie tour
    description: Create a one-day itinerary considering weather, iconic local dishes (with vegan options), drinks, desserts, local trivia, and ambience.
    main:
    - prompt:
      - role: system
        content: |
          You are a fun, creative travel planner. Your job:
          1. Use the weather to recommend indoor or outdoor dining
          2. Pick 3 iconic local dishes, with at least 1 vegan option if requested
          3. Suggest local drinks and desserts
          4. Include fun local trivia or history about the city or food
          5. Suggest ambience/vibe for the venues
          6. Create a catchy, creative tour name
          7. Present venue, ambience, and short review snippets on separate lines
          8. Output breakfast, lunch, and dinner plans tailored to weather and preferences
          9. At the end, list iconic dishes clearly as a bullet list titled "Iconic Dishes:" with dish names only, like:
             Iconic Dishes:
             - Dish 1
             - Dish 2
             - Dish 3
          10. Clearly mention dining recommendation (indoor or outdoor) in the narrative.
      - role: user
        content: |
          Weather: {steps[0].input.weather}
          Vegan option: {steps[0].input.vegan}
          Create a foodie tour for {steps[0].input.city} with the above requirements.
    """
    task_def = yaml.safe_load(task_yaml)
    task = _client.tasks.create(agent_id=agent.id, **task_def)
    return agent, task

def extract_dishes(tour_text):
    pattern = r"Iconic Dishes:\s*((?:- .+\n?)+)"
    match = re.search(pattern, tour_text, re.IGNORECASE)
    dishes = []
    if match:
        dish_lines = match.group(1).strip().split('\n')
        for line in dish_lines:
            dish = line.strip().lstrip('- ').strip()
            if dish and len(dish) > 2:
                dishes.append(dish)
    else:
        meal_lines = re.findall(r"(Breakfast|Lunch|Dinner):\s*(.+)", tour_text, re.I)
        for _, dish_str in meal_lines:
            split_dishes = re.split(r",| and | with ", dish_str)
            for d in split_dishes:
                clean_dish = d.strip().strip(".")
                if clean_dish and len(clean_dish) > 2 and clean_dish.lower() not in ['the', 'and', 'or']:
                    if len(dishes) < 3:
                        dishes.append(clean_dish)
    return dishes[:3]

def extract_dining_recommendation(tour_text):
    # Look for indoor/outdoor dining mention
    match = re.search(r"(indoor|outdoor) dining", tour_text, re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    else:
        return "Not specified"

# --- Streamlit UI ---

st.title("🌍 Creative AI Foodie Tour Planner")
st.write("Enter one or more cities (comma separated) and your preferences, then get personalized foodie tours!")

cities_input = st.text_input("Enter cities (comma separated)", value="Paris, Bangalore, New York")
vegan_pref = st.checkbox("Include vegan options?", value=False)

if st.button("Generate Tours") and cities_input.strip():
    cities = [c.strip() for c in cities_input.split(",") if c.strip()]
    client = get_julep_client()
    agent, task = setup_julep_agent_task(client)

    for city in cities:
        st.markdown(f"---\n## Foodie Tour for {city}")

        with st.spinner(f"Fetching weather for {city}..."):
            weather = get_weather(city)
        st.success(f"Weather in {city}: {weather}")

        with st.spinner(f"Generating foodie tour for {city}..."):
            execution = client.executions.create(
                task_id=task.id,
                input={"city": city, "weather": weather, "vegan": vegan_pref}
            )
            while True:
                result = client.executions.get(execution.id)
                if result.status in ["succeeded", "failed"]:
                    break
                time.sleep(1)

        if result.status == "succeeded":
            tour_text = result.output['choices'][0]['message']['content']

            # Extract dining recommendation
            dining_reco = extract_dining_recommendation(tour_text)
            st.markdown(f"**Dining recommendation:** _{dining_reco} dining_\n")

            st.markdown("### Tour Narrative:")
            for line in tour_text.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.lower().startswith("review:"):
                    continue  # skip review lines
                elif re.match(r"^(BREAKFAST|LUNCH|DINNER)", line, re.IGNORECASE):
                    st.subheader(line)
                elif ":" in line:
                    key, val = line.split(":", 1)
                    st.markdown(f"**{key.strip()}:** {val.strip()}")
                else:
                    st.write(line)

            dishes = extract_dishes(tour_text)
            st.markdown("### Top Restaurants for iconic dishes:")
            for dish in dishes:
                st.markdown(f"**{dish}:**")
                with st.spinner(f"Fetching top restaurants for {dish} in {city}..."):
                    restaurants = get_restaurants_foursquare(city, dish)
                if restaurants:
                    for r in restaurants:
                        name = r['name']
                        address = r['address']
                        query = f"{name} {address}".replace(' ', '+')
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={query}"
                        st.markdown(f"- [{name}]({maps_url}) — {address}")
                else:
                    st.write("No restaurants found.")
        else:
            st.error(f"Failed to generate foodie tour for {city}. Please try again.")
