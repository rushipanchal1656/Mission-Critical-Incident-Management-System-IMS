# Debounce logic for incident creation to prevent duplicate incidents within a short time window

import redis
import time
import os

r = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, decode_responses=True)

WINDOW = 10

def should_create_incident(component_id):
    key = f"debounce:{component_id}"
    now = int(time.time())

    last = r.get(key)

    if last and now - int(last) < WINDOW:
        return False

    r.set(key, now, ex=WINDOW)
    return True