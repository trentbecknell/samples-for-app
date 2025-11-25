from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI(title="AI Song Generator API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class CompositionRequest(BaseModel):
    prompt: str
    bpm: Optional[int] = None
    key: Optional[str] = None
    length_bars: int = 8

class CompositionResponse(BaseModel):
    success: bool
    message: str
    composition: Optional[Dict] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web UI"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>AI Song Generator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .card { 
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 2.5em; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 1.1em; }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input, textarea { 
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border 0.3s;
            font-family: inherit;
        }
        input:focus, textarea:focus { 
            outline: none;
            border-color: #667eea;
        }
        textarea { 
            resize: vertical;
            min-height: 100px;
        }
        .row { 
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        button { 
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .result { 
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 12px;
            display: none;
        }
        .result.show { display: block; }
        .result h3 { color: #333; margin-bottom: 15px; }
        .result pre { 
            background: white;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .error { 
            background: #fee;
            border: 2px solid #fcc;
        }
        .error h3 { color: #c33; }
        .spinner { 
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .api-link { 
            margin-top: 20px;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 8px;
            text-align: center;
        }
        .api-link a { 
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        .api-link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🎵 AI Song Generator</h1>
            <p class="subtitle">Create AI-powered music compositions with OpenAI</p>
            
            <form id="compositionForm">
                <div class="form-group">
                    <label for="prompt">Music Prompt *</label>
                    <textarea id="prompt" placeholder="e.g., upbeat jazz piano solo with smooth saxophone" required></textarea>
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label for="bpm">BPM (optional)</label>
                        <input type="number" id="bpm" placeholder="120" min="40" max="200">
                    </div>
                    <div class="form-group">
                        <label for="key">Key (optional)</label>
                        <input type="text" id="key" placeholder="C major">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="length_bars">Length (bars)</label>
                    <input type="number" id="length_bars" value="8" min="4" max="32" required>
                </div>
                
                <button type="submit" id="submitBtn">Generate Composition</button>
            </form>
            
            <div id="result" class="result"></div>
            
            <div class="api-link">
                <a href="/docs" target="_blank">📚 API Documentation</a> | 
                <a href="/health">💚 Health Check</a>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('compositionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('submitBtn');
            const result = document.getElementById('result');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Generating...';
            result.classList.remove('show', 'error');
            
            const data = {
                prompt: document.getElementById('prompt').value,
                length_bars: parseInt(document.getElementById('length_bars').value)
            };
            
            const bpm = document.getElementById('bpm').value;
            const key = document.getElementById('key').value;
            if (bpm) data.bpm = parseInt(bpm);
            if (key) data.key = key;
            
            try {
                const response = await fetch('/generate-composition', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const json = await response.json();
                
                if (response.ok) {
                    result.innerHTML = `
                        <h3>✅ Composition Generated!</h3>
                        <pre>${JSON.stringify(json.composition, null, 2)}</pre>
                    `;
                } else {
                    result.classList.add('error');
                    result.innerHTML = `<h3>❌ Error</h3><pre>${json.detail || 'Unknown error'}</pre>`;
                }
            } catch (error) {
                result.classList.add('error');
                result.innerHTML = `<h3>❌ Error</h3><pre>${error.message}</pre>`;
            }
            
            result.classList.add('show');
            btn.disabled = false;
            btn.innerHTML = 'Generate Composition';
        });
    </script>
</body>
</html>
"""

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv('OPENAI_API_KEY'))
    }

@app.post("/generate-composition", response_model=CompositionResponse)
async def generate_composition(request: CompositionRequest):
    """Generate a music composition using OpenAI"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
    
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{
                "role": "user",
                "content": f"Generate a detailed music composition structure for: {request.prompt}. Include chord progressions, melody notes, rhythm patterns, and arrangement suggestions."
            }],
            max_tokens=500
        )
        
        return CompositionResponse(
            success=True,
            message="Composition generated successfully",
            composition={
                "prompt": request.prompt,
                "bpm": request.bpm or 120,
                "key": request.key or "C",
                "length_bars": request.length_bars,
                "ai_response": response.choices[0].message.content
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
