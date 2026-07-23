# TECH_STACK.md

# CHITTI Technology Stack

Version: 2.0

---

# Philosophy

Technology choices must support the following principles:

- Modular Architecture
- Hardware Independence
- Cross Platform
- Offline First
- Scalable
- Testable
- Production Ready
- Long-term Maintainability

No technology should lock the project into a single vendor.

---

# High-Level Architecture

```
Desktop Application
        │
        ▼
Business Logic
        │
        ▼
AI Layer
        │
        ▼
Hardware API
        │
        ▼
ESP32 Firmware
        │
        ▼
Electronics
```

---

# Desktop Application

## Language

Python 3.13+

Reason

- Excellent AI ecosystem
- Fast development
- Huge community
- Cross-platform
- Mature libraries

---

## GUI Framework

PySide6 (Qt6)

Reasons

- Native desktop performance
- Windows
- Linux
- macOS
- GPU accelerated
- Excellent animation support
- Long-term support

Avoid

Tkinter

Kivy

Electron (unless future web edition)

---

# AI Layer

Provider-independent architecture.

Supported providers

- OpenAI
- Google Gemini
- Anthropic Claude
- Ollama
- LM Studio
- Future Local LLMs

Never hardcode a provider.

Use Provider Interfaces.

---

# AI SDKs

OpenAI SDK

Google GenAI SDK

Anthropic SDK

Ollama API

OpenRouter API

Each provider must implement the same interface.

---

# Voice

## Speech To Text

Primary

Faster Whisper

Alternative

Whisper.cpp

Cloud

Gemini Live

OpenAI Speech

---

## Text To Speech

Primary

Microsoft Edge TTS

Alternatives

Piper

ElevenLabs

OpenAI TTS

System TTS

Should be configurable.

---

## Wake Word

OpenWakeWord

Future

Porcupine

---

## Voice Activity Detection

Silero VAD

---

# Vision

OpenCV

MediaPipe

YOLO

ONNX Runtime

Tesseract OCR

EasyOCR

---

Capabilities

Camera

Face Detection

Object Detection

Gesture Recognition

OCR

Tracking

---

# Animation

Qt Animation Framework

Lottie

SVG Animation

JSON Animation

Future

Spine2D

Rive

---

# Avatar Rendering

Qt Graphics View

Qt Quick

QML

OpenGL (optional)

Future

GPU rendering

---

# Memory System

SQLite

FAISS

JSON

Pickle (temporary cache only)

Future

PostgreSQL

Qdrant

ChromaDB

---

Memory Types

Conversation

Semantic

Episodic

Preferences

Knowledge

Relationships

Context

---

# Database

SQLite

Reason

Simple

Reliable

Cross Platform

Zero Configuration

---

# Vector Database

FAISS

Future

Chroma

Qdrant

Milvus

---

# Configuration

YAML

JSON

Environment Variables

Never hardcode secrets.

---

# Networking

HTTPX

WebSockets

gRPC (future)

REST APIs

---

# Plugin System

Python Entry Points

Dynamic Module Loading

Sandbox Support (future)

Plugins should never modify the core.

---

# Desktop Automation

PyAutoGUI

Pynput

psutil

pywin32 (Windows)

Cross-platform abstraction required.

---

# Scheduler

APScheduler

Cron-style scheduling

Persistent jobs

---

# Logging

Python Logging

Rich

Loguru

Structured logs

Log rotation

Crash logs

---

# Dependency Injection

Dependency Injector

or

Manual Constructor Injection

Avoid global state.

---

# Testing

pytest

pytest-qt

pytest-cov

unittest

Mock

---

Testing Requirements

Unit Tests

Integration Tests

UI Tests

Hardware Tests

Regression Tests

Performance Tests

---

# Code Quality

Black

Ruff

isort

mypy

pre-commit

---

# Documentation

Markdown

MkDocs

Mermaid

PlantUML

Automatic API documentation.

---

# Build System

Poetry

or

uv (Preferred)

Future

PyInstaller

Nuitka

---

# Packaging

Windows

MSIX

EXE Installer

Linux

AppImage

deb

Flatpak

macOS

DMG

---

# Firmware

Language

C++

Framework

ESP-IDF

FreeRTOS

Arduino Component (only where necessary)

---

# Firmware Libraries

ESP-IDF

LVGL (optional)

TinyUSB

ArduinoJson

LittleFS

ESP-NOW (future)

---

# Communication

USB Serial

UART

BLE

Wi-Fi

JSON Protocol

Future

Protocol Buffers

---

# Hardware

Primary MCU

ESP32-S3

Future

ESP32-P4

RP2350

Raspberry Pi Compute Module

---

# PCB Design

KiCad

Version Controlled

Libraries

SnapEDA

Ultra Librarian

---

# Mechanical Design

Fusion 360

STEP

STL

3MF

---

# Version Control

Git

GitHub

GitHub Projects

GitHub Actions

Feature Branch Workflow

---

# CI/CD

GitHub Actions

Automated

Formatting

Linting

Testing

Packaging

Release

---

# Security

Secrets

Environment Variables

GitHub Secrets

Never commit API keys.

---

# Cloud

Optional

Supabase

Firebase

Custom Backend

OTA

Authentication

Cloud Memory Sync

---

# Repository Standards

One Responsibility Per Module

Loose Coupling

High Cohesion

Dependency Inversion

Interface Driven Design

Composition Over Inheritance

No Circular Dependencies

---

# Folder Naming

snake_case

Example

conversation_engine

emotion_engine

hardware_manager

plugin_sdk

Avoid spaces.

---

# Naming Convention

Classes

PascalCase

Functions

snake_case

Variables

snake_case

Constants

UPPER_CASE

Files

snake_case.py

---

# Code Style

PEP8

Type Hints Required

Docstrings Required

Public APIs Documented

No Magic Numbers

No Hardcoded Paths

---

# Branch Strategy

main

Stable Releases

develop

Integration Branch

feature/*

New Features

bugfix/*

Bug Fixes

hotfix/*

Critical Production Fixes

---

# Commit Format

feat:

fix:

docs:

refactor:

test:

perf:

build:

ci:

chore:

---

# Definition of Done

Every feature must include

✓ Working Implementation

✓ Unit Tests

✓ Documentation

✓ Error Handling

✓ Logging

✓ Configuration

✓ Code Review

✓ Integration Test

✓ No Compiler Warnings

✓ No Linter Errors

---

# Future Technologies

Rust Modules

ONNX Runtime

CUDA Acceleration

TensorRT

ROS2 Bridge

Docker

Kubernetes

Web Companion

Mobile Companion

Wearables

Smart Home Integration

These are optional extensions and must not affect the core architecture.

---

# Final Principle

The desktop application is the permanent brain.

Firmware is an execution layer.

Hardware is replaceable.

AI providers are replaceable.

Plugins are extensible.

Every engineering decision should preserve these principles.