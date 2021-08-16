This file was written by @BlityMango on Github and was inspired by several aiortc examples that already exist on GitHub. This program is still being updated as of 8/16/2021. 
In order to run this program, both server.py and client.py should be downloaded onto a machine that uses Linux (Ubuntu Linux 20.04 is recommended, but the programs may still work on older versions such as 18.04).
Server.py must run before client.py is ran. This can be done by executing each program in different terminal windows.
Once both programs are running, events will occur as follows:
1.) The server will send an offer to the client
2.) The client will receive the offer and handle it by sending back an answer to the server
3.) Once the server receives an answer back from the client, the "three-way-handshake" will be complete a channel (connection) will open for streaming data
4.) The server will begin sending data to the client that will help it display a 2D ball
5.) Using OpenCV, the client will display the animation of the 2D ball

Code hasn't been developed to help the client receive the data as images instead of messages. More developments will be made to add this feature so that the server may be able to send other kinds of animations.
Error-checking and unit tests will also be made and documented in this README file to perfect these programs and prevent the possibility of any issues occurring.
