# ADR-001: FastAPI as the backend framework

**Status:** Accepted

## Context
The backend must orchestrate STT, RAG, LLM, safety and TTS, and later serve WebSockets.

## Options
FastAPI, Flask, Django.

## Decision
FastAPI with Pydantic.

## Reasoning
Async support, native Pydantic validation (important for structured LLM output),
auto-generated OpenAPI docs, strong ecosystem for ML services.

## Consequences
Python-only backend; requires an ASGI server (uvicorn).