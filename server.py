from fastapi import FastAPI

app = FastAPI();

@app.get('/upload')
def results():
    return results
