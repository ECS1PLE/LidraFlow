## Быстрый запуск

```bash
cp config/secrets.example.env config/secrets.env
cp frontend/.env.example frontend/.env.local
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Открыть:

```text
http://127.0.0.1:3000
```
