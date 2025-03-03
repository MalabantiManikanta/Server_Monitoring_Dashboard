from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime

# Install dependencies
# pip install fastapi uvicorn sqlite3 pydantic

app = FastAPI()

# Connect to SQLite database
db = sqlite3.connect("monitoring.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        status TEXT,
        timestamp TEXT
    )
""")
db.commit()

class WriteRequest(BaseModel):
    data: str

@app.get("/read")
def read_api():
    try:
        cursor.execute("INSERT INTO requests (type, status, timestamp) VALUES (?, ?, ?)",
                       ("read", "success", datetime.utcnow().isoformat()))
        db.commit()
        return {"message": "Read API success"}
    except Exception as e:
        cursor.execute("INSERT INTO requests (type, status, timestamp) VALUES (?, ?, ?)",
                       ("read", "failure", datetime.utcnow().isoformat()))
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/write")
def write_api(request: WriteRequest):
    try:
        if request.data:
            cursor.execute("INSERT INTO requests (type, status, timestamp) VALUES (?, ?, ?)",
                           ("write", "success", datetime.utcnow().isoformat()))
            db.commit()
            return {"message": "Write API success"}
        else:
            raise ValueError("Invalid data")
    except Exception as e:
        cursor.execute("INSERT INTO requests (type, status, timestamp) VALUES (?, ?, ?)",
                       ("write", "failure", datetime.utcnow().isoformat()))
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary")
def get_summary():
    cursor.execute("SELECT status, COUNT(*) FROM requests GROUP BY status")
    summary = dict(cursor.fetchall())
    return {"total_requests": sum(summary.values()), "success": summary.get("success", 0), "failure": summary.get("failure", 0)}
