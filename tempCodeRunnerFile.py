import psutil  # type: ignore
import pandas as pd  # type: ignore
import random
import time
from datetime import datetime

# config
device_id="Router 1"
store_to_file="D:\\TELECOM_project\\data\\telemetry_simulatory_dataset.csv"

timestamp = datetime.now()

prev_bytes_sent=psutil.net_io_counters().bytes_sent
prev_bytes_recv=psutil.net_io_counters().bytes_recv
dataset=[]

print("To stop the data collection, press CTRL + C ,here!!!!")   
try:
    while True:
        # real time data from my machine
        cpu=psutil.cpu_percent(None)
        memory=psutil.virtual_memory().percent
        
        # bandwidth calculation
        current_bytes_sent=psutil.net_io_counters().bytes_sent
        current_bytes_recv=psutil.net_io_counters().bytes_recv  
        bandwidth_out=(current_bytes_sent-prev_bytes_sent)/1e6/1  # MB/s
        bandwidth_in=(current_bytes_recv-prev_bytes_recv)/1e6/1  # MB/s
        prev_bytes_sent=current_bytes_sent
        prev_bytes_recv=current_bytes_recv
        
        record={
            "timestamp":timestamp,
            "device_id":device_id,
            "cpu_percent":cpu,
            "memory_percent":memory,
            "latency":random.gauss(25,5),
            "bandwidth_out":bandwidth_out,
            "bandwidth_in":bandwidth_in,
            "packet_loss":max(random.gauss(0.3,0.1),0.0),
            "crc_errors":random.randint(0,2)
            }
        
        dataset.append(record)
        if len(dataset)>=2000:
            with open(store_to_file, 'a') as f:
                pd.DataFrame(dataset).to_csv(f, header=f.tell()==0, index=False)
            dataset=[]
        
        time.sleep(1)
        
except KeyboardInterrupt:
    try:
        pd.DataFrame(dataset).to_csv(store_to_file,index=False)
    except Exception as e:
        print(f"Error saving dataset: {e}")