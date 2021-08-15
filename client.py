import numpy as np
import cv2
import multiprocessing
import asyncio
import json


from aiortc import RTCPeerConnection, RTCIceCandidate, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling, add_signaling_arguments, create_signaling, BYE

async def client_ball(msg):
    global runball
    '''
    Display client-side ball using data received from server
    '''
    # extract contents from message
    width = msg["window_width"]
    length =  msg["window_length"]
    color = msg["ball_color"],
    radius = int(msg["ball_radius"])
    img = np.zeros((width, length, 3), dtype = 'uint8')

    # increment circle position based on server data
    position = msg["position"]
    x, y = position[0], position[1]

    runball = bool(msg['runball'])

    # draw ball
    img = cv2.circle(img, (x,y), 10, (255, 255, 255), -1)

    # show image
    cv2.imshow('client', img)
    k = cv2.waitKey(10)

    if k != -1:
        runball = False

async def handle_offer(pc, tcp):
    '''
    Receive offer from server and create/send answer
    '''
    while True:
        offer = await tcp.receive() #receive offer from server

        if isinstance(offer, RTCSessionDescription):
            await pc.setRemoteDescription(offer)
            if offer.type == "offer":
                await pc.setLocalDescription(await pc.createAnswer())
                await tcp.send(pc.localDescription)
        elif isinstance(offer, RTCIceCandidate):
            await pc.addIceCandidate(offer)
        elif offer is BYE:
            print("Exiting Program")
            break

async def answer(rc, tcp):
    '''
    Connect to the server and prepare to handle incoming offer
    '''
    await tcp._connect(False)   #await connection to server

    @rc.on("datachannel")
    def ondatachannel(channel):
        print(f'Channel({channel.label}) - Created by remote party')
        print("Connection opened!")
        @channel.on("message")
        def onmessage(message):
            global runball
            runball = True
            if runball:
                # decode json message from server
                msg = json.loads(message)
                asyncio.create_task(client_ball(msg))
            else:
                cv2.destroyAllWindows()

    await handle_offer(rc, tcp)


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 1234

    tcp = TcpSocketSignaling(HOST, PORT)
    pc = RTCPeerConnection()
    # run event loop
    loop = asyncio.get_event_loop()
    try: 
        loop.run_until_complete(answer(pc, tcp))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
        loop.run_until_complete(tcp.close())
