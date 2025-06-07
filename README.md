# Creative AI Foodie Tour Planner  

## Overview  

The Creative AI Foodie Tour Planner is a Streamlit web application that generates personalized one-day foodie tours for multiple cities. It uses real-time weather data, local iconic dishes, and top-rated restaurants to create tailored breakfast, lunch, and dinner narratives. The app recommends indoor or outdoor dining based on the weather and includes clickable Google Maps links for restaurant locations.  

---  

## Features  

- Supports multiple city inputs and loops through each city.  
- Fetches today's weather and provides clear indoor/outdoor dining recommendations.  
- Selects 3 iconic local dishes per city, including vegan options if requested.  
- Finds top-rated restaurants serving these dishes using the Foursquare API.  
- Creates a creative and engaging foodie tour itinerary with local trivia and ambience suggestions.  
- Displays clickable Google Maps links for restaurant locations.  
- Provides a smooth, interactive Streamlit UI.  

---  
  
## Installation  


1. Install dependencies:  
```bash  
pip install -r requirements.txt  
```

2. Add your API keys for OpenWeather, Julep, and Foursquare in the code or environment variables.  

---  

## Usage  

Run the Streamlit app:  
```bash
streamlit run app.py  
```

- Enter one or more cities separated by commas (e.g., `Paris, New York, Tokyo`).  
- Check the vegan option box if desired.  
- Click "Generate Tour" to get foodie tours for all listed cities.  
- View weather, indoor/outdoor dining suggestions, local dishes, and top restaurants with clickable map links.  

---  

## Code Highlights  

- Uses OpenWeather API for current weather data.  
- Uses Julep API for creative foodie tour generation with weather and vegan preferences.  
- Uses Foursquare Places API to fetch restaurant data with detailed addresses.  
- Extracts iconic dishes from the tour narrative.  
- Supports multiple cities input and loops over each for complete tour generation.  
- Separates and highlights indoor/outdoor dining recommendations clearly in the UI.  
- Creates clickable Google Maps URLs for restaurant locations.  

---  
  
## Example  

Input:  
```
Cities: Paris, Bangalore  
Include vegan options: Yes  
```  

Output:  
- Weather and indoor/outdoor dining recommendation for Paris  
- Breakfast, Lunch, Dinner with iconic dishes for Paris  
- Top restaurants for each dish with clickable map links  
- Repeat the same for Bangalore  

---  

## Notes  

- Ensure valid API keys are set for OpenWeather, Julep, and Foursquare.  
- Julep provides a generous free tier; no need to create your own LLM API key.  
- The app focuses on user-friendly, creative food tours incorporating local culture and weather.  
