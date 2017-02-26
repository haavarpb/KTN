# This skeleton is valid for both Python 2.7 and Python 3.
# You should be aware of your additional code for compatibility of the Python version of your choice.

import time
from socket import *

# Get the server hostname and port as command line arguments                    
host = "127.0.0.1"
port = 8888
 
# Create UDP client socket
udpSocket = socket(AF_INET, SOCK_DGRAM)

# Note the second parameter is NOT SOCK_STREAM
# but the corresponding to UDP

# Set socket timeout as 1 second
udpSocket.settimeout(1)

# Sequence number of the ping message
ptime = 0

# Ping for 10 times

print "Starting client..."

while ptime < 10: 
    ptime += 1
    # Format the message to be sent as in the Lab description	
    
    timeSent = time.clock()
    data = str(ptime)
    
    try:
    	
    	# Record the "sent time"

    	# Send the UDP packet with the ping message
        udpSocket.sendto(data, (host, port))
        print "Packet out: " + data + " at time ", time.localtime().tm_hour,":", time.localtime().tm_min,":", time.localtime().tm_sec

    	# Receive the server response
        recvData, recvAddr = udpSocket.recvfrom(1024)
        timeReceived = time.clock()
    	# Record the "received time"
        print "Packet in: " + recvData + " Round trip time " + '{0:.2}'.format((timeReceived - timeSent)*1000) + " ms"
    	# Display the server response as an output
    	# Round trip time is the difference between sent and received time
    except timeout:
        # Server does not response
	    # Assume the packet is lost
        print("Request timed out.")
        continue

# Close the client socket
udpSocket.shutdown(SHUT_RDWR)
udpSocket.close()
 
