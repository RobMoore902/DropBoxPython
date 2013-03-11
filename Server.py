import socket 
import dropbox

backlog = 2
box =  dropbox.dropbox('test')
size = 1024 
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
serversock.bind(('euro.cs.dal.ca',22345)) 
serversock.listen(backlog)
clientsock, addr = serversock.accept()#need threads to accept more than one connection.
while True:
    data = None
    request = clientsock.recv(size)
    print request
    data = request.split()
    if data[0]:
        if data[0] == 'DIR':
            clientsock.send(box.directory_listing())
        elif data[0] == 'Login':
            login_info = data[3].split(':')
            clientsock.send(box.authenticate(login_info[0], login_info[1]))
        elif data[0] == 'EXIT':
            clientsock.send(box.response(data[0], 200))
            break
        else:
            clientsock.send(box.response(data[0], 400))
clientsock.close()

serversock.close()


