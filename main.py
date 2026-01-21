from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Emails.router import router as email_router


app = FastAPI(
    title= "Ville Propre API",
    Version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_router)

@app.get("/")
def root():
    return {"message": "Welcome to Ville Propre API", "status": "operational"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)