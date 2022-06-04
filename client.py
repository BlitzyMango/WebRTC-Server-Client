import cv2
import multiprocessing
import asyncio
import socket
from av import VideoFrame


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
        print(f"Track ID: {track.id}")

    async def recv(self) -> VideoFrame:
        """
        Receive VideoFrames from server and display it on client-side window
        """
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        cv2.imshow("client", img)
        cv2.waitKey(1)
        return frame
        
        
async def run(pc, signaling) -> None:
    """
    Connect to server and receive tracks by sending an answer after awaiting an offer
    """

    @pc.on("track")
    def on_track(track):
        print("Connection opened!")
        print("Receiving %s" % track.kind)
        if track.kind == "video":
            pc.addTrack(BallTransformTrack(track))

    # connect signaling
    await signaling.connect()

    while True:
        obj = await signaling.receive()                                 # receive offer
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            if obj.type == "offer":
                await pc.setLocalDescription(await pc.createAnswer())   # create answer
                await signaling.send(pc.localDescription)               # send to server
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
        loop.run_until_complete(run(pc, signaling))      # Begin signaling process by responding to server offer
    except KeyboardInterrupt:                               # Exit program when ^C is entered on command-line
        pass
    finally:
        loop.run_until_complete(signaling.close())          # End signaling process
        loop.run_until_complete(pc.close())                 # Close WebRTC Connection
