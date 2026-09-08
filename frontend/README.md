# Smart Study Room frontend

## Run the frontend

```powershell
npm install
npm run dev
```

The Vite app runs at `http://127.0.0.1:5173/` and uses the Django API at `http://127.0.0.1:8000/`.

## Run the backend

From the project root:

```powershell
cd backend
.venv\Scripts\python.exe manage.py runserver
```

The Django project, database, migrations, and requirements are all contained in `backend/`.

## Build

```powershell
npm run build
```