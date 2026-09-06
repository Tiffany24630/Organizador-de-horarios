# Organizador de horarios

Aplicación web y de escritorio para registrar personas, importar y corregir sus horarios, comparar disponibilidad y proponer actividades recurrentes. Una propuesta aceptada se añade automáticamente al horario de las personas seleccionadas.

## Funciones

- Crear, editar y eliminar personas.
- Consultar y modificar horarios semanales.
- Importar CSV, Excel (`.xlsx`), PDF e imágenes (`.png`, `.jpg`, `.jpeg`).
- Revisar las filas detectadas antes de guardarlas. Los PDF escaneados o imágenes que no puedan reconocerse abren una fila editable.
- Generar, comparar y aceptar propuestas de actividades grupales.
- Ejecutar la misma interfaz como web, contenedor Docker o aplicación Electron para Windows.

## Desarrollo local

Requisitos: Python 3.11 o posterior y Node.js 20 o posterior. Tesseract OCR es opcional; sin él, la aplicación permite completar manualmente los horarios de imágenes.

Backend:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --reload
```

Frontend, en otra terminal:

```powershell
cd frontend
npm ci
npm run dev
```

La web queda disponible en `http://localhost:5173`; Vite redirige `/api` a `http://127.0.0.1:8000`. También puede definirse `VITE_API_URL` para usar una API remota.

## Docker

Desde la raíz:

```powershell
docker compose up --build
```

Abre `http://localhost:8080`. La base SQLite se conserva en el volumen `scheduler-data`. Para detener los contenedores sin borrar los datos:

```powershell
docker compose down
```

## Aplicación de escritorio (Electron)

Instala las dependencias de ambos proyectos:

```powershell
.\venv\Scripts\python.exe -m pip install -r backend\requirements-desktop.txt
cd frontend
npm ci
```

Modo de desarrollo:

```powershell
npm run electron:dev
```

Crear un instalador de Windows en `frontend/release`:

```powershell
npm run desktop:dist
```

Electron inicia la API local automáticamente. En una instalación, los datos se guardan en la carpeta de datos de usuario de la aplicación y no dentro del instalador.

## Formato de importación

Los CSV (con coma, punto y coma, tabulador o `|`), Excel y PDF tabulares deben contener estas columnas; también se reconocen equivalentes en inglés:

| Actividad | Día | Inicio | Fin |
|---|---|---|---|
| Matemática | Lunes | 08:00 | 09:20 |
| Trabajo | Miércoles | 14:00 | 17:00 |

Para OCR de imágenes o PDF sin tabla, cada línea debe verse aproximadamente así:

```text
Lunes 08:00-09:20 Matemática
Miércoles 14:00-17:00 Trabajo
```

El tamaño máximo por archivo es 20 MB.

## Verificación

```powershell
cd backend
..\venv\Scripts\python.exe -m unittest discover -s tests -v

cd ..\frontend
npm run lint
npm run build

cd ..
docker compose config
```
