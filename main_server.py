from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="AI Song Generator API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class CompositionRequest(BaseModel):
    prompt: str
    bpm: Optional[int] = None

@app.get("/")
async def root():
    return {"status": "running", "openai": bool(os.getenv('OPENAI_API_KEY'))}

@app.get("/health")
async def health():
