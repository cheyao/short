from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
import aiofiles
from typing_extensions import Annotated
from requests import get
import random
import string
import os.path

codes = {
	"0":{
		"day":{
			"description":"Sunny",
			"image":"http://openweathermap.org/img/wn/01d@2x.png"
		},
		"night":{
			"description":"Clear",
			"image":"http://openweathermap.org/img/wn/01n@2x.png"
		}
	},
	"1":{
		"day":{
			"description":"Mainly Sunny",
			"image":"http://openweathermap.org/img/wn/01d@2x.png"
		},
		"night":{
			"description":"Mainly Clear",
			"image":"http://openweathermap.org/img/wn/01n@2x.png"
		}
	},
	"2":{
		"day":{
			"description":"Partly Cloudy",
			"image":"http://openweathermap.org/img/wn/02d@2x.png"
		},
		"night":{
			"description":"Partly Cloudy",
			"image":"http://openweathermap.org/img/wn/02n@2x.png"
		}
	},
	"3":{
		"day":{
			"description":"Cloudy",
			"image":"http://openweathermap.org/img/wn/03d@2x.png"
		},
		"night":{
			"description":"Cloudy",
			"image":"http://openweathermap.org/img/wn/03n@2x.png"
		}
	},
	"45":{
		"day":{
			"description":"Foggy",
			"image":"http://openweathermap.org/img/wn/50d@2x.png"
		},
		"night":{
			"description":"Foggy",
			"image":"http://openweathermap.org/img/wn/50n@2x.png"
		}
	},
	"48":{
		"day":{
			"description":"Rime Fog",
			"image":"http://openweathermap.org/img/wn/50d@2x.png"
		},
		"night":{
			"description":"Rime Fog",
			"image":"http://openweathermap.org/img/wn/50n@2x.png"
		}
	},
	"51":{
		"day":{
			"description":"Light Drizzle",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Light Drizzle",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"53":{
		"day":{
			"description":"Drizzle",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Drizzle",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"55":{
		"day":{
			"description":"Heavy Drizzle",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Heavy Drizzle",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"56":{
		"day":{
			"description":"Light Freezing Drizzle",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Light Freezing Drizzle",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"57":{
		"day":{
			"description":"Freezing Drizzle",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Freezing Drizzle",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"61":{
		"day":{
			"description":"Light Rain",
			"image":"http://openweathermap.org/img/wn/10d@2x.png"
		},
		"night":{
			"description":"Light Rain",
			"image":"http://openweathermap.org/img/wn/10n@2x.png"
		}
	},
	"63":{
		"day":{
			"description":"Rain",
			"image":"http://openweathermap.org/img/wn/10d@2x.png"
		},
		"night":{
			"description":"Rain",
			"image":"http://openweathermap.org/img/wn/10n@2x.png"
		}
	},
	"65":{
		"day":{
			"description":"Heavy Rain",
			"image":"http://openweathermap.org/img/wn/10d@2x.png"
		},
		"night":{
			"description":"Heavy Rain",
			"image":"http://openweathermap.org/img/wn/10n@2x.png"
		}
	},
	"66":{
		"day":{
			"description":"Light Freezing Rain",
			"image":"http://openweathermap.org/img/wn/10d@2x.png"
		},
		"night":{
			"description":"Light Freezing Rain",
			"image":"http://openweathermap.org/img/wn/10n@2x.png"
		}
	},
	"67":{
		"day":{
			"description":"Freezing Rain",
			"image":"http://openweathermap.org/img/wn/10d@2x.png"
		},
		"night":{
			"description":"Freezing Rain",
			"image":"http://openweathermap.org/img/wn/10n@2x.png"
		}
	},
	"71":{
		"day":{
			"description":"Light Snow",
			"image":"http://openweathermap.org/img/wn/13d@2x.png"
		},
		"night":{
			"description":"Light Snow",
			"image":"http://openweathermap.org/img/wn/13n@2x.png"
		}
	},
	"73":{
		"day":{
			"description":"Snow",
			"image":"http://openweathermap.org/img/wn/13d@2x.png"
		},
		"night":{
			"description":"Snow",
			"image":"http://openweathermap.org/img/wn/13n@2x.png"
		}
	},
	"75":{
		"day":{
			"description":"Heavy Snow",
			"image":"http://openweathermap.org/img/wn/13d@2x.png"
		},
		"night":{
			"description":"Heavy Snow",
			"image":"http://openweathermap.org/img/wn/13n@2x.png"
		}
	},
	"77":{
		"day":{
			"description":"Snow Grains",
			"image":"http://openweathermap.org/img/wn/13d@2x.png"
		},
		"night":{
			"description":"Snow Grains",
			"image":"http://openweathermap.org/img/wn/13n@2x.png"
		}
	},
	"80":{
		"day":{
			"description":"Light Showers",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Light Showers",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"81":{
		"day":{
			"description":"Showers",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Showers",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"82":{
		"day":{
			"description":"Heavy Showers",
			"image":"http://openweathermap.org/img/wn/09d@2x.png"
		},
		"night":{
			"description":"Heavy Showers",
			"image":"http://openweathermap.org/img/wn/09n@2x.png"
		}
	},
	"85":{
		"day":{
			"description":"Light Snow Showers",
			"image":"http://openweathermap.org/img/wn/13d@2x.png"
		},
		"night":{
			"description":"Light Snow Showers",
			"image":"http://openweathermap.org/img/wn/13n@2x.png"
		}
	},
	"86":{
		"day":{
			"description":"Snow Showers",
			"image":"http://openweathermap.org/img/wn/13d@2x.png"
		},
		"night":{
			"description":"Snow Showers",
			"image":"http://openweathermap.org/img/wn/13n@2x.png"
		}
	},
	"95":{
		"day":{
			"description":"Thunderstorm",
			"image":"http://openweathermap.org/img/wn/11d@2x.png"
		},
		"night":{
			"description":"Thunderstorm",
			"image":"http://openweathermap.org/img/wn/11n@2x.png"
		}
	},
	"96":{
		"day":{
			"description":"Light Thunderstorms With Hail",
			"image":"http://openweathermap.org/img/wn/11d@2x.png"
		},
		"night":{
			"description":"Light Thunderstorms With Hail",
			"image":"http://openweathermap.org/img/wn/11n@2x.png"
		}
	},
	"99":{
		"day":{
			"description":"Thunderstorm With Hail",
			"image":"http://openweathermap.org/img/wn/11d@2x.png"
		},
		"night":{
			"description":"Thunderstorm With Hail",
			"image":"http://openweathermap.org/img/wn/11n@2x.png"
		}
	}
};

app = FastAPI();

class Item(BaseModel):
    name: str
    password: str
    file: UploadFile

stat = "";

def generateNonce() -> str:
    len: int = random.randint(16, 40);
    return ''.join(random.choices(string.ascii_letters + string.digits, k=len));

def auth(id: int, otp: str, retry: bool = False) -> bool:
    global stat;

    nonce: str = generateNonce();
    url: str = f"https://api.yubico.com/wsapi/2.0/verify?id={id}&otp={otp}&nonce={nonce}"; 
    resp = get(url);

    if (resp.status_code >= 400 and resp.status_code <= 599 and not retry):
        return auth(id, otp, True);

    if (resp.status_code != 200):
        stat = f"HTTP {resp.status_code}: Failed to reach yubico";
        return False;

    respl = [i.split('=', 1) for i in resp.text.strip().split('\n')];
    resp = {key.strip(): val.strip() for [key, val] in respl};

    if (resp['status'] == "REPLAYED_REQUEST" and not retry):
        return auth(id, otp, True);

    if (resp['status'] != "OK"):
        stat = f"HTTP 403: {resp['status']}";
        return False;

    if (resp['sl'] != "100"):
        stat = f"HTTP 403: Only {resp['sl']}% of servers validated";
        return False;

    return True;

async def upload(file: UploadFile, name: str) -> None:
    async with aiofiles.open(f"files/{name}", 'wb') as ofile:
        contents = await file.read();
        await ofile.write(contents);

@app.post('/upload')
async def results(password: Annotated[str, Form()], file: UploadFile, name: Annotated[str, Form()]):
    global stat;
    stat = ""

    if auth(105543, password) == True:
        await upload(file, name);
        stat = "Success";
        return;

    if auth(105538, password) == True:
        await upload(file, name);
        stat = "Success";
        return;

async def getWeather():
    url: str = f"https://api.open-meteo.com/v1/forecast?latitude=43.5513&longitude=7.0127&current=rain,temperature_2m,is_day,weather_code&forecast_days=1&models=meteofrance_seamless";
    resp = get(url);

    if (resp.status_code != 200):
        return "Failed to call weather API";

    data = resp.json()["current"];
    dn = "day" if data["is_day"] else "night";
    rain = data["rain"];
    temp = data["temperature_2m"];
    desc = codes[str(data["weather_code"])][dn]["description"];
    return f"Temperature: {temp} Rain: {rain} Weather: {desc}";

@app.get('/weather')
async def weather():
    return await getWeather();

@app.get('/status')
async def status():
    return {"status": stat};

@app.get('/')
async def index():
    return FileResponse("index.html")

@app.get('/url')
async def url():
    return FileResponse("url.html")

@app.get('/url.html')
async def url2():
    return FileResponse("url.html")

@app.get('/api')
async def api():
    return FileResponse("static/api.json")

@app.get('/{file}')
async def file(file: str):
    if (os.path.isfile(f"files/{file}")):
        return FileResponse(f"files/{file}")

    return FileResponse(f"static/404.html")

@app.get('/static/{full_path:path}')
async def static(full_path: str):
    if (os.path.isfile(f"static/{full_path}")):
        return FileResponse(f"static/{full_path}")
    if (os.path.isfile(f"static/{full_path}.html")):
        return FileResponse(f"static/{full_path}.html")
    if (os.path.isfile(f"static/{full_path}/index.html")):
        return FileResponse(f"static/{full_path}/index.html")
    if (os.path.isfile(f"static/{full_path}.gz")):
        return FileResponse(f"static/{full_path}.gz", headers={"Content-Encoding": "gzip"})

    return FileResponse(f"static/404.html")

