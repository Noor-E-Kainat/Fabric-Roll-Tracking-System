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

        # 1. Update main fabric_rolls status
        update_query = f"""
            UPDATE fabric_rolls
            SET status = 'sent_to_tgms'
            WHERE id IN ({placeholders})
        """
        cursor.execute(update_query, selection.roll_ids)

        # 2. Insert selected rolls into TGMS table
        insert_query = """
            INSERT INTO tgms_rolls (fabric_roll_id, tgms_status)
            VALUES (%s, 'waiting_to_receive')
        """

        for roll_id in selection.roll_ids:
            cursor.execute(insert_query, (roll_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "success": True,
            "message": "Selected rolls sent to TGMS and added to TGMS waiting list"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
@app.get("/tgms/waiting-rolls")
def get_tgms_waiting_rolls():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                tgms_rolls.id AS tgms_id,
                fabric_rolls.id AS fabric_roll_id,
                fabric_rolls.roll_id,
                fabric_rolls.barcode,
                fabric_rolls.status AS tkms_status,
                tgms_rolls.tgms_status,
                tgms_rolls.sent_at
            FROM tgms_rolls
            JOIN fabric_rolls 
                ON tgms_rolls.fabric_roll_id = fabric_rolls.id
            WHERE tgms_rolls.tgms_status = 'waiting_to_receive'
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "success": True,
            "data": rows
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }