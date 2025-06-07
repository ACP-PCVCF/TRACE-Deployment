from pydantic import BaseModel
from typing import Optional

class Distance(BaseModel):
    actual: Optional[float] = None
    gcd: Optional[float] = None
    sfd: Optional[float] = None

class SensorData(BaseModel):
    distance: Distance

class TceSensorData(BaseModel):
    tceId: str
    camundaProcessInstanceKey: str
    camundaActivityId: str
    sensorkey: str
    signedSensorData: str
    sensorData: SensorData

class SensorRequest(BaseModel):
    shipment_id: str
    tceId: str
    camundaProcessInstanceKey: str
    camundaActivityId: str
