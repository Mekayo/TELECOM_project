import pandas as pd
import time
import os
from src.ingestion.telemetry_collector import NetworkDevice

# Config
devices_config = [
    {"id": "Router_1", "type": "router"},
    {"id": "Router_2", "type": "router"},
    {"id": "Switch_1", "type": "switch"},
    {"id": "Switch_2", "type": "switch"}
]


store_to_file = "D:\\TELECOM_project\\data\\raw\\telemetry_simulatory_dataset.csv"

# Initialize Simulator Devices
# (Solves Problem 1 - Single Device Illusion)
devices = [NetworkDevice(d["id"], d["type"]) for d in devices_config]
dataset = []

print("Starting Network Telemetry Simulation with Multiple Devices...")
print("To stop the data collection, press CTRL + C here!!!!")

try:
    while True:
        # Collect data from all simulated devices
        for device in devices:
            record = device.generate_telemetry()
            dataset.append(record)
            
        # Batch save every ~5 seconds for 4 devices (20 records)
        if len(dataset) >= 20:
            df = pd.DataFrame(dataset)
            file_exists = os.path.isfile(store_to_file)
            
            # Using mode 'a' prevents overwriting previous sessions
            df.to_csv(store_to_file, mode='a', header=not file_exists, index=False)
            dataset = []
            
        time.sleep(1) 

except KeyboardInterrupt:
    print("\nStopping data collection. Saving remaining data...")
    try:
        if dataset:
            df = pd.DataFrame(dataset)
            file_exists = os.path.isfile(store_to_file)
            df.to_csv(store_to_file, mode='a', header=not file_exists, index=False)
        print(f"Residual data successfully saved to {store_to_file}")
    except Exception as e:
        print(f"Error saving dataset: {e}")