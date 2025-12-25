import random
import time
import threading
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.equipment import Equipment

def simulate_iot_telemetry():
    """
    Background task to simulate IoT data.
    Updates equipment telemetry in the database.
    """
    while True:
        try:
            db: Session = SessionLocal()
            equipment_list = db.query(Equipment).all()
            
            for eq in equipment_list:
                # Simulate data based on status
                if eq.status == "operational":
                    # Normal operating range
                    eq.temperature = round(random.uniform(40.0, 65.0), 1)
                    eq.vibration = round(random.uniform(0.1, 2.5), 2)
                elif eq.status == "broken":
                    # Overheating / High vibration
                    eq.temperature = round(random.uniform(80.0, 110.0), 1)
                    eq.vibration = round(random.uniform(5.0, 15.0), 2)
                else: # maintenance
                    # Maintenance - Sensors Disabled
                    eq.temperature = 0.0
                    eq.vibration = 0.0
                
                eq.last_telemetry_update = datetime.now()
            
            db.commit()
            db.close()
        except Exception as e:
            print(f"[IoT Simulator] Error: {e}")
            
        time.sleep(5)  # Update every 5 seconds

def start_iot_simulation():
    thread = threading.Thread(target=simulate_iot_telemetry, daemon=True)
    thread.start()
