import socket
import dropbox
import sys
import getopt
import pdb

optlist = getopt.getopt(sys.argv[1:],'d:p:h:u:q:')
args = []
for a,o in optlist[0]:
    args.append(o)
#arg[0] = directory
#arg[1] = port num
#arg[2] = host name
#arg[3] = username
#arg[4] = password
if len(args) != 5:
    print "Must give the following information:"
    print "-d directory -p port# -h host_name -u username -q password"
    sys.exit(0)
try:
    int(args[1])
except ValueError:
    print "The -p value " + args[1]  + " is not an integer."
    sys.exit(0)
size = 4096

# Create the socket connection
box = dropbox.dropbox(args[0])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((args[2], int(args[1])))
    #sock.connect(('euro.cs.dal.ca', 22345))
except:
    print "Server not responding, exiting..."
    sys.exit(0)
sock.send(box.login(args[3], args[4]))
#sock.send(box.login('bob', 'password'))
login_response = sock.recv(size)
print login_response
response_code = login_response.split()
if response_code[2] == '401' or response_code[2] == '402':
    sock.send(box.request('EXIT'))
    sys.exit(0)
sock.send(box.request('EXG'))
while True:
    response = sock.recv(size)
    data = response.split()
    if data: 
        print response
        if data[1].lower() == 'exit':
            break
        if data[1].lower() == 'dir':
            client_diff_put    = box.sync_client('PUT')
            client_diff_delete = box.sync_client('DELETE')
            for file in client_diff_put:
                file = file.split(":")
                sock.send(box.put_file(str(file[0])))
                resp = sock.recv(size)
                print resp
            for file in client_diff_delete:
                file = file.split(":")
                sock.send(box.request('DELETE '+file[0]))
                resp = sock.recv(size)
                print resp
            server_files = response.split("\r\n\r\n")
            server_diff_put    = box.sync_server(server_files[1], 'PUT')
            server_diff_delete = box.sync_server(server_files[1], 'DELETE')
            
            for file in server_diff_put:
                file = file.split(":")
                sock.send(box.get_file(str(file[0])))
                resp = sock.recv(size)
                resp = resp.split("\r\n\r\n")
                box.save_file(resp[1], file[0])
                box.create_snapshot() 
                print resp[0] + resp[1]
            for file in server_diff_delete:
                file = file.split(":")
                box.delete_file(file[0])
                print "delete " + file[0]
                box.create_snapshot()
            sock.send(box.request('EXIT'))
        if data[1].lower() == 'exg':
            sock.send(box.request('DIR'))
# Finish with the socket
data = sock.recv(size)
if data:
    print data
sock.close()
