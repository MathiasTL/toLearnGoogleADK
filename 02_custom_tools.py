import asyncio
import json
import requests
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from utils.runner import run_agent_query, session_service, my_user_id

"""
Custom Tools Example: Spontaneous Day Trip Generator

This agent generates a full-day trip itinerary based on the user's mood, interests, and budget. It uses a custom tool to fetch real-time information about venues and events.

⚠️ CONCEPTO CLAVE: el docstring ES lo que el LLM lee para decidir
#    cuándo y cómo usar esta herramienta. Debe ser descriptivo.

"""

def get_live_weather_forecast(location: str) -> dict:
    """
    Retrieves the current weather and a short forecast for a given city.
    Use this tool when the user asks about weather conditions, temperature,
    or climate for trip planning purposes.

    Args:
        city: The name of the city to get the weather forecast for.

    Returns:
        A dictionary containing current weather data and forecast,
        or an error message if the city is not found.
    """
    
    base_url = "https://wttr.in"
    try:
        response = requests.get(
            f"{base_url}/{location}",
            params={"format": "j1"},
            timeout=10
        )
        response.raise_for_status()
        weather_data = response.json()
        
        current = weather_data["current_condition"][0]
        weather_desc = current["weatherDesc"][0]["value"]
        temp_c       = current["temp_C"]
        feels_like_c = current["FeelsLikeC"]
        humidity     = current["humidity"]
        wind_kmph    = current["windspeedKmph"]

        return {
            "city": location,
            "condition": weather_desc,
            "temperature_celsius": temp_c,
            "feels_like_celsius": feels_like_c,
            "humidity_percent": humidity,
            "wind_speed_kmph": wind_kmph,
            "status": "success"
        }
    except requests.exceptions.HTTPError:
        return {"status": "error", "message": f"City '{location}' not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# Wrap the function in a FunctionTool to make it available to the agent
weather_tool = FunctionTool(func=get_live_weather_forecast)

# Define the agent with instructions and tools
weather_trip_agent = Agent(
    name="weather_trip_agent",
    model="gemini-2.5-flash",
    description="A travel agent that uses real weather data to give trip advice.",
    instruction="""You are a smart travel assistant with access to live weather data.
    When a user asks about visiting a destination, ALWAYS use the
    get_live_weather_forecast tool to get real weather data first.
    Then provide tailored advice based on the actual conditions:
    - What to pack
    - Best activities for the weather
    - Any weather-related warnings""",
    tools=[weather_tool]
)

# Example usage
async def main():
    session = await session_service.create_session(
        app_name=weather_trip_agent.name,
        user_id=my_user_id
        )
    print(f"✅ Session created → ID: {session.id} | User: {my_user_id}")
    
    await run_agent_query(
        agent=weather_trip_agent,
        query="I'm planning a trip to Lima, Peru this week. What's the weather like and what should I pack?",
        session=session,
        user_id=my_user_id
    )
    
if __name__ == "__main__":
    asyncio.run(main())