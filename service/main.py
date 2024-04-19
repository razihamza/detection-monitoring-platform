from typing import Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel
from joblib import load

import uvicorn
from fastapi import FastAPI
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge


# Prometheus Metrics
# ------------------
## Request counts
prediction_counter = Counter('num_prediction_requests', "Number of 'prediction' requests made")
model_information_counter = Counter('num_model_info_requests', "Number of 'model_information' requests made")
## Response Distributions
prediction_hist = Histogram('prediction_output_distribution', 'Distribution of prediction outputs')
prediction_score_hist = Histogram('prediction_score_distribution', 'Distribution of prediction scores')
prediction_latency_hist = Histogram('prediction_latency_distribution', 'Distribution of prediction response latency')

# Define Prometheus gauge metric for fire probability score
fire_probability_gauge = Gauge('fire_probability', 'Fire Probability Score')

#guages for sensor data
humidity_gauge = Gauge("humidity_percentage", "Humidity from DHT sensor")
temperature_gauge = Gauge("temperature_celsius", "Temperature from DHT sensor")
hydrogen_gauge = Gauge("hydrogen_concentration", "Hydrogen concentration")

app = FastAPI()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

model = load("anomaly-model.joblib")



class PredictionRequest(BaseModel):
    feature_vector: List[float] # input to model - [Temperature: float, Humidity: float, concentration: float]
    score: Optional[bool] = False


@app.post("/prediction")
def predict(req: PredictionRequest) -> Dict:
    '''
    Send a PredictionRequest in the following format: 
    
    {  
        "feature_vector": [0, 0, 0],  
        "score": false  
    }  
    
    and check whether the "feature_vector" is an inlier.

    Set "score" to true to get the anomaly score.
    '''
    
    start = datetime.now()
    
    # increment the count of 'prediction' requests made every time a request is made
    prediction_counter.inc()

    response = {}

    prediction = model.predict([req.feature_vector])
    response["is_inlier"] = int(prediction[0])

    # record prediction output in histogram
    prediction_hist.observe(response["is_inlier"])

    if req.score:
        score = model.score_samples([req.feature_vector])
        response["anomaly_score"] = score[0]

        # record prediction score in histogram
        prediction_score_hist.observe(response["anomaly_score"])
    
    latency = datetime.now() - start
    
    # record latency in histogram
    prediction_latency_hist.observe(latency.total_seconds())
    
    return response


@app.get("/model_information")
def model_information():
    '''
    Get the model's parameters
    '''
    # increment the count of 'model_information' requests made every time a request is made
    model_information_counter.inc()

    return model.get_params()


@app.post("/detection_score")
def receive_detection_score(data: Dict):
    '''
    Receive the detection score from detection.py and update the Prometheus gauge metric.
    '''
    score = data.get("score")
    if score is not None:
        # Set the value of the fire probability gauge metric
        fire_probability_gauge.set(score)
        return {"score": score, "message": "Detection score received successfully."}
    else:
        return {"error": "No score received."}
    
@app.post("/sensor_data")
def receive_sensor_data(data: Dict):
    '''
    Receive sensor data from fetchfirebase.py and update Prometheus gauge metrics.
    '''
    dht_data = data.get("DHT", {})
    hydrogen_data = data.get("Hydrogen", {})

    humidity = dht_data.get("humidity")
    temperature = dht_data.get("temperature")
    concentration = hydrogen_data.get("concentration")

    if humidity is not None:
        humidity_gauge.set(humidity)
    if temperature is not None:
        temperature_gauge.set(temperature)
    if concentration is not None:
        hydrogen_concentration_gauge.set(concentration)

    return {"message": "Sensor data received successfully."}
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
