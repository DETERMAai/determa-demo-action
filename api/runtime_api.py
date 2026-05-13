from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="DETERMA Runtime API")


class Proposal(BaseModel):
    proposal_id: str
    action: str


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "runtime": "determa",
    }


@app.post("/proposal")
def create_proposal(proposal: Proposal) -> dict:
    return {
        "status": "WAITING_APPROVAL",
        "proposal_id": proposal.proposal_id,
        "action": proposal.action,
    }


@app.post("/approve/{proposal_id}")
def approve(proposal_id: str) -> dict:
    return {
        "status": "CAPABILITY_GRANTED",
        "proposal_id": proposal_id,
    }


@app.post("/execute/{proposal_id}")
def execute(proposal_id: str) -> dict:
    return {
        "status": "EXECUTION_ALLOWED",
        "proposal_id": proposal_id,
    }


@app.get("/replay/{proposal_id}")
def replay(proposal_id: str) -> dict:
    return {
        "status": "REPLAY_VALIDATED",
        "proposal_id": proposal_id,
    }
