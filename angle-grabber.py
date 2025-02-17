import asyncio
import json
import threading

import bpy
import websockets

# WebSocket server address (update this to match your robot's IP)
WEBSOCKET_SERVER = "ws://localhost:8080"
ARMATURE_NAME = "Armature"  # Change to match your armature's name
BONE_NAME = "Bone"  # Change to match your bone's name

class WebSocketClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.websocket = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.running = True
        self.thread.start()
        print("WebSocket client initialized.")

    def run(self):
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        """Establish a persistent WebSocket connection."""
        try:
            async with websockets.connect(self.server_url) as websocket:
                self.websocket = websocket
                print("Connected to WebSocket server.")
                await self.listen()  # Keeps the connection alive
        except Exception as e:
            print(f"WebSocket Connection Error: {e}")

    async def listen(self):
        """Keep listening to maintain the connection."""
        while self.running:
            await asyncio.sleep(1)  # Keep connection alive

    def send_rotation(self, rotation):
        """Send rotation data asynchronously."""
        if self.websocket:
            data = json.dumps({"rotation": [rotation.x, rotation.y, rotation.z, rotation.w]})
            asyncio.run_coroutine_threadsafe(self.websocket.send(data), self.loop)
            print("Sending rotation data...")

    def close(self):
        """Close the WebSocket connection."""
        self.running = False
        self.loop.stop()
        self.thread.join()
        print("WebSocket client closed.")

# Initialize WebSocket client
ws_client = WebSocketClient(WEBSOCKET_SERVER)

def get_bone_rotation(armature_name, bone_name):
    """Gets the world rotation of a bone as a quaternion."""
    obj = bpy.data.objects.get(armature_name)
    if obj and obj.type == 'ARMATURE':
        pose_bone = obj.pose.bones.get(bone_name)
        if pose_bone:
            world_matrix = obj.matrix_world @ pose_bone.matrix
            return world_matrix.to_quaternion()
    return None

def my_handler(scene):
    global ARMATURE_NAME, BONE_NAME
    """Runs every 5 frames and sends bone rotation data via WebSocket."""
    if scene.frame_current % 5 == 0:
        rotation = get_bone_rotation(ARMATURE_NAME, BONE_NAME)
        if rotation:
            print(f"Frame {scene.frame_current}: Sending rotation {rotation}")
            ws_client.send_rotation(rotation)


if __name__ == "__main__":
    print("Registering frame change handler...")
    # Remove old handlers to avoid duplicates
    bpy.app.handlers.frame_change_pre.clear()
    # Add new handler
    bpy.app.handlers.frame_change_pre.append(my_handler)
    print("Finished registering frame change handler...")
