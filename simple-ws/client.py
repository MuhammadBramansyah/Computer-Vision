import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)

async def communicate(message):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        logging.info(f"Sent message to server: {message}")

        response = await websocket.recv()
        # logging.info(f"Received response from server: {response}")

async def main():
    messages = ["hai", "asd", "asdsa", "asdasdasda", "asdasdasd"]
    await asyncio.gather(*(communicate(msg) for msg in messages))

if __name__ == "__main__":
    asyncio.run(main())
