from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from requests import get

app = FastAPI();

class Item(BaseModel):
    name: str
    password: str

def generateNonce():
    return '1';

@app.put('/upload')
async def results(item: Item):
    url = f"https://api.yubico.com/wsapi/2.0/verify?id=${105538}&otp=${item.password}&nonce=${generateNonce()}"; 
    resp = get(url);

    if (resp.status_code != 200):
        return HTTPException(status_code=resp.status_code, detail="Failed to reach yubico");

    if (resp.json()['status'] != "OK"):
        return HTTPException(status_code=403, detail=resp.json()['status']);

