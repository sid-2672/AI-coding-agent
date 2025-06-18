"""
Beautiful FastAPI web server for the God-Tier Coding Agent
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import os
from pathlib import Path
import aiofiles

from .model import CodeAssistant
from .memory import ConversationMemory
from .analyzer import CodeAnalyzer

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None

class CodeRequest(BaseModel):
    prompt: str
    language: Optional[str] = None
    template: Optional[str] = None

class AnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    deep_analysis: bool = False

class ConnectionManager:
    """Manages WebSocket connections for real-time features"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

def create_app(model_path: str = "deepseek-coder-1.3b-instruct.Q4_K_M.gguf") -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="🚀 God-Tier Coding Agent",
        description="The Ultimate Offline AI Developer Assistant",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize components
    assistant = CodeAssistant(model_path)
    memory = ConversationMemory()
    analyzer = CodeAnalyzer(model_path)
    manager = ConnectionManager()
    
    # Create necessary directories
    static_dir = Path("static")
    templates_dir = Path("templates")
    uploads_dir = Path("uploads")
    
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)
    uploads_dir.mkdir(exist_ok=True)
    
    # Initialize templates
    templates = Jinja2Templates(directory="templates")
    
    @app.on_startup
    async def startup_event():
        """Initialize the application"""
        print("🚀 God-Tier Coding Agent Web Server Starting...")
        print("🤖 Loading AI model...")
        # Create default templates and static files if they don't exist
        await create_default_ui_files()
    
    @app.get("/", response_class=HTMLResponse)
    async def home():
        """Serve the main application"""
        return await get_index_html()
    
    @app.post("/api/chat")
    async def chat_endpoint(request: ChatMessage):
        """Handle chat messages"""
        try:
            response = assistant.generate_response(request.message, request.context or "")
            memory.add_exchange(request.message, response)
            
            return {
                "response": response,
                "status": "success",
                "context": memory.get_context()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/code/generate")
    async def generate_code(request: CodeRequest):
        """Generate code from prompt"""
        try:
            response = assistant.generate_advanced_code(
                request.prompt,
                language=request.language,
                template=request.template
            )
            
            return {
                "code": response,
                "status": "success",
                "language": request.language
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/code/analyze")
    async def analyze_code(request: AnalysisRequest):
        """Analyze code and provide insights"""
        try:
            results = analyzer.analyze_code_string(
                request.code,
                request.language,
                deep_analysis=request.deep_analysis
            )
            
            return {
                "analysis": results,
                "status": "success"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/files/upload")
    async def upload_file(file: UploadFile = File(...)):
        """Handle file uploads"""
        try:
            file_path = uploads_dir / file.filename
            
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
            
            return {
                "filename": file.filename,
                "path": str(file_path),
                "status": "success"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/files/list")
    async def list_files():
        """List uploaded files"""
        try:
            files = []
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    files.append({
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
            
            return {"files": files, "status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """Handle WebSocket connections for real-time features"""
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data["type"] == "chat":
                    response = assistant.generate_response(message_data["message"])
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "response",
                            "message": response
                        }),
                        websocket
                    )
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    @app.get("/api/stats")
    async def get_stats():
        """Get application statistics"""
        stats = memory.get_statistics()
        return {
            "conversation_stats": stats,
            "model_info": {
                "name": Path(model_path).name,
                "path": model_path
            },
            "connections": len(manager.active_connections),
            "status": "running"
        }
    
    # Mount static files (will be created by create_default_ui_files)
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app

async def create_default_ui_files():
    """Create default UI files if they don't exist"""
    
    # Create index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 God-Tier Coding Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-dark.min.css" rel="stylesheet">
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .chat-container {
            max-height: 60vh;
            overflow-y: auto;
        }
        .code-editor {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="gradient-bg">
        <div class="container mx-auto px-4 py-8">
            <div class="text-center">
                <h1 class="text-5xl font-bold mb-4">🚀 God-Tier Coding Agent</h1>
                <p class="text-xl mb-8">The Ultimate Offline AI Developer Assistant</p>
            </div>
        </div>
    </div>

    <div class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Chat Interface -->
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-2xl font-bold mb-4">💬 AI Chat</h2>
                <div id="chat-container" class="chat-container bg-gray-700 rounded p-4 mb-4">
                    <p class="text-gray-400">Hello! I'm your God-Tier AI coding assistant. Ask me anything!</p>
                </div>
                <div class="flex gap-2">
                    <input id="chat-input" type="text" placeholder="Ask me anything..." 
                           class="flex-1 px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button id="send-btn" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded transition">Send</button>
                </div>
            </div>

            <!-- Code Generator -->
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-2xl font-bold mb-4">⚡ Code Generator</h2>
                <textarea id="code-prompt" placeholder="Describe what code you want to generate..." 
                          class="w-full h-32 px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"></textarea>
                <div class="flex gap-2 mb-4">
                    <select id="language-select" class="px-4 py-2 bg-gray-700 rounded">
                        <option value="">Auto-detect</option>
                        <option value="python">Python</option>
                        <option value="javascript">JavaScript</option>
                        <option value="typescript">TypeScript</option>
                        <option value="java">Java</option>
                        <option value="cpp">C++</option>
                        <option value="rust">Rust</option>
                        <option value="go">Go</option>
                    </select>
                    <button id="generate-btn" class="px-6 py-2 bg-green-600 hover:bg-green-700 rounded transition">Generate</button>
                </div>
                <div id="generated-code" class="bg-gray-700 rounded p-4 code-editor"></div>
            </div>
        </div>

        <!-- Code Analyzer -->
        <div class="mt-8 bg-gray-800 rounded-lg p-6">
            <h2 class="text-2xl font-bold mb-4">🔍 Code Analyzer</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                    <textarea id="analyze-code" placeholder="Paste your code here for analysis..." 
                              class="w-full h-64 px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 code-editor mb-4"></textarea>
                    <button id="analyze-btn" class="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded transition">Analyze Code</button>
                </div>
                <div id="analysis-results" class="bg-gray-700 rounded p-4">
                    <p class="text-gray-400">Analysis results will appear here...</p>
                </div>
            </div>
        </div>

        <!-- Features Grid -->
        <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-gray-800 rounded-lg p-6 text-center">
                <div class="text-4xl mb-4">🎨</div>
                <h3 class="text-xl font-bold mb-2">Beautiful UI</h3>
                <p class="text-gray-400">Modern, responsive interface with dark theme</p>
            </div>
            <div class="bg-gray-800 rounded-lg p-6 text-center">
                <div class="text-4xl mb-4">🔒</div>
                <h3 class="text-xl font-bold mb-2">Fully Offline</h3>
                <p class="text-gray-400">No internet required, complete privacy</p>
            </div>
            <div class="bg-gray-800 rounded-lg p-6 text-center">
                <div class="text-4xl mb-4">⚡</div>
                <h3 class="text-xl font-bold mb-2">Lightning Fast</h3>
                <p class="text-gray-400">Optimized for performance and speed</p>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
    <script>
        // Chat functionality
        const chatContainer = document.getElementById('chat-container');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');

        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;

            addMessageToChat('You', message, 'user');
            chatInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                addMessageToChat('AI', data.response, 'assistant');
            } catch (error) {
                addMessageToChat('System', 'Error: ' + error.message, 'error');
            }
        }

        function addMessageToChat(sender, message, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `mb-2 ${type === 'user' ? 'text-right' : 'text-left'}`;
            messageDiv.innerHTML = `
                <div class="inline-block max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    type === 'user' ? 'bg-blue-600' : 
                    type === 'error' ? 'bg-red-600' : 'bg-gray-600'
                }">
                    <strong>${sender}:</strong> ${message}
                </div>
            `;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Code generation
        const generateBtn = document.getElementById('generate-btn');
        const codePrompt = document.getElementById('code-prompt');
        const languageSelect = document.getElementById('language-select');
        const generatedCode = document.getElementById('generated-code');

        generateBtn.addEventListener('click', async () => {
            const prompt = codePrompt.value.trim();
            if (!prompt) return;

            generateBtn.textContent = 'Generating...';
            generateBtn.disabled = true;

            try {
                const response = await fetch('/api/code/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt,
                        language: languageSelect.value || null
                    })
                });

                const data = await response.json();
                generatedCode.innerHTML = `<pre><code class="language-${data.language || 'python'}">${data.code}</code></pre>`;
                Prism.highlightAll();
            } catch (error) {
                generatedCode.innerHTML = `<div class="text-red-400">Error: ${error.message}</div>`;
            } finally {
                generateBtn.textContent = 'Generate';
                generateBtn.disabled = false;
            }
        });

        // Code analysis
        const analyzeBtn = document.getElementById('analyze-btn');
        const analyzeCode = document.getElementById('analyze-code');
        const analysisResults = document.getElementById('analysis-results');

        analyzeBtn.addEventListener('click', async () => {
            const code = analyzeCode.value.trim();
            if (!code) return;

            analyzeBtn.textContent = 'Analyzing...';
            analyzeBtn.disabled = true;

            try {
                const response = await fetch('/api/code/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, language: 'python' })
                });

                const data = await response.json();
                analysisResults.innerHTML = `<pre class="text-sm">${JSON.stringify(data.analysis, null, 2)}</pre>`;
            } catch (error) {
                analysisResults.innerHTML = `<div class="text-red-400">Error: ${error.message}</div>`;
            } finally {
                analyzeBtn.textContent = 'Analyze Code';
                analyzeBtn.disabled = false;
            }
        });
    </script>
</body>
</html>"""
    
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    async with aiofiles.open("templates/index.html", "w") as f:
        await f.write(index_html)

async def get_index_html():
    """Get the main index.html content"""
    try:
        async with aiofiles.open("templates/index.html", "r") as f:
            return await f.read()
    except FileNotFoundError:
        await create_default_ui_files()
        async with aiofiles.open("templates/index.html", "r") as f:
            return await f.read() 