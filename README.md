# Real-Time Video Streaming Program

## Overview

A repository containing a server program that is able to display and transmit live video to a client program, which also displays the same video in real-time.

## Requirements

This project has several installations and requirements that must be satisfied before proceeding. The programs inside this repository can only run on a Python IDE/interpreter that meets these conditions:

- Is running on Linux (Debian/Ubuntu) or Mac OS X
- Uses Python 3.9 or higher (recommended)
- Has the following Python modules installed:
  - `aiortc`
  - `numpy`
  - `av`
  - `opencv`

The above modules can be installed using the following pip command:

```
pip install aiortc, numpy, av, opencv-python
```

## How to Run

The files `server.py` and `client.py` provide all the functionality for this project, and will need to run on <b>separate</b> terminals using these commands in the following order:

#### 1.) Run `server.py` on one terminal first

```
python3 server.py
```

#### 2.) Run `client.py` on a separate terminal

```
python3 client.py
```

This process can currently only occur within a localhost, but remote functionality on the command line will be implemented in a future update.

## Animated Demo(s)

<img src="./animations/server-client.gif" alt="Server and Client Video Feed" width="500"/>

## License

This repository is available under the MIT license. See the LICENSE file for more info.
