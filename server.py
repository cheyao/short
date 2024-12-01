from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
import aiofiles
from typing_extensions import Annotated
from requests import get
import random
import string
import os.path

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

@app.get('/{file}')
async def file(file: str):
    return FileResponse(f"files/{file}")

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

