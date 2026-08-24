# Organizador de horarios

Aplicación web para registrar personas, importar y corregir sus horarios, comparar disponibilidad y proponer actividades recurrentes. Una propuesta aceptada se añade automáticamente al horario de todas las personas seleccionadas.

## Funciones incluidas

- Crear, editar y eliminar personas.
- Consultar el horario semanal individual.
- Crear, editar y eliminar bloques ocupados.
- Importar CSV, Excel (`.xlsx`), PDF con tablas e imágenes (`.png`, `.jpg`).
- Revisar y corregir las filas detectadas antes de guardarlas.
- Reemplazar un horario completo o añadir nuevos bloques.
- Elegir participantes, sesiones por semana, duración y asistencia mínima por sesión.
- Obtener hasta diez propuestas puntuadas, con minutos disponibles por persona.
- Aceptar una propuesta y añadir el evento a cada horario participante.

## Requisitos

- Python 3.11 o posterior.
- Node.js 20 o posterior.
- Para OCR automático de imágenes se recomienda [Tesseract OCR](https://github.com/tesseract-ocr/tesseract). Si no está instalado o el texto no se reconoce, la aplicación abre una fila editable para permitir completar el horario sin bloquear la importación.

## Ejecutar en desarrollo

Desde la raíz del proyecto, instala el backend:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --reload
```

La API quedará en `http://127.0.0.1:8000` y su documentación en `http://127.0.0.1:8000/docs`.

En otra terminal, inicia el frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. Vite redirige automáticamente las llamadas `/api` al backend. Para un backend remoto se puede definir `VITE_API_URL`.

## Formato recomendado para importación

Los CSV, Excel y PDF tabulares deben contener estas columnas (también se reconocen equivalentes en inglés):

| Actividad | Día | Inicio | Fin |
|---|---|---|---|
| Matemática | Lunes | 08:00 | 09:20 |
| Trabajo | Miércoles | 14:00 | 17:00 |

Para imágenes o PDF sin tabla, cada línea debe verse aproximadamente así:

```text
Lunes 08:00-09:20 Matemática
Miércoles 14:00-17:00 Trabajo
```

La vista previa permite arreglar cualquier reconocimiento antes de guardar.

## Verificación

```powershell
cd backend
..\venv\Scripts\python.exe -m unittest discover -s tests -v

cd ..\frontend
npm run lint
npm run build
```

La base SQLite se guarda siempre en `backend/scheduler.db`, independientemente del directorio desde el que se inicie Uvicorn.
