import os
import time
import json
import redis
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import boto3

sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION"))
QUEUE_URL = os.getenv("SQS_QUEUE_URL")

print("🔥 Worker file loaded")

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
QUEUE_NAME = os.getenv("QUEUE_NAME", "incident_queue")


while True:
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        print("✅ Worker connected to DB")
        break
    except Exception:
        print("⏳ Worker waiting for DB...")
        time.sleep(2)

Session = sessionmaker(bind=engine)

Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    component_id = Column(String)
    status = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def process(body):
    data = json.loads(body)
    component = data["component_id"]

    print(f"⚙️ Processing: {component}")

    db = Session()
    incident = Incident(
        component_id=component,
        status="OPEN",
        start_time=datetime.utcnow()
    )
    db.add(incident)
    db.commit()

def run():
    print("🚀 Worker started (SQS mode)")

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )

            messages = response.get("Messages", [])

            if not messages:
                print("⏳ No messages...")
                continue

            for msg in messages:
                body = msg["Body"]
                print(f"📩 Received: {body}")

                process(body)

                # delete after processing
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=msg["ReceiptHandle"]
                )

        except Exception as e:
            print(f"❌ Worker error: {e}")