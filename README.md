# Ticketera – Backend (FastAPI + SQLAlchemy + SQL Server)

Pequeña mesa de ayuda con tickets, técnicos, usuarios y comentarios.

## Stack
- Python 3.11+ (probado en Windows)
- FastAPI 0.112
- SQLAlchemy 2.x
- Uvicorn
- SQL Server (Driver ODBC 17)
- pyodbc

## Requisitos
- **ODBC Driver 17 for SQL Server** instalado.
- Python 3.11+
- Acceso a un SQL Server local (o remoto) con la BD `Ticketera` creada.

## Instalación
```powershell
# 1) Crear y activar venv
python -m venv .ticket
.ticket\Scripts\activate

# 2) Instalar dependencias
pip install -r requirements.txt
```

## Variables de entorno
Crea un archivo **.env** en la raíz (o usa `.env.example` como base):
```
DATABASE_URL=mssql+pyodbc://localhost,1433/Ticketera?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

> Si usas autenticación SQL (usuario/clave), el formato es:
> `mssql+pyodbc://USUARIO:CLAVE@localhost,1433/Ticketera?driver=ODBC+Driver+17+for+SQL+Server`

## Ejecutar el servidor
```powershell
uvicorn main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

## Endpoints principales
- `POST  /usuarios` – Crea usuario
- `PUT   /usuarios/{usuario_id}` – Actualiza usuario
- `GET   /usuarios/{usuario_id}` – Detalle usuario
- `DELETE /usuarios/{usuario_id}` – Elimina usuario

- `POST  /tecnicos` – Crea técnico
- `GET   /tecnicos/{tecnico_id}` – Detalle técnico
- `DELETE /tecnicos/{tecnico_id}` – Elimina técnico
- `GET   /tecnicos/{tecnico_id}/tickets` – Tickets por técnico

- `POST  /tickets/` – Crea ticket (Estado siempre `Nuevo`)
- `PUT   /tickets/` – Actualiza ticket (cambia estado, asigna técnico, etc.)
- `GET   /tickets` – Lista con filtros y paginación (`estado`, `tecnico_id`, `page`, `size`)
- `GET   /tickets/id/{ticket_id}` – Detalle ticket
- `DELETE /tickets/{ticket_id}` – Elimina ticket (borra comentarios)
- `GET   /tickets/estadisticas` – Conteos por estado

- `POST  /tickets/{ticket_id}/comentarios` – Agrega comentario
- `GET   /tickets/{ticket_id}/comentarios` – Lista comentarios

### Parámetros útiles en `GET /tickets`
- `estado` ∈ {"Nuevo","Abierto","En Progreso","Cerrado"}
- `tecnico_id` (int ≥ 1)
- `page` (int ≥ 1), `size` (1..100)
- Header de respuesta: **X-Total-Count** con el total de registros (sin paginar).

## Script de datos demo
Ejecuta este archivo en SQL Server para poblar datos iniciales:  
**sql_seed_demo.sql**

## Constraint y FK (recomendado)
Ejecuta este archivo para:
- Hacer único el correo de usuarios
- Asegurar `ON DELETE CASCADE` en comentarios  
**sql_constraints.sql**

## Troubleshooting
- **Swagger no carga /openapi.json**: revisa que no haya parámetros default raros (p. ej., `Response=None` en firmas de rutas). Reinicia `uvicorn`.
- **WatchFiles recarga por cambios en venv**: corre sin `--reload-dir` extra. Si molesta, usa `--reload-exclude .ticket/*` desde un `.bat`.
- **pyodbc falla al instalar**: verifica **ODBC Driver 17**. Si usas Python 3.13 y da problemas, considera Python 3.11/3.12.

## Licencia
Uso educativo/demostrativo.
