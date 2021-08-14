import socket
import threading
from typing import Coroutine
import numpy as np
import cv2
import multiprocessing
import asyncio
import argparse

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import BYE, TcpSocketSignaling, add_signaling_arguments, create_signaling


if __name__ == '__main__':
    PORT = 5555
    ADDR = socket.gethostbyname(socket.gethostname())

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(TcpSocketSignaling(ADDR, PORT)._connect(False))
    pc = RTCPeerConnection()

    # pc.createAnswer

'''
C:/Users/redma/OneDrive/Desktop/VSCode_Projects/SERVER-CLIENT-HACKATHON/client.py
'''