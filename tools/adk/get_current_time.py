import datetime
import pytz
import requests
from typing import Dict, Optional

def get_timezone_for_city(city: str) -> Optional[str]:
    """Get timezone for a city using the TimeZoneDB API.
    
    Args:
        city (str): Name of the city
        
    Returns:
        Optional[str]: Timezone identifier (e.g. 'America/New_York') or None if not found
    """
    # You can get a free API key from https://timezonedb.com/
    API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
    base_url = "http://api.timezonedb.com/v2.1/get-time-zone"
    
    try:
        params = {
            "key": API_KEY,
            "format": "json",
            "by": "zone",
            "zone": city
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            return data["zoneName"]
        return None
    except Exception as e:
        print(f"Error fetching timezone: {str(e)}")
        return None

def get_current_time(city: str) -> Dict[str, str]:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: A dictionary containing status and either a report (on success) or an error_message (on failure).
    """

    print(f"Getting current time for {city}")

    # Try to get the timezone for the city
    tz_identifier = get_timezone_for_city(city)
    
    if not tz_identifier:
        # Fallback to common city mappings if API fails
        common_cities = {
            "new york": "America/New_York",
            "london": "Europe/London",
            "tokyo": "Asia/Tokyo",
            "paris": "Europe/Paris",
            "sydney": "Australia/Sydney",
            "berlin": "Europe/Berlin",
            "moscow": "Europe/Moscow",
            "beijing": "Asia/Shanghai",
            "dubai": "Asia/Dubai",
            "singapore": "Asia/Singapore",
            "seoul": "Asia/Seoul",
            "mumbai": "Asia/Kolkata",
            "cairo": "Africa/Cairo",
            "rio de janeiro": "America/Sao_Paulo",
            "mexico city": "America/Mexico_City",
            "los angeles": "America/Los_Angeles",
            "chicago": "America/Chicago",
            "toronto": "America/Toronto",
            "amsterdam": "Europe/Amsterdam",
            "rome": "Europe/Rome"
        }
        
        tz_identifier = common_cities.get(city.lower())
    
    if not tz_identifier:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I couldn't find timezone information for {city}. "
                "Please try a major city name or check the spelling."
            ),
        }
    
    try:
        tz = pytz.timezone(tz_identifier)
        now = datetime.datetime.now(tz)
        report = (
            f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        )
        return {"status": "success", "report": report}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error getting time for {city}: {str(e)}"
        }
