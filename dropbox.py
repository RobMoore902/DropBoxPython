import hashlib
import os
import sys
import pdb

class dropbox:
    #important information
    version = "DROP/1.0"
    dir = ""
    encoding = ""
    
    def __init__(self, directory):
        if os.path.isdir(directory):
            self.dir = "./" + directory
        else:
            print "directory does not exist."
            sys.exit(0)
    
    #return message with directory listing and encoding
    def directory_listing(self):
        dir = os.listdir(self.dir)
        files = ""
        lines = 0  
        for file in dir:
            if self.encoding == "MD5_hash":
                files = files + self.MD5_hash(file) + "\r\n"
            elif self.encoding == "byte_count":
    
                files = files + self.byte_count(file) + "\r\n"
            else:
                return self.response('DIR', 100)
            lines = lines + 1
        message = self.response('DIR', 200)
        message = message + "Bytes: " + str(sys.getsizeof(files)) + "\r\n" 
        message = message + "Lines: " + str(lines) + "\r\n" + "\r\n" + files
        return message

    #determines the byte count of a file and returns a formatted string
    def byte_count(self, file):
        size = str(sys.getsizeof(file))
        file_name = str(file) + ":" + size
        return file_name

    #hashs a file and returns a formatted string with the filename and hash
    def MD5_hash(self, file_name):
        digest = hashlib.md5()
        file = open(self.dir+"/"+file_name)
        for line in file:
            digest.update(line)
        file_name = file_name + ":" + str(digest.hexdigest())
        return file_name

    #formats the first line of a request
    def request(self, command):
        request = command + " " + self.version + "\r\n"
        if command == 'EXG':
            return self.list_exchange_selection(request)
        return request

    #formats the first line of a GET request
    def get_file(self, name):
        command = "GET " + name
        request = self.request(command)
        return request

    #formats the header and body of a message that involves sending a file
    def send_file(self, name):
        path = self.dir + "/" + str(name)
        file = open(path, 'r')
        body = ""
        for line in file.readlines():
            body = body + line
        file.close()
        response = "Bytes: " + str(sys.getsizeof(body)) + "\r\n\r\n" + body
        return response        
    
    #creates a file in the dropbox's directory 
    def save_file(self, file_text, file_name):
        file = open(self.dir+"/"+file_name, 'w')
        file.write(file_text)
        file.close()

    #formats the PUT request
    def put_file(self, name):
        command = "PUT " + name
        request = self.request(command)
        request = request + self.send_file(name)
        return request 

    #formats the login request
    def login(self, username, password):
        request = self.request('Login')
        authorization = "authorization: " + username + ":" + password +"\r\n" + "\r\n"        
        request = request + authorization
        return request

    #takes in a username and password to authenticate the user
    def authenticate(self, username, password):
        if username == 'bob':
            if password == 'password':
                return self.response('Login', 200)
            else:
                return self.response('Login', 402)
        elif username == 'alice':
            if password == 'password':
                return self.response('Login', 200)
            else:
                return self.response('Login', 402)
        else:
            return self.response('Login', 401)

    #formats a request to choose an exchange selection
    def list_exchange_selection(self, request):
        body = "MD5_hash\r\n" + "byte_count\r\n"
        message = "Bytes: " + str(sys.getsizeof(body)) + "\r\n"
        message = message + "Lines: 2" + "\r\n" + "\r\n"
        request = request + message + body
        return request

    #decides an encoding type from an EXG command
    def summary_selection(self, request):
        parts = request.split('\r\n')
        if 'MD5_hash' in parts:
            body = "MD5_hash" + "\r\n"
            self.encoding = "MD5_hash"
        else:
            body = "byte_count" + "\r\n"
            self.encoding = "byte_count"
        header = "Bytes: " + str(sys.getsizeof(body)) + "\r\n \r\n" + body
        message = self.response('EXG', 200) + header
        return message

    #deletes a file
    def delete_file(self, name):
        if os.path.exists(self.dir+"/"+name):
            os.remove(self.dir+"/"+name)

    #formats a response message
    def response(self, command, num):
        if num == 100:
            phrase = "Unsupported encoding method, run EXG command."
        elif num == 200:
            phrase = "Success"
        elif num == 300:
            phrase = "Redirection"
        elif num == 400:
            phrase = "Client-Side Error"
        elif num == 500:
            phrase = "Server-Side Error"
        elif num == 402:
            phrase = "Bad password"
        elif num == 401:
            phrase = "Bad username"
        else:
            phrase = "Somthing bizare just happened"
        response = self.version + " " + command + " " + str(num) + " " + phrase + "\r\n"
        return response

    #determines if there are new files on the client side.
    def sync_client(self, operation):#take in the directory listing returned from the DIR command.
        snapshot = open('snapshot.txt', 'r+b')
        list2 = self.get_snapshot_list(snapshot)
        list1 = self.get_dir_list()
        l1 = set(list1)#directory listing
        l2 = set(list2)#snapshot listing
        if operation == 'PUT':
            client_diff = list(l1 - l2)#take client side differences and PUT/DELETE them on server
        if operation == 'DELETE':
            client_diff = list(l2 - l1)
        #self.create_snapshot()
        snapshot.close()
        return client_diff

    #determines if there are new files on the server side
    def sync_server(self, server_files, operation):
        snapshot = open('snapshot.txt', 'r+b')
        list1 = self.get_server_list(server_files)
        list2 = self.get_snapshot_list(snapshot)
        l1 = set(list1)
        l2 = set(list2)
        if operation == 'PUT':
            server_diff = list(l1-l2)
        if operation == 'DELETE':
            server_diff = list(l2-l1)
        self.create_snapshot()        
        snapshot.close()
        return server_diff

    def get_snapshot_list(self, snapshot):
        lines = snapshot.readlines()
        list1 = []
        for line in lines:
            file_name = line.split('\n')
            list1.append(file_name[0])
        return list1

    def get_dir_list(self):
        dir = os.listdir(self.dir)
        list1 = []
        for file in dir:
            list1.append(self.MD5_hash(file))
        return list1

    def get_server_list(self, server_files): 
        files = server_files.split('\r\n')
        list1 = []
        for file in files:
            if file != "":
                list1.append(file)
        return list1

    #Method to create a snapshot of the current directory for use with syncing
    def create_snapshot(self):
        file = open("snapshot.txt", 'w')
        file.seek(0)
        file_names = self.get_dir_list()
        for name in file_names:
            file.write(name+"\n")
        file.close()

