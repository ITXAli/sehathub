from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import triage, mediscan, labsense, nutriscan

app = FastAPI(title="SehatHub AI API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(triage.router, prefix="/api/triage", tags=["Triage"])
app.include_router(mediscan.router, prefix="/api/mediscan", tags=["MediScan"])
app.include_router(labsense.router, prefix="/api/labsense", tags=["LabSense"])
app.include_router(nutriscan.router, prefix="/api/nutriscan", tags=["NutriScan"])

@app.get("/")
def read_root():
    return {"status": "SehatHub AI Backend is running"}
