"""
FastAPI entry point for the Autonomous Life Orchestration Agent.
"""

from fastapi import FastAPI

app = FastAPI(title="Autonomous Life Orchestration Agent")

@app.get("/")
def health_check():
    return {"status": "agent alive"}
