import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.session import init_db
from backend.database.seed import seed_database
from backend.iot.serial_manager import serial_manager
from backend.iot.simulator import simulator
from backend.iot.command_manager import command_manager
from backend.iot.device_manager import device_manager
from backend.api.websocket import ws_manager, router as ws_router
from backend.api import (
    fields, sensors, irrigation, ai, weather, alerts, history, analytics, reports, settings as settings_api, debug
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agrivision.main")

# Setup WebSocket Broadcast Listener Callback
def handle_system_broadcast(msg: dict):
    # Loop over asyncio event loop to broadcast via WebSockets
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(ws_manager.broadcast(msg))
    except RuntimeError:
        pass

serial_manager.set_broadcast_callback(handle_system_broadcast)
simulator.set_broadcast_callback(handle_system_broadcast)

async def background_scheduler():
    """
    Background loop for simulation step generation, command timeout checks, and device health monitoring.
    """
    logger.info("AgriVision Background Scheduler started.")
    while True:
        try:
            # 1. Periodic Simulation Step if DEMO_MODE
            if settings.DEMO_MODE:
                packet = simulator.step()
                
            # 2. Check Command ACKs & Timeouts
            command_manager.check_timeouts()
            
            # 3. Check Device Health & Stale telemetry
            dev_health = device_manager.check_device_health()
            
        except Exception as e:
            logger.error(f"Error in background scheduler: {e}")
            
        await asyncio.sleep(3.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AgriVision Platform...")
    # Initialize Database & Seed initial dataset
    init_db()
    seed_database()
    
    # Attempt Serial Connection (Hardware Mode)
    serial_manager.connect()
    serial_manager.start_listening()
    
    # Start Background Task Scheduler
    scheduler_task = asyncio.create_task(background_scheduler())
    
    yield
    
    logger.info("Shutting down AgriVision Platform...")
    scheduler_task.cancel()
    serial_manager.stop_listening()

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AgTech SaaS & Real IoT Control Room Platform for Precision Agriculture",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ws_router)
app.include_router(fields.router)
app.include_router(sensors.router)
app.include_router(irrigation.router)
app.include_router(ai.router)
app.include_router(weather.router)
app.include_router(alerts.router)
app.include_router(history.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(settings_api.router)
app.include_router(debug.router)

@app.get("/")
def root():
    return {
        "system": settings.APP_NAME,
        "status": "OPERATIONAL",
        "demo_mode": settings.DEMO_MODE,
        "serial_port": settings.SERIAL_PORT,
        "serial_connected": serial_manager.is_connected,
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
