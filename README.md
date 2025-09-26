# 📌 Ticketera – Backend (FastAPI + SQLAlchemy + SQL Server)

Pequeña **mesa de ayuda** con gestión de **tickets, técnicos, usuarios y comentarios**.  
Incluye **pruebas automáticas con Postman/Newman** y **pruebas de carga con Locust**.  

---

## 🚀 Stack Tecnológico
- Python 3.11+ (probado en Windows)
- FastAPI 0.112
- SQLAlchemy 2.x
- Uvicorn
- SQL Server (Driver ODBC 17)
- pyodbc
- Postman + Newman (pruebas funcionales)
- Locust (pruebas de carga)

---

## ⚙️ Requisitos
- **ODBC Driver 17 for SQL Server** instalado.
- Python 3.11+  
- Acceso a un SQL Server local (o remoto) con la BD `Ticketera` creada.

---

## 🔑 Variables de entorno
Crear un archivo **.env** en la raíz:

```env
DATABASE_URL=mssql+pyodbc://localhost,1433/Ticketera?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

📚 Endpoints principales
👤 Usuarios

POST /usuarios – Crea usuario

PUT /usuarios/{usuario_id} – Actualiza usuario

GET /usuarios/{usuario_id} – Detalle usuario

DELETE /usuarios/{usuario_id} – Elimina usuario

👨‍🔧 Técnicos

POST /tecnicos – Crea técnico

GET /tecnicos/{tecnico_id} – Detalle técnico

DELETE /tecnicos/{tecnico_id} – Elimina técnico

GET /tecnicos/{tecnico_id}/tickets – Tickets por técnico

🎫 Tickets

POST /tickets/ – Crea ticket (Estado inicial: Nuevo)

PUT /tickets/ – Actualiza ticket (cambia estado, asigna técnico, etc.)

GET /tickets – Lista con filtros y paginación (estado, tecnico_id, page, size)

GET /tickets/id/{ticket_id} – Detalle ticket

DELETE /tickets/{ticket_id} – Elimina ticket (borra comentarios asociados)

GET /tickets/estadisticas – Conteos por estado

💬 Comentarios

POST /tickets/{ticket_id}/comentarios – Agrega comentario

GET /tickets/{ticket_id}/comentarios – Lista comentarios


📊 Pruebas con Postman & Newman
📂 Archivos incluidos

mesa_de_ayuda_API_v2.postman_collection.json

localhost.postman_environment.json


👉 Evidencias:

✅ Todos los tests pasaron sin errores (0 failed).

📄 Reporte generado: reporte.postman.html

👉 Evidencias:

📄 Reportes CSV en reports/

📊 Dashboard web con métricas:

RPS (requests per second)

Tiempo de respuesta (p50, p95)

Fallos (0% en pruebas exitosas)
