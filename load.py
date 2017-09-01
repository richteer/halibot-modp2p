from halibot import HalModule, Message
from subprocess import check_output as px
import os
import time
import base64

class Load(HalModule):

	def init(self):
		self.loadmode = False

		self.commands = {
			"!send":self.c_send,
			"!load":self.c_load,
		}

	def c_send(self, msg, target, module):

		if (target == self._hal.objects.get("irc").client.nickname):
			return

		os.system("tar czf tmp.tar packages/" + module)	

		with open("tmp.tar", "rb") as f:
			out = base64.b64encode(f.read())

		out = out.decode()
		os.remove("tmp.tar")

		m = Message()
		dest = ["irc/" + target]

		n = 64
		ls = ["!load start"] + [out[i:i+n] for i in range(0, len(out), n)]

		ls.append("!load stop")
		for l in ls:
			msg.body = l.replace("\n","")
			time.sleep(1)
			self.send_to(msg, dest)


	def c_load(self, msg, mode):
		self.log.info("LOAD CALLED = " + mode)
		if mode == "start":
			self.data = []
			self.loadmode = True
			self.log.info("STARTING LOAD")
			return
		self.log.info("ENDING LOAD")
		self.loadmode = False

		out = base64.b64decode("".join(self.data))

		with open("tmp.tar.gz", "wb") as f:
			f.write(out)

		self.data = []

		os.system("tar xzf tmp.tar.gz")
		os.remove("tmp.tar.gz")

		self.log.info("FINISHED LOADING")
		# instantiate the module

		# TODO: pull loading info from !load start, or load up the module another way somehow
		c = self._hal.get_package("hello")
		self._hal.add_instance("hello", c.Default(self._hal))


	# TODO: Make this only load data from a specific origin
	# ...so random channel chatter doesn't break the load :P
	def loaddata(self, msg):
		self.log.info("loading data...")
		self.data.append(msg.body)

	def receive(self, msg):
		argv = msg.body.split(" ")
		cmd = argv[0]
		args = argv[1:]

		f = self.commands.get(cmd, None)
		if f:
			self.log.info("calling '{}' with args '{}'".format(cmd, str(args)))
			f(msg, *args)
		elif self.loadmode:
			self.loaddata(msg)

		
