import random
import time
from datetime import datetime


def generate_sample_telemetry():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "vehicle_id": f"TRUCK-{random.randint(1, 9)}",
        "speed_kmh": random.uniform(10, 35),
        "temperature_c": random.uniform(45, 95),
        "vibration": random.uniform(0.5, 2.5),
        "dust_level": random.uniform(30, 90),
        "gas_level": random.uniform(0.1, 1.5),
    }


if __name__ == "__main__":
    while True:
        print(generate_sample_telemetry())
        time.sleep(2)
