# Server-side WebRTC program using TCP Signaling
# Written by Eddie Elvira

import numpy as np
import cv2
import multiprocessing
import asyncio
import json


from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling, BYE, add_signaling_arguments

def initialize_server_ball(channel):
    '''
    Initialize server-side ball and send its data to client
    '''
    global img, x, y, dirnx, dirny, kball, width, length, runball, color, radius
    width, length = 480, 640
    img = np.zeros((width, length, 3), dtype = 'uint8')
    color = (255, 255, 255)
    radius = 10

    x, y = width//2, length//2
    position = [x, y]

    dirnx, dirny = 2, -2
    displacement = [dirnx, dirny]

    runball = True
    msg_list = {
        "position": position, 
        "ball_color": color,
        "ball_radius": radius,
        "runball": runball,
        "window_width": width, 
        "window_length": length
    }
    # encode json message and send to client
    channel.send(json.dumps(msg_list))



def server_ball(channel):
    '''
    Display server-side ball and send its data to client
    '''
    global img, x, y, dirnx, dirny, runball, width, length, runball, color, radius
    # show image
    cv2.imshow('server', img)
    k = cv2.waitKey(10)
    img = np.zeros((width, length, 3), dtype='uint8') 

    # increment position using displacement variables
    x = x + dirnx
    y = y + dirny
    position = [x,y]
    radius = 10

    # draw ball
    cv2.circle(img,(x,y), radius, color, -1)

    if k != -1:
        runball = False

    # handle collisions
    if y >= width-radius:       # if ball reaches top boundary
        dirny *= -1
    elif y <= radius:           # if ball reaches bottom boundary
        dirny *= -1
    if x >= length - radius:    # if ball reaches right boundary
        dirnx *= -1
    elif x <= radius:           # if ball reaches left boundary
        dirnx *= -1

    msg_list = {
        "position": position, 
        "ball_color": color,
        "ball_radius": radius,
        "runball": runball,
        "window_width": width, 
        "window_length": length
    }

    channel.send(json.dumps(msg_list))

async def handle_answer(pc, tcp):
    '''
    Receive answer from client
    '''
    while True:
        answer = await tcp.receive()

        if isinstance(answer, RTCSessionDescription):
            await pc.setRemoteDescription(answer)

        elif isinstance(answer, RTCIceCandidate):
            await pc.addIceCandidate(answer)
        elif answer is BYE:
            print("Exiting Program")
            break

async def offer(lc, tcp):
    '''
    Connect to the client and create/send offer
    '''
    await tcp._connect(True)    #await connection to client
    dc = lc.createDataChannel("stream")
    print(f"Channel({dc.label}) - created by local party")

    async def send_media():
        global runball
        initialize_server_ball(dc)
        while True:
            if runball:
                server_ball(dc)
            else:
                 cv2.destroyAllWindows()
            await asyncio.sleep(0)

    @dc.on("message")
    def onmessage(message):
        print(f"New message from client: {message}")
    
    @dc.on("open")
    def onopen():
        print("Connection opened!")
        asyncio.ensure_future(send_media())

    await lc.setLocalDescription(await lc.createOffer())
    await tcp.send(lc.localDescription)   # send offer to client
    await handle_answer(lc, tcp)

if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 1234

    tcp = TcpSocketSignaling(HOST, PORT)
    pc = RTCPeerConnection()


    # run event loop
    loop = asyncio.get_event_loop()
    try: 
        loop.run_until_complete(offer(pc, tcp))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
        loop.run_until_complete(tcp.close())
