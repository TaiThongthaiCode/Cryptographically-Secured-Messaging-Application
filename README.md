# CryptoProject

This program simulates a network whereby a client can send a cryptographically secure message to the server.  Read the design document for details of 
the application implementation.

Running the Program Directions:
1. Go to the netsim directory.
2. Edit client.py and change 'CLIENT_FOLDER_PATH' to your desired client folder location
3. Edit client.py and change 'RELATIVE_SERVER_PATH' to your desired server folder location
4. Open terminal/command prompt, go to netsim and run the command: "python3 network.py -p './network/' --clean"
5. Open terminal/command prompt, go to netsim and run the command: "python3 server.py"
6. Open terminal/command prompt, go to netsim and run the command: "python3 client.py"
