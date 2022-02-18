import numpy as np
import cv2
import multiprocessing
import asyncio
import json
import socket


from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling, BYE

class BallTransformTrack(MediaStreamTrack):
    """
    A video transform track that transforms frames of a 2D ball from another track
    """

    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        
async def answer(pc, signaling):
    """
    Connect to server and receive tracks by sending an answer after awaiting an offer
    """

    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)
        if track.kind == "video":
            pc.addTrack(BallTransformTrack(track))

    await signaling.connect()
    while True:
        obj = await signaling.receive()
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            if obj.type == "offer":
                # send answer
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting Program")
            break
        
if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    port = 8888

    signaling = TcpSocketSignaling(ip, port)                # Mark signaling process on socket that uses TCP
    pc = RTCPeerConnection()                                # Create a new WebRTC Connection from peer to peer

    loop = asyncio.get_event_loop()                         # Event loop
    try:
        loop.run_until_complete(answer(pc, signaling))      # Begin signaling process by responding to server offer
    except KeyboardInterrupt:                               # Exit program when ^C is entered on command-line
        pass
    finally:
        loop.run_until_complete(signaling.close())          # End signaling process
        loop.run_until_complete(pc.close())                 # Close WebRTC Connection