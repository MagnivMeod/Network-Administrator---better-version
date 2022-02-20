import socket, threading


class Server(object):

    def __init__(self, host, port, listen=5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(listen)

    def accept(self, verbose=False):
        self.connection, address = self.sock.accept()
        if verbose:
            print("Server accept method verbose\nConnection: {0}\nAddress: {1}".format(self.connection, address))

    def send_data(self, connection, data):
        connection.sendall(data)

    def recv_data(self, connection, buffsize=1024):
        return connection.recv(buffsize)

    def close(self):
        self.sock.close()


class MultiClientServer(Server):

    def __init__(self):
        self.clients = []
        self.server_running = False

    def config(self, host, port, listen=5):
        Server.__init__(self, host, port, listen)

    def __call__(self):
        self.server_running = True
        serverAcceptThread = threading.Thread(target=self.accept)
        serverAcceptThread.start()

    def accept(self):
        while self.server_running:
            connection, address = self.sock.accept()
            client = {"conn":connection, "addr":address}
            self.clients.append(client)

    def close(self):
        self.server_running = False
        self.sock.close()


class Client(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __call__(self):
        try:
            self.sock.connect((self.host, self.port))
        except Exception as e:
            print("Error when trying to connect client:\n{0}".format(e))

    def send_data(self, data):
        self.sock.sendall(data)

    def recv_data(self, buffsize=1024):
        return self.sock.recv(buffsize)

    def close(self):
        self.sock.close()