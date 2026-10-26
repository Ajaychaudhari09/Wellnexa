@echo off
title WellNexa AI Launcher
echo ==================================================
echo         WellNexa AI - Starting System
echo ==================================================

echo.
echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "WellNexa Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo [2/3] Starting WellNexa Web App (Vite) on http://localhost:5173 ...
start "WellNexa Web App" cmd /k "cd apps\web && npm run dev"

echo.
echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "WellNexa Next.js" cmd /k "cd frontend && npm run dev"

echo.
echo ==================================================
echo All services launched!
echo - Web App:      http://localhost:5173
echo - Next.js:      http://localhost:3000
echo - Swagger Docs: http://127.0.0.1:8000/docs
echo ==================================================
pause
