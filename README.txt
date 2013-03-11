Instructions

1. First you must start the server using the command: python Server_threaded.py -p [port number]
    
2. On a different machine enter the following command to start the client:
python Client.py -d [directory] -p [port number] -h [host name] -u [user name] -q [password]

LIST OF VALID USERS
users  passwords
________________
bob    password
alice  password

3. The program will automatically sync the server folder with the client one
and create a snapshot that will be used to update in the future.





TEST CASES
__________


to make sure the program was working correctly I tried it in several test
situations. In each I start with the folders and the snapshot.txt syncronized.

1. Add a new file to the client folder and run both programs. The new file
should appear in both snapshot.txt as well as the folder 'test' on the server.

2. Delete a file from the client folder and run both programs. The file should
be deleted from both snapshot.txt as well as the folder 'test' on the server.

3. Add a new file to folder 'test' on the server and run both programs. The new
file should appear in both snapshot.txt as well as in the designated folder on
the client side.

4. Delete a file from folder 'test' and run both programs. The file should be
deleted from both snapshot.txt as well as the designated folder on the client
side. 

5. Modify a file in the client folder and run both programs. The modified file
should appear in both snapshot.txt (updated hash) as well as in the folder
'test' on the server.

6. Modify a file in the folder 'test' on the server and run both programs. The
modified file should appear in both snapshot.txt (updated hash) as well as in
the client folder.


PROGRAM STRUCTURE
_________________

The server includes the client_handler which creates threads for individual
connections. On each thread is a listener for different commands (PUT, DELETE,
GET, EXG, DIR, EXIT) whenever a message is recieved it will send a response to
the server. If the message recieved is in the correct format the server will
execute on of the 6 commands listed above. 

The client uses the arguments passed from the user to connect to the server
and sync a folder. The client is programmed to connect to the server first.
Next an exchange where the server chooses an encodig method for file
differences (MD5 is preferred). Next the client requests a list of the files
on the server, when this is returned the client begins comparing the contents
of its folder to its snapshot of the last sync and with the list the server
returned and sends out the appropriate GET, PUT, and delete commands to make
the two folders the same. Finally it updates the snapshot.txt file for the
next sync.

Both the client and the server include a file called dropbox.py. This file has
all the functionality for constructing the DROP/1.0 message structure. It also
contains all of the client functions necessary to sync folders. 
