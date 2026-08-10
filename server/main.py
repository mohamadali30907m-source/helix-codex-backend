from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Helix Codex Backend",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



RobotMode = Literal["idle", "running", "error", "emergency_stop"]


class RobotStatus(BaseModel):
    online: bool
    mode: RobotMode
    emergency_stop: bool
    battery: float
    temperature: float
    timestamp: str



robot = RobotStatus(
    online=True,
    mode="idle",
    emergency_stop=False,
    battery=100.0,
    temperature=25.0,
    timestamp=datetime.now(timezone.utc).isoformat(),
)



@app.get("/")
async def root():
    return {
        "status": "online",
        "project": "Helix Codex Backend",
        "version": "0.2.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }




@app.get("/api/robot/status", response_model=RobotStatus)
async def get_robot_status():
    robot.timestamp = datetime.now(timezone.utc).isoformat()

    return robot


@app.post("/api/robot/emergency-stop", response_model=RobotStatus)
async def emergency_stop():
    robot.emergency_stop = True
    robot.mode = "emergency_stop"
    robot.timestamp = datetime.now(timezone.utc).isoformat()

    return robot


@app.post("/api/robot/reset", response_model=RobotStatus)
async def reset_robot():
    robot.emergency_stop = False
    robot.mode = "idle"
    robot.timestamp = datetime.now(timezone.utc).isoformat()

    return robot

class RobotCommand(BaseModel):
    command: Literal["start", "stop"]


@app.post("/api/robot/command", response_model=RobotStatus)
async def robot_command(payload: RobotCommand):
    if robot.emergency_stop:
        return robot

    if payload.command == "start":
        robot.mode = "running"

    elif payload.command == "stop":
        robot.mode = "idle"

    robot.timestamp = datetime.now(timezone.utc).isoformat()

    return robot
