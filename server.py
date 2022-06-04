import numpy as np
import cv2
import multiprocessing
import asyncio
import socket
from av import VideoFrame
import random
import colorsys
from threading import Thread


from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling, BYE


class BallStreamTrack(VideoStreamTrack):
    """
    A video stream track that displays continuous 2D images of a ball bouncing across the screen
    """
    
    def __init__(self):
        super().__init__()
        self.height, self.width = 320, 480
        self.x, self.y = 100, 100
        self.dx, self.dy = 2, 2
        self.radius = 20
        self.color = (0, 0, 0)
        self.randomize_color()

    async def recv(self) -> VideoFrame:
        """
        Send VideoFrame to client and display it on server-side window
        """
        pts, time_base = await self.next_timestamp()

        img = self.next_image()

        frame = VideoFrame.from_ndarray(img, format="bgr24")
        cv2.imshow("server", img)
        cv2.waitKey(1)
        frame.pts = pts
        frame.time_base = time_base
        return frame
    
    def next_image(self) -> np.ndarray:
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.x += self.dx
        self.y += self.dy
        cv2.circle(img, (self.x, self.y), self.radius, self.color, -1)

        if self.y >= (self.height - self.radius) or self.y <= self.radius:
            self.dy *= -1
            Thread(target=self.randomize_color).start()

        if self.x >= (self.width - self.radius) or self.x <= self.radius:
            self.dx *= -1
            Thread(target=self.randomize_color).start()

        return img
        
    def randomize_color(self) -> None:
        r, g, b = self.color
        while (r, g, b) == self.color:
            h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
            r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]   
        self.color = (r, g, b)


async def run(pc, signaling) -> None:
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
