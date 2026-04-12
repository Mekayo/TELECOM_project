import random
from datetime import datetime

class NetworkDevice:
    def __init__(self, device_id, device_type):
        """
        Initialize a stateful network device simulation.
        Heterogeneous baselines based on device type (Problem 2).
        """
        self.device_id = device_id
        self.device_type = device_type
        
        # Baselines based on type
        if self.device_type == "router":
            self.base_latency = 20.0  # higher processing delay
            self.base_bandwidth = 100.0 # higher capacity
        else: # switch
            self.base_latency = 5.0   # fast switching
            self.base_bandwidth = 50.0
            
        # Internal state for smooth random walk transitions
        self.current_cpu = random.uniform(20, 40)
        self.current_memory = random.uniform(30, 60)
        
    def get_time_multiplier(self, dt):
        """
        Time-awareness: Peak hours have higher load than night
        (Problem 3)
        """
        # Peak hours: 9 AM to 6 PM (18:00)
        if 9 <= dt.hour < 18:
            return 1.5 # 50% more base load
        else:
            return 0.8 # 20% less base load
   
    #generating random data for each devices
    def generate_telemetry(self):
        dt = datetime.now()
        time_mult = self.get_time_multiplier(dt)
        
        # Update state via random walk
        self.current_cpu = max(0.0, min(100.0, self.current_cpu + random.uniform(-5, 5)))
        self.current_memory = max(0.0, min(100.0, self.current_memory + random.uniform(-2, 2)))
        
        # Calculate metrics with time-aware multipliers
        cpu = min(100.0, self.current_cpu * time_mult)
        memory = min(100.0, self.current_memory * time_mult)
        latency = max(1.0, random.gauss(self.base_latency * time_mult, 2.0))
        bandwidth_out = max(0.0, random.gauss(self.base_bandwidth * time_mult, 10.0))
        bandwidth_in = max(0.0, random.gauss(self.base_bandwidth * time_mult, 10.0))
        
        # Baselines for errors
        packet_loss = max(random.gauss(0.1, 0.05), 0.0)
        crc_errors = random.randint(0, 1) if random.random() < 0.1 else 0
        
        # Fault Injection (Problem 4)
        # 1% chance a severe anomaly occurs during this collection tick
        if random.random() < 0.01:
            anomaly_type = random.choice(['cpu_spike', 'network_drop', 'memory_leak'])
            if anomaly_type == 'cpu_spike':
                cpu = random.uniform(90.0, 100.0)
            elif anomaly_type == 'network_drop':
                packet_loss = random.uniform(5.0, 20.0)
                latency = random.uniform(100.0, 500.0)
                bandwidth_out = random.uniform(0.0, 5.0)
                bandwidth_in = random.uniform(0.0, 5.0)
            elif anomaly_type == 'memory_leak':
                memory = random.uniform(85.0, 99.0)
                # Ensure the leak sticks around longer
                self.current_memory = memory 
        
        return {
            "timestamp": dt,
            "device_id": self.device_id,
            "device_type": self.device_type,
            "cpu_percent": round(cpu, 2),
            "memory_percent": round(memory, 2),
            "latency": round(latency, 2),
            "bandwidth_out": round(bandwidth_out, 2),
            "bandwidth_in": round(bandwidth_in, 2),
            "packet_loss": round(packet_loss, 2),
            "crc_errors": crc_errors
        }
