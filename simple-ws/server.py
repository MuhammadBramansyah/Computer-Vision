import asyncio
import websockets
import signal
import logging
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

logging.basicConfig(level=logging.INFO)

clients = set()

async def handler(websocket, path):
    clients.add(websocket)
    logging.info(f"New client connected: {websocket.remote_address}")

    try:
        while True:
            message = await websocket.recv()
            logging.info(f"Received message from {websocket.remote_address}: {message}")

            response = f"Echo: {message}"
            await websocket.send(response)
            logging.info(f"Sent response to {websocket.remote_address}: {response}")
    except (ConnectionClosedOK, ConnectionClosedError) as e:
        logging.info(f"Client {websocket.remote_address} disconnected: {e}")
    finally:
        clients.remove(websocket)

async def broadcast(message):
    if clients:
        logging.info(f"Broadcasting message: {message}")
        await asyncio.wait([client.send(message) for client in clients])

async def periodic_broadcast():
    while True:
        await asyncio.sleep(10)
        message = "Halo ini aku kirim pesan"
        await broadcast(message)

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    logging.info("WebSocket server is running on ws://localhost:8765")

    broadcast_task = asyncio.create_task(periodic_broadcast())

    try:
        await server.wait_closed()
    finally:
        broadcast_task.cancel()

        # Graceful shutdown
    for signame in {'SIGINT', 'SIGTERM'}:
        asyncio.get_event_loop().add_signal_handler(
            getattr(signal, signame),
            lambda: asyncio.create_task(shutdown(server))
        )

async def shutdown(server):
    logging.info("Shutting down server...")
    for websocket in clients:
        await websocket.close(reason="Server shutdown")
    server.close()
    await server.wait_closed()
    logging.info("Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())