from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import json
import requests
import geocoder
import ssl

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# Enable SSL eventually
#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#ssl_context.load_cert_chain('/cert/cert.pem', keyfile='/cert/key.pem')

###Start weather app
@app.get("/weather", response_class=HTMLResponse)
def get_weather(request: Request):
    ip = request.client.host
    geocoded_ip = geocoder.ip(ip)
    coor = geocoded_ip.latlng
    if coor:  # Ensure coor is not None
        coor_str = f"{coor[0]},{coor[1]}"  # Convert to "lat,lng" format
        url = "https://api.weather.gov/points/" + coor_str
        response = requests.get(url)
        data = response.json()  
        hrfc = data["properties"]["forecastHourly"]
        hrfc_data = requests.get(hrfc).json()

        periods = hrfc_data["properties"]["periods"]
        for period in periods:
            utc_time = datetime.fromisoformat(period["startTime"].replace("Z", "+00:00"))
            period["startTime"] = utc_time.strftime("%Y-%m-%d %I:%M %p")  # Format: YYYY-MM-DD HH:MM AM/PM

        return templates.TemplateResponse(
            "weather.html",
            {"request": request, "periods": periods},
        )
    else:
        return {"error": "Could not determine coordinates"}