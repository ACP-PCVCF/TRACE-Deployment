from fastapi import FastAPI
import random
from cryptography.hazmat.primitives import serialization

from utils.models import TceSensorData, SensorRequest, Distance, SensorData
from utils.crypto_utils import load_private_key, sign_data, get_all_private_key_paths, generate_keys_if_missing
from utils.config import logger


# FastAPI App Init
app = FastAPI()

generate_keys_if_missing()

# POST Endpoint
@app.post("/api/v1/sensor-data", response_model=TceSensorData)
def post_sensor_data(req: SensorRequest):
    logger.info(f"Incoming request for shipment: {req.shipment_id}")
    logger.info(f"Process Instance Key: {req.camundaProcessInstanceKey} | Activity ID: {req.camundaActivityId} | tceId: {req.tceId}")

    # simulate sensor 
    key_paths = get_all_private_key_paths()
    private_key_path = random.choice(key_paths)
    private_key = load_private_key(private_key_path)
    public_key = private_key.public_key()

    # generate data
    distance_val = round(random.uniform(10.0, 500.0), 2)
    sensor_data = SensorData(distance=Distance(actual=distance_val))

    # sign data
    signature = sign_data(sensor_data.dict(), private_key)
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    logger.info("Sensor data signed successfully.")
    logger.info("Returning signed sensor data...")

    return TceSensorData(
        tceId=req.tceId,
        camundaProcessInstanceKey=req.camundaProcessInstanceKey,
        camundaActivityId=req.camundaActivityId,
        sensorkey=public_key_pem,  
        signedSensorData=signature,
        sensorData=sensor_data
    )