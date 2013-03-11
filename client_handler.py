import dropbox
from threading import Thread

#client handler class, threaded to allow multiple client connections
class client_handler(Thread):
    def __init__ (self, socket):
        Thread.__init__(self)
        self.socket = socket
    
    def run(self):
        #create dropbox opject
        box = dropbox.dropbox('test')
        #start listening loop
        while True:
            data = None
            #recieve some data
            request = self.socket.recv(1024)
            #print request
            print request
            #split data on the spaces
            data = request.split()
            content = request.split("\r\n\r\n")
            #first value of split data is the command
            if data[0]:
                #send a directory listing to client
                if data[0].lower() == 'dir':
                    self.socket.send(box.directory_listing())
                #attempt to authenticate a user
                elif data[0].lower() == 'login':
                    login_info = data[3].split(':')
                    self.socket.send(box.authenticate(login_info[0], login_info[1]))
                #request to exit the program
                elif data[0].lower() == 'exit':
                    self.socket.send(box.response(data[0], 200))
                    break
                #request to choose summary selection
                elif data[0].lower() == 'exg':
                    response = box.summary_selection(request)
                    self.socket.send(response)
                #request to download a file from the server
                elif data[0].lower() == 'get':
                    response = box.response(data[0], 200)
                    response = response + box.send_file(str(data[1]))
                    self.socket.send(response)
                #sending a file to the server
                elif data[0].lower() == 'put':
                    self.socket.send(box.response(data[0], 200))
                    box.save_file(content[1], data[1])
                #recieve a request to delete a file
                elif data[0].lower() == 'delete':
                    self.socket.send(box.response(data[0], 200))
                    box.delete_file(data[1])
                    print 'trying to delete something.'
                #in the event of a command not being understood, an error is sent to the client
                else:
                    self.socket.send(box.response(data[0], 400))
        #close the socket when communication complete
        self.socket.close()


