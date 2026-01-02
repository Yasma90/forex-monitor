# Guia de Contribucion

Gracias por tu interes en contribuir a Forex Monitor. Esta guia te ayudara a comenzar.

## Codigo de Conducta

Este proyecto sigue un codigo de conducta de respeto mutuo. Se espera que todos los contribuidores:
- Sean respetuosos y constructivos
- Acepten criticas constructivas
- Se enfoquen en lo mejor para la comunidad

## Como Contribuir

### Reportar Bugs

1. Verifica que el bug no haya sido reportado previamente en [Issues](../../issues)
2. Crea un nuevo issue con:
   - Descripcion clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica
   - Entorno (OS, version Python/Node, navegador)

### Sugerir Features

1. Revisa el README para ver features planeados
2. Abre un issue con etiqueta `enhancement`
3. Describe el caso de uso y beneficio

### Pull Requests

1. Fork el repositorio
2. Crea una rama desde `main`:
   ```bash
   git checkout -b feature/mi-feature
   ```
3. Realiza tus cambios siguiendo las guias de estilo
4. Asegurate de que los tests pasen:
   ```bash
   cd backend && pytest tests/ -v
   ```
5. Commit con mensajes descriptivos:
   ```bash
   git commit -m "feat: agregar soporte para EUR/GBP"
   ```
6. Push y crea el Pull Request

## Estructura del Proyecto

```
forex-monitor/
├── backend/           # API Python FastAPI
│   ├── app/
│   │   ├── api/       # Endpoints REST
│   │   ├── models/    # Modelos SQLAlchemy
│   │   ├── services/  # Logica de negocio
│   │   └── jobs/      # Tareas programadas
│   └── tests/         # Tests unitarios
├── frontend/          # UI Next.js React
│   ├── src/
│   │   ├── app/       # Paginas
│   │   ├── components/# Componentes React
│   │   └── lib/       # Utilidades
│   └── public/        # Assets estaticos
└── docs/              # Documentacion
```

## Guias de Estilo

### Python (Backend)

- Seguir PEP 8
- Type hints en funciones publicas
- Docstrings en clases y funciones principales
- Nombres descriptivos en snake_case

```python
async def get_exchange_rate(
    base: str = "USD",
    target: str = "EUR"
) -> ExchangeRate:
    """
    Obtiene la tasa de cambio actual.

    Args:
        base: Moneda base (default USD)
        target: Moneda objetivo (default EUR)

    Returns:
        ExchangeRate con la tasa actual
    """
    ...
```

### TypeScript (Frontend)

- Usar TypeScript estricto
- Interfaces para props de componentes
- Nombres en camelCase para variables, PascalCase para componentes

```typescript
interface ExchangeCardProps {
  rate: ExchangeRate;
  onRefresh?: () => void;
}

export function ExchangeCard({ rate, onRefresh }: ExchangeCardProps) {
  ...
}
```

### Commits

Seguir Conventional Commits:
- `feat:` Nueva funcionalidad
- `fix:` Correccion de bug
- `docs:` Documentacion
- `style:` Formato (no afecta logica)
- `refactor:` Refactorizacion
- `test:` Tests
- `chore:` Mantenimiento

## Desarrollo Local

### Requisitos
- Python 3.10+
- Node.js 18+
- npm o yarn

### Setup

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/forex-monitor.git
cd forex-monitor

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Ejecutar en desarrollo

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app --cov-report=html
```

## Areas de Contribucion

### Alta Prioridad
- [ ] Autenticacion de usuarios (JWT)
- [ ] Soporte multi-divisa
- [ ] Tests de integracion

### Media Prioridad
- [ ] Modo oscuro
- [ ] Exportar datos CSV
- [ ] Calendario economico

### Documentacion
- [ ] Traducir a ingles
- [ ] Agregar ejemplos de API
- [ ] Video tutorial

## Preguntas

Si tienes preguntas, abre un issue con etiqueta `question` o contacta a los maintainers.

---

Gracias por contribuir!
