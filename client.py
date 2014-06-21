from Tkinter import *
from ttk import *

import Queue
import time
import socket
import threading

root = Tk()
root.geometry("645x415")
root.title("Donut")

class ThreadSafeTB(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.queue = Queue.Queue()
        self.update_me()
    def write(self, line):
        self.queue.put(line+"\n")
    def clear(self):
        self.queue.put(None)
    def update_me(self):
        try:
            while 1:
                line = self.queue.get_nowait()
                if line == None:
                    self.delete(1.0, END)
                else:
                    self.insert(END, str(line))
                self.see(END)
                self.update_idletasks()
        except Queue.Empty:
            pass
        self.after(100, self.update_me)

tb = ThreadSafeTB(root)
tb.place(x=0, y=0)

eb = Entry(root,width=90)
eb.place(x=2, y=390)

class Client:
	def __init__(self, tb, eb):
		self.tb = tb
		self.eb = eb

		self.ip = "192.3.21.183"
		self.port = 5555

		self.connected = True
		self.running = True

		self.initSocket()

		self.tb.write("[Donut]: Welcome to Donut!")
		self.sendToServer("len")
		self.tb.write("[Donut]: Type !help for commands or !new to talk to a stranger.")
	def sendMessage(self, msg):
		self.tb.write("<You>: "+msg)
		self.sendToServer("msg "+msg)

	def sendToServer(self, data):
		self.s.sendto(data, (self.ip, self.port))

	def initSocket(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.bind(("", 7775))

	def handleEntry(self, entry):
		if entry:
			if entry.startswith("!"):
				entry = entry[1:]
				if entry == "quit":
					self.sendToServer("quit")
				elif entry == "quitnew":
					self.sendToServer("quitnew")
				elif entry == "new":
					self.tb.write("[Donut]: Looking for a stranger...")
					self.sendToServer("new")
				elif entry == "help":
					self.tb.write("[Donut]: Commands:")
					self.tb.write("[Donut]: !help        View this help message")
					self.tb.write("[Donut]: !new         Talk to a stranger")
					self.tb.write("[Donut]: !quit        Quit the current chat")
					self.tb.write("[Donut]: !quitnew     Quit the current chat and connect to a new stranger")
					self.tb.write("[Donut]: !len         Print how many users are online")
				elif entry == "len":
					self.sendToServer("len")
				else:
					self.tb.write("[Donut]: Invalid command \"%s\"" % entry)
			else:
				self.sendMessage(entry)
	def handle(self, msg):
		if msg == "ping":
			self.sendToServer("pong")
		elif msg == "new":
			self.tb.write("[Donut]: You are now connected to a random stranger!")
		elif msg == "quit":
			self.tb.write("[Donut]: The other user disconnected!")
		elif msg == "quitt":
			self.tb.write("[Donut]: The other user timed out!")
		elif msg == "error":
			self.tb.write("[Donut]: Error!")
		elif msg.startswith("print"):
			message = " ".join(msg.split()[1:])
			tb.write("[Donut]: "+message)
		elif msg.startswith("msg"):
			message = " ".join(msg.split()[1:])
			tb.write("<Stranger>: "+message)

	def listener(self):
		while self.running:
			msg, addr = self.s.recvfrom(1024)
			if addr[0] == self.ip:
				threading.Thread(target=self.handle, args=(msg,)).start()

client = Client(tb, eb)
def ButtonFunction():
	global eb
	text = eb.get()
	eb.delete(0, END)
	client.handleEntry(text)

threading.Thread(target=client.listener).start()

sb = Button(root, text="Send", width=14, command=ButtonFunction)
sb.place(x=550, y=389)

root.mainloop()