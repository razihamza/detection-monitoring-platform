# Detection and Monitoring System for Industrial Environment using AI & IoT

## Overview

This project presents an integrated platform that leverages Artificial Intelligence (AI) and Internet of Things (IoT) technologies to monitor and detect anomalies in industrial environments. By combining sensor data acquisition, real-time processing, and machine learning models, the system aims to enhance safety and operational efficiency in industrial settings.

## Features

- **Sensor Data Acquisition**: Collects environmental data such as temperature and humidity using DHT sensors.
- **Real-time Monitoring**: Utilizes Firebase for real-time data visualization and storage.
- **Anomaly Detection**: Implements machine learning models to identify deviations from normal operational parameters.
- **Modular Architecture**: Organized into distinct modules for detection, monitoring, and service management.
- **Dockerized Services**: Employs Docker for containerization, ensuring consistent deployment across environments.

## Project Structure

```
detection-monitoring-platform/
├── detection/           # Contains scripts for anomaly detection
├── dht_firebase1/       # Handles sensor data acquisition and Firebase integration
├── jupyter/             # Jupyter notebooks for data analysis and model training
├── monitoring/          # Modules for monitoring and visualization
├── service/             # Backend services and APIs
├── tester/              # Testing scripts and utilities
├── Makefile             # Automation scripts for building and managing services
├── requirements.txt     # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Firebase account for real-time database integration

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/razihamza/detection-monitoring-platform.git
   cd detection-monitoring-platform
   ```

2. **Set Up Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   - Set up your Firebase credentials and other necessary environment variables as required by the modules.

5. **Build and Run Services**

   Utilize the provided `Makefile` to build and manage services:

   ```bash
   make run-all
   ```

   This command will build and start all services including the Jupyter notebooks, APIs, and monitoring tools.

## Usage

- **Data Acquisition**: The `dht_firebase1` module reads data from DHT sensors and pushes it to Firebase.
- **Anomaly Detection**: The `detection` module processes incoming data to detect anomalies using trained ML models.
- **Monitoring**: The `monitoring` module visualizes data and alerts users of any detected anomalies.
- **API Services**: The `service` module provides RESTful APIs for external integrations.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

