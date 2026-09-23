import json
import sys
from datetime import datetime
from pathlib import Path

import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    from .database.connection import SessionLocal, engine
    from .models import AuditLog, Base, Incident
    from .routes import auth, incidents, logs
except ImportError:
    from backend.database.connection import SessionLocal, engine
    from backend.models import AuditLog, Base, Incident
    from backend.routes import auth, incidents, logs

# Initialize Database tables
Base.metadata.create_all(bind=engine)

# Create Socket.IO Async Server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(title="NMDC Control Room Engine")


@app.get("/")
async def root():
    return {"status": "ok", "service": "NMDC Safety Control Room"}


# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(logs.router)

# Mount SocketIO App
socket_app = socketio.ASGIApp(sio, app)

# Global Buzzer State
buzzer_state = "MUTED"


@sio.event
async def connect(sid, environ):
    print(f"⚡ [SOCKET.IO] Client Connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"❌ [SOCKET.IO] Client Disconnected: {sid}")


@sio.event
async def telemetry_data(sid, data):
    global buzzer_state
    dist = data.get("distance", 100.0)

    # Threshold rules trigger alerts into database
    if dist < 5.0 and buzzer_state != "MUTED":
        buzzer_state = "ACTIVE"
        db = SessionLocal()
        inc = Incident(
            incident_code=f"INC-{int(datetime.utcnow().timestamp())}",
            node_id=data.get("node_id", "LORA_NODE_01"),
            severity="CRITICAL",
            description=f"Proximity violation! Obstacle detected at {dist}cm.",
            status="OPEN",
        )
        db.add(inc)
        db.commit()
        db.close()

    data["buzzer_state"] = buzzer_state
    # Broadcast to all connected web dashboards
    await sio.emit("telemetry_update", data)


@sio.event
async def hardware_command(sid, data):
    global buzzer_state
    cmd = data.get("command")
    user = data.get("operator", "OP-BAILADILA-01")

    if cmd == "MUTE_PIEZO":
        buzzer_state = "MUTED"
    elif cmd == "FORCE_PIEZO_ON":
        buzzer_state = "ACTIVE"

    # Log action to audit database
    db = SessionLocal()
    audit = AuditLog(
        user_id=user,
        action=cmd,
        module="HARDWARE_REMOTE_CONTROL",
        payload=json.dumps(data),
    )
    db.add(audit)
    db.commit()
    db.close()

    # Echo confirmation
    await sio.emit(
        "command_executed",
        {
            "status": "SUCCESS",
            "command": cmd,
            "buzzer_state": buzzer_state,
        },
    )


if __name__ == "__main__":
    # Insert mock seed data if empty
    db = SessionLocal()
    if db.query(Incident).count() == 0:
        db.add(
            Incident(
                incident_code="INC-8831",
                node_id="LORA_NODE_01",
                severity="WARNING",
                description="Sensor proximity distance < 15cm threshold detected.",
                status="OPEN",
            )
        )
        db.add(
            AuditLog(
                user_id="SYSTEM",
                action="BOOTSTRAP",
                module="CORE",
                payload="System initialized.",
            )
        )
        db.commit()
    db.close()

    uvicorn.run(socket_app, host="127.0.0.1", port=8000)