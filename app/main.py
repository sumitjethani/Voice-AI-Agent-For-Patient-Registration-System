from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .database import Base, engine
from .routes.patients import router as patients_router
from .routes.vapi import router as vapi_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("[STARTUP] Patient database initialized.", flush=True)
    yield


app = FastAPI(
    title="Voice AI Patient Registration API",
    version="1.0.0",
    description="REST API backing the Voice AI Patient Registration assessment.",
    lifespan=lifespan,
)

app.include_router(patients_router)
app.include_router(vapi_router)


@app.get("/health")
def health():
    return {"data": {"status": "ok"}, "error": None}


@app.get("/")
def root():
    return {
        "data": {
            "service": "Voice AI Patient Registration API",
            "docs": "/docs",
            "health": "/health",
            "demo": "/demo",
        },
        "error": None,
    }


@app.get("/demo", response_class=HTMLResponse)
def voice_demo():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Patient Registration AI Agent - Live Demo</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          margin: 0;
          background: #0f172a;
          color: #f8fafc;
        }
        .card {
          text-align: center;
          background: #1e293b;
          padding: 2.5rem;
          border-radius: 16px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.5);
          max-width: 480px;
          width: 90%;
          border: 1px solid #334155;
        }
        h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
        p { color: #94a3b8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem; }
        #call-btn {
          background: #10b981;
          color: white;
          border: none;
          padding: 14px 28px;
          font-size: 1.05rem;
          font-weight: 600;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          width: 100%;
        }
        #call-btn:hover { background: #059669; }
        #call-btn:disabled { background: #64748b; cursor: not-allowed; }
        #status {
          margin-top: 1rem;
          font-size: 0.85rem;
          color: #cbd5e1;
          font-family: monospace;
          word-break: break-word;
        }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🎙️ Voice Patient Registration</h1>
        <p>Click below to start a live voice intake session directly from your browser.</p>
        <button id="call-btn">Start Voice Call</button>
        <div id="status">Status: Initializing Voice SDK...</div>
      </div>

      <!-- Native ESM Module Import -->
      <script type="module">
        import Vapi from "https://esm.sh/@vapi-ai/web";

        const btn = document.getElementById("call-btn");
        const status = document.getElementById("status");
        let isCalling = false;

        try {
          const vapi = new Vapi("a0864276-0f81-4d1c-b2ff-60fa8f61d9de");
          status.innerText = "Status: Ready to call";

          vapi.on("call-start", () => {
            isCalling = true;
            btn.innerText = "End Call";
            btn.style.background = "#ef4444";
            status.innerText = "Status: 🟢 Connected! Speak into your microphone.";
          });

          vapi.on("call-end", () => {
            isCalling = false;
            btn.innerText = "Start Voice Call";
            btn.style.background = "#10b981";
            status.innerText = "Status: ⚪ Call Ended";
          });

          vapi.on("error", (err) => {
            console.error("Vapi Runtime Error:", err);
            status.innerText = "Status: ⚠️ Error: " + (err.message || JSON.stringify(err));
          });

          btn.onclick = async () => {
            if (!isCalling) {
              try {
                status.innerText = "Status: Requesting mic & connecting...";
                await vapi.start("d5900e36-a37c-43e9-b76b-896bbfaf9f75");
              } catch (e) {
                console.error("Call start exception:", e);
                status.innerText = "Status: ⚠️ Failed to connect: " + e.message;
              }
            } else {
              status.innerText = "Status: Disconnecting...";
              vapi.stop();
            }
          };
        } catch (initErr) {
          console.error("SDK Init Error:", initErr);
          status.innerText = "Status: ⚠️ Failed to initialize SDK: " + initErr.message;
        }
      </script>
    </body>
    </html>
    """