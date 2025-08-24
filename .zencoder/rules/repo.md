---
description: Repository Information Overview
alwaysApply: true
---

# CamboAI TraderStation Information

## Summary
CamboAI TraderStation is an advanced AI-powered trading intelligence platform that integrates multiple charting solutions, trading platforms, and AI-driven analysis tools. It provides real-time market data, pattern recognition, sentiment analysis, and strategy recommendations.

Note: The Streamlit dashboard is temporary; the final product will run at https://camboai.com (Vercel/Render behind Cloudflare).

## Structure
- **frontend/**: React TypeScript frontend with MUI components and chart libraries
- **backend/**: FastAPI Python backend for market data, analysis, and trading
- **dashboard/**: Streamlit dashboard for visualization
- **monitoring/**: Prometheus and Grafana for system monitoring
- **docs/**: Project documentation

## Language & Runtime
**Languages**: TypeScript (Frontend), Python (Backend, Dashboard)
**Versions**: Node.js 16+, Python 3.9
**Build Systems**: npm (Frontend), pip (Backend, Dashboard)
**Package Managers**: npm (Frontend), pip (Backend, Dashboard)

## Dependencies

### Frontend
**Main Dependencies**:
- React 18.2.0
- Material UI 5.13.0
- Highcharts 11.0.0
- Plotly.js 2.35.3
- Nivo visualization components
- Zustand 4.3.8 (State management)
- Axios 1.4.0 (HTTP client)

**Development Dependencies**:
- TypeScript 4.9.5
- React Scripts 5.0.1
- Tailwind CSS 3.3.2

### Backend
**Main Dependencies**:
- FastAPI 0.68.0
- SQLAlchemy 1.4.23
- Pandas 1.3.3
- NumPy 1.21.2
- TensorFlow 2.6.0
- Transformers 4.11.3
- Various trading APIs (yfinance, python-binance, alpaca-trade-api)

**Testing Dependencies**:
- Pytest 7.4.0
- Pytest-asyncio 0.21.1
- Pytest-cov 4.1.0

**Monitoring**:
- Prometheus client 0.17.1
- Loguru 0.7.0

## Build & Installation

### Frontend
```bash
cd frontend
npm install
npm start  # Development
npm run build  # Production
```

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker
**Docker Compose**: Orchestrates all services (frontend, backend, dashboard, database)
**Frontend Dockerfile**: Multi-stage build with Node.js 16 for build and Nginx for serving
**Backend Dockerfile**: Python 3.9 slim with required system dependencies
**Database**: PostgreSQL 13 Alpine

## Testing
**Backend Framework**: Pytest with asyncio support
**Test Location**: backend/tests/
**Run Command**:
```bash
cd backend
pytest --cov=app
```

**Frontend Testing**:
```bash
cd frontend
npm test
```

## CI/CD
**Workflow**: GitHub Actions for testing, building, and deployment
**Test Environment**: Ubuntu with PostgreSQL service container
**Build Process**: Docker images for backend and frontend
**Deployment**: Configured for main branch to production