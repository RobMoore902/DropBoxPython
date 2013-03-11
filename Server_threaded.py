import socket 
import client_handler
import getopt
import sys

optlist = getopt.getopt(sys.argv[1:], 'p:')
args = []
for a,o in optlist[0]:
    args.append(o)
if len(args) != 1:
    print "must include: -p [port_number]"
    sys.exit(0)
try:
    int(args[0])
except ValueError:
    print "The -p value " + args[0] + " is not an integer."
    sys.exit(0)

backlog = 2
#size of sent data
size = 4096 
#information to setup and start listening on a port
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
serversock.bind(('', int(args[0]))) 
serversock.listen(backlog)

#start loop to create client threads as they connect
while True:
    clientsock, addr = serversock.accept()
    client_thread = client_handler.client_handler(clientsock)
    client_thread.start()
serversock.close()


