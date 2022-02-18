import numpy as np
import cv2
import multiprocessing
import asyncio
import json
import socket


from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
class BallStreamTrack(MediaStreamTrack):
    """
    A video stream track that displays continuous 2D images of a ball bouncing across the screen
    """

    kind = "video"

    def __init__(self):
        super().__init__()

    def send(self):
        pass

async def offer(pc, signaling):
    """
    Connect to client and send data by sending an offer and establishing a connection after an answer 
    """
    
    await signaling.connect()                               # Wait for a client to connect through socket
    pc.addTrack(BallStreamTrack())                          # Stream continuous 2D ball images
    await pc.setLocalDescription(await pc.createOffer())    
    await signaling.send(pc.localDescription)

    while True:
        obj = await signaling.receive()
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
        elif obj is BYE:
            print("Exiting Program")
            break

if __name__ == '__main__':
    ip = socket.gethostbyname(socket.gethostname())
    port = 8888

    signaling = TcpSocketSignaling(ip, port)                # Start signaling process on socket using TCP
    pc = RTCPeerConnection()                                # Create a new WebRTC Connection from peer to peer

    loop = asyncio.get_event_loop()                         # Event loop
    try: 
        loop.run_until_complete(offer(pc, signaling))       # Begin signaling process by sending offer
    except KeyboardInterrupt:
        pass                                                # Exit program when ^C is entered on command-line
    finally:
        loop.run_until_complete(signaling.close())          # End signaling process
        loop.run_until_complete(pc.close())                 # Close WebRTC Connection