import asyncio
import websockets
import logging
import json 
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)


bootstrap_servers = "localhost:9092"
topic_name = 'test_bram'
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

def send_to_kafka(data):
    producer.send(topic_name, json.dumps(data).encode('utf-8'))
    producer.flush()

async def handle_connection(websocket, path):
    async for message in websocket:
        logging.info(f"Received message from client: {message}")
        await websocket.send(f"Received: {message}")

        try:
            data = json.loads(message)
            logging.info(f"data received from websocket: {data}")
            send_to_kafka(data)
            logging.info("Data sended to kafka :", data)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

async def main():
    server = await websockets.serve(handle_connection, "localhost", 8765)
    logging.info("WebSocket server started")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
