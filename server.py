from fastapi import FastAPI, HTTPException, UploadFile, Form
from pydantic import BaseModel
import aiofiles
from typing import Union
from typing_extensions import Annotated
from requests import get
import random
import string

app = FastAPI();

class Item(BaseModel):
    name: str
    password: str
    file: UploadFile

def generateNonce() -> str:
    len: int = random.randint(16, 40);
    return ''.join(random.choices(string.ascii_letters + string.digits, k=len));

def auth(id: int, otp: str, retry: bool = False) -> bool | HTTPException:
    nonce: str = generateNonce();
    url: str = f"https://api.yubico.com/wsapi/2.0/verify?id={id}&otp={otp}&nonce={nonce}"; 
    resp = get(url);

    if (resp.status_code >= 400 and resp.status_code <= 599 and not retry):
        return auth(id, otp, True);

    if (resp.status_code != 200):
        return HTTPException(status_code=resp.status_code, detail="Failed to reach yubico");

    respl = [i.split('=', 1) for i in resp.text.strip().split('\n')];
    resp = {key.strip(): val.strip() for [key, val] in respl};

    if (resp['status'] == "REPLAYED_REQUEST" and not retry):
        return auth(id, otp, True);

    if (resp['status'] != "OK"):
        return HTTPException(status_code=403, detail=resp['status']);

    if (resp['sl'] != "100"):
        return HTTPException(status_code=403, detail=f"Only {resp['sl']}% of servers validated");

    return True

async def upload(file: UploadFile, name: str):
    async with aiofiles.open(name, 'wb') as ofile:
        contents = await file.read();
        await ofile.write(contents);

    return "Success";

@app.post('/upload')
async def results(password: Annotated[str, Form()], file: UploadFile, name: Annotated[str, Form()]):
    result1 = auth(105543, password); # Main Yubikey
    if type(result1) is bool and result1 == True:
        return await upload(file, name);

    result2 = auth(105538, password); # Back Yubikey
    if type(result2) is bool and result2 == True:
        return await upload(file, name);

    if type(result1) is HTTPException:
        return result1;

    if type(result2) is HTTPException:
        return result2;


