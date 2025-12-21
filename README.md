# Forex Monitor - USD/EUR

Monitor de tipo de cambio USD/EUR con predicciones y alertas.

## Inicio Rapido (Windows)

### Opcion 1: Script automatico
```bash
# Ejecutar el script de inicio
start-dev.bat
```

### Opcion 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### URLs
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs

## Estructura del Proyecto

```
forex-monitor/
├── backend/                 # Python FastAPI
│   ├── app/
│   │   ├── api/routes/     # Endpoints REST
│   │   ├── models/         # SQLAlchemy + Pydantic
│   │   ├── services/       # Logica de negocio
│   │   └── main.py         # Entry point
│   └── requirements.txt
├── frontend/               # Next.js + React
│   ├── src/
│   │   ├── app/           # Pages (App Router)
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities
│   └── package.json
└── data/                   # SQLite database
```

## APIs Utilizadas (Gratuitas)

| API | Uso | Limite |
|-----|-----|--------|
| Frankfurter | Tipo de cambio (BCE) | Ilimitado |
| ExchangeRate-API | Backup | 1500/mes |

## Proximas Fases

- [ ] Fase 2: Noticias + Analisis de sentimiento
- [ ] Fase 3: Predicciones con ML (Prophet)
- [ ] Fase 4: Alertas + PWA completo
- [ ] Fase 5: Refinamiento y optimizacion

## Requisitos

- Python 3.10+
- Node.js 18+
- npm o yarn
