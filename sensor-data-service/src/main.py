from fastapi import FastAPI
import random

from models import TceSensorData, SensorRequest, Distance, SensorData
from crypto_utils import load_private_key, sign_data
from config import logger, SENSOR_IDS

# FastAPI App Init
app = FastAPI()

# POST Endpoint
@app.post("/api/v1/sensor-data", response_model=TceSensorData)
def post_sensor_data(req: SensorRequest):
    logger.info(f"Incoming request for shipment: {req.shipment_id}")
    logger.info(f"Process Instance Key: {req.camundaProcessInstanceKey} | Activity ID: {req.camundaActivityId} | tceId: {req.tceId}")

    sensor_id = random.choice(SENSOR_IDS)
    logger.info(f"Selected sensor: {sensor_id}")

    distance_val = round(random.uniform(10.0, 500.0), 2)
    logger.info(f"Generated distance: {distance_val} km")

    sensor_data = SensorData(distance=Distance(actual=distance_val))

    private_key = load_private_key(sensor_id)
    signature = sign_data(sensor_data.dict(), private_key)

    logger.info("Sensor data signed successfully.")
    logger.info("Returning signed sensor data...")

    return TceSensorData(
        tceId=req.tceId,
        camundaProcessInstanceKey=req.camundaProcessInstanceKey,
        camundaActivityId=req.camundaActivityId,
        sensorkey=sensor_id,
        signedSensorData=signature,
        sensorData=sensor_data
    )
