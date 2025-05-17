from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_weather_endpoint_success(monkeypatch):
    # Mock the geocoder response
    def mock_geocoder_ip(ip):
        class MockGeocoder:
            latlng = [40.7128, -74.0060]  # Mock coordinates for New York City
        return MockGeocoder()
    
    monkeypatch.setattr("geocoder.ip", mock_geocoder_ip)

    # Mock the weather.gov API response
    def mock_requests_get(url):
        class MockResponse:
            def json(self):
                if "points" in url:
                    return {
                        "properties": {
                            "forecastHourly": "https://api.weather.gov/mock-hourly-forecast"
                        }
                    }
                elif "mock-hourly-forecast" in url:
                    return {
                        "properties": {
                            "periods": [
                                {
                                    "startTime": "2023-03-15T14:00:00Z",
                                    "temperature": 55,
                                    "windSpeed": "10 mph",
                                    "shortForecast": "Partly Cloudy"
                                },
                                {
                                    "startTime": "2023-03-15T15:00:00Z",
                                    "temperature": 57,
                                    "windSpeed": "12 mph",
                                    "shortForecast": "Sunny"
                                }
                            ]
                        }
                    }
        return MockResponse()
    
    monkeypatch.setattr("requests.get", mock_requests_get)

    # Make a request to the /weather endpoint
    response = client.get("/weather")
    assert response.status_code == 200
    assert "Partly Cloudy" in response.text
    assert "Sunny" in response.text
    assert "55" in response.text
    assert "57" in response.text

def test_weather_endpoint_no_coordinates(monkeypatch):
    # Mock the geocoder response to return None
    def mock_geocoder_ip(ip):
        class MockGeocoder:
            latlng = None
        return MockGeocoder()
    
    monkeypatch.setattr("geocoder.ip", mock_geocoder_ip)

    # Make a request to the /weather endpoint
    response = client.get("/weather")
    assert response.status_code == 200
    assert "Could not determine coordinates" in response.json()["error"]