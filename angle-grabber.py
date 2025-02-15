import bpy
import asyncio
import websockets
import json

async def send_joint_angle():
    uri = "ws://localhost:8765"  # WebSocket server address
    async with websockets.connect(uri) as websocket:
        while True:
            knee_joint = bpy.data.objects["Armature"].pose.bones["Knee"]
            angle = knee_joint.rotation_euler.x  # Get knee joint angle
            data = json.dumps({"knee_angle": angle})
            await websocket.send(data)  # Send data as JSON
            await asyncio.sleep(0.1)  # Stream every 100ms

if __name__ == "__main__":
    # Run the async function
    asyncio.run(send_joint_angle())
