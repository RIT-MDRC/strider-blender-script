import asyncio
import threading
from dataclasses import dataclass

import bpy
import websockets


@dataclass
class WebsocketConnection:
    server_url: str
    connection: websockets.connect
    task: asyncio.Task = None


WEBSOCKET_SERVER = "ws://localhost:8080"
WEBSOCKET: dict[str, WebsocketConnection] = (
    dict()
)  # Global dictionary to store WebSocket connection and interval task

bl_info = {
    "name": "Send Websocket Message",
    "blender": (2, 80, 0),
    "category": "Object",
}


class SendMessage(bpy.types.Operator):
    bl_idname = "object.send_message"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Send websocket message"  # Display name in the interface.
    bl_options = {"REGISTER"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_url = WEBSOCKET_SERVER
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _connect(self):
        assert WEBSOCKET.get(self.server_url) is None
        try:
            conn = WebsocketConnection(
                server_url=self.server_url,
                connection=await websockets.connect(self.server_url),
            )
            WEBSOCKET[self.server_url] = conn
            print("WebSocket connection established.")
        except Exception as e:
            print(f"Failed to connect: {e}")

    async def _send_message(self):
        assert WEBSOCKET.get(self.server_url) is not None
        try:
            await WEBSOCKET.get(self.server_url).connection.send("hello")
            print("Message 'hello' sent successfully.")
        except Exception as e:
            print(f"Failed to send message: {e}")

    async def _close_connection(self):
        if WEBSOCKET.get(self.server_url) is not None:
            ws = WEBSOCKET.get(self.server_url)
            if (task := ws.task) is not None:
                task.cancel()
                ws.task = None
            try:
                await WEBSOCKET.get(self.server_url).connection.close()
                print("WebSocket connection closed.")
            except Exception as e:
                print(f"Failed to close connection: {e}")
            finally:
                WEBSOCKET[self.server_url] = None

    async def _send_message_interval(self, interval):
        while True:
            await self._send_message()
            await asyncio.sleep(interval)

    def execute(self, context):
        # Ensure connection is established
        if WEBSOCKET.get(self.server_url) is None:
            connect_future = asyncio.run_coroutine_threadsafe(
                self._connect(), self.loop
            )
            connect_future.result()  # Wait for connection to complete

        ws = WEBSOCKET.get(self.server_url)
        assert ws is not None
        # Check if an interval task is already running
        if (task := ws.task) is None:
            # Start the interval task
            ws.task = asyncio.run_coroutine_threadsafe(
                self._send_message_interval(2), self.loop
            )
            print("Started sending messages every 2 seconds.")
        else:
            # Cancel the interval task
            task.cancel()
            ws.task = None
            print("Stopped sending messages.")

        return {"FINISHED"}

    def close(self):
        # Close the WebSocket connection
        asyncio.run_coroutine_threadsafe(self._close_connection(), self.loop)
        # Stop the event loop
        self.loop.call_soon_threadsafe(self.loop.stop)
        # Wait for the thread to finish
        self.thread.join()


def menu_func(self, context):
    self.layout.operator(SendMessage.bl_idname)


def register():
    bpy.utils.register_class(SendMessage)
    bpy.types.VIEW3D_MT_object.append(
        menu_func
    )  # Adds the new operator to an existing menu.


def unregister():
    bpy.utils.unregister_class(SendMessage)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
