from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import pandas as pd
import os
from gtfs_loader import GTFSLoader

app = FastAPI(title="GTFS Visualizer API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.getenv("GTFS_DATA_DIR", "../gtfs_data")
loader = GTFSLoader(DATA_DIR)

@app.on_event("startup")
def load_data():
    try:
        loader.load()
        print("GTFS data loaded successfully.")
    except Exception as e:
        print(f"Error loading GTFS data: {e}")

@app.get("/stops")
def get_stops():
    return loader.get_stops()

@app.get("/routes")
def get_routes():
    return loader.get_routes()

@app.get("/trips/{route_id}")
def get_trips(route_id: str):
    trips = loader.get_trips(route_id)
    if not trips:
        raise HTTPException(status_code=404, detail="Route not found or no trips")
    return trips

@app.get("/trips/{trip_id}/stops")
def get_trip_stops(trip_id: str):
    return loader.get_stop_times_for_trip(trip_id)

@app.get("/timetable/{route_id}")
def get_timetable(route_id: str):
    return loader.get_timetable(route_id)
