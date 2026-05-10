from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all frontend origins (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3308,
        user="root",
        password="",
        database="tkms_db",
        connection_timeout=5,
        autocommit=True
    )

class RollSelection(BaseModel):
    roll_ids: List[int]


@app.get("/tkms/fabric-rolls")
def get_fabric_rolls():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM fabric_rolls")
        rows = cursor.fetchall()

        conn.close()

        return {
            "success": True,
            "data": rows
        }

    except Exception as e:
        return {"error": str(e)}
    

@app.post("/tkms/send-to-tgms")
def send_to_tgms(selection: RollSelection):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        placeholders = ",".join(["%s"] * len(selection.roll_ids))

        query = f"""
            UPDATE fabric_rolls
            SET status = 'sent_to_tgms'
            WHERE id IN ({placeholders})
        """

        cursor.execute(query, selection.roll_ids)
        conn.commit()

        affected_rows = cursor.rowcount

        cursor.close()
        conn.close()

        return {
            "success": True,
            "message": "Selected rolls sent to TGMS",
            "updated_rows": affected_rows
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }