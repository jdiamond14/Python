from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import json
import requests
import geocoder

app = FastAPI()
templates = Jinja2Templates(directory="templates")

###Start weather app
@app.get("/weather", response_class=HTMLResponse)
def get_weather(request: Request):
    #flip this back when going to prod (it pulls localhost which cannot be geocoded so we hardcode a real ip)
    #ip = request.client.host
    ip = "107.128.162.44"
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


#test endpoints
@app.get("/get-message")
def hello():
    return {"Message": "You can modify the following string by using the /add, /change, and /remove endpoints: " + static_string}

#Initial static string
static_string = "What?"

@app.post("/add")
async def add_text(text: str):
    global static_string
    static_string += text
    return {"message": "Text added successfully", "current_string": static_string}

@app.put("/change")
async def change_text(new_text: str):
    global static_string
    static_string = new_text
    return {"message": "Text changed successfully", "current_string": static_string}

@app.delete("/remove")
async def remove_text():
    global static_string
    static_string = ""
    return {"message": "Text removed successfully"}



