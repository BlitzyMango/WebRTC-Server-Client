import numpy as np
import cv2
import multiprocessing
import asyncio
import socket
from av import VideoFrame


from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling, BYE


class BallStreamTrack(VideoStreamTrack):
    """
    A video stream track that displays continuous 2D images of a ball bouncing across the screen
    """
    
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.frames = []

        for i in range(0, 200, 2):
            img = np.ones((200, 200, 3), dtype=np.uint8) * i
            self.frames.append(VideoFrame.from_ndarray(img, format="bgr24"))

    async def recv(self):
        """
        Send VideoFrame to client and display it on server-side window
        """
        pts, time_base = await self.next_timestamp()

        frame = self.frames[self.counter % 100]
        img = frame.to_ndarray(format="bgr24")
        cv2.imshow("server", img)
        cv2.waitKey(1)
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame

async def run(pc, signaling):
    """
    Connect to client and send data by sending an offer and establishing a connection after an answer 
    """
    
    await signaling.connect()                               # Wait for a client to connect through socket
    pc.addTrack(BallStreamTrack())                          # Stream continuous 2D ball images

    @pc.on("track")
    def on_track(track):
        print("Connection opened!")
        print(f'')
        
    await pc.setLocalDescription(await pc.createOffer())    # Create aiortc offer
    await signaling.send(pc.localDescription)               # Send to client

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
        loop.run_until_complete(run(pc, signaling))         # Begin signaling process by sending offer
    except KeyboardInterrupt:
        pass                                                # Exit program when ^C is entered on command-line
    finally:
        loop.run_until_complete(signaling.close())          # End signaling process
        loop.run_until_complete(pc.close())                 # Close WebRTC Connection
