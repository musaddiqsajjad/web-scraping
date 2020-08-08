import psutil
import sys
import subprocess
from subprocess import Popen
import time
import os

def running():
	for process in psutil.process_iter():	
		if process.cmdline() == ['python3', 'getProducts.py']:
			print('Process found! ----------------------------------------------------------------------------------------------------------------------------')
			return True
		else:
			continue
	print('Process not running! ----------------------------------------------------------------------------------------------------------------------------')
	return False

def start():
	print("Starting script")
	script = Popen(['python3', 'getProducts.py'])
	
def close():
	print("Terminating script...")
	script.terminate()


while True:
	if running():
		print("Waiting 40 minutes before terminating the script...")
		time.sleep(2400)
	
		print("Terminating script...")
		script.terminate()
		sb = Popen(['ps', '-A'], stdout=subprocess.PIPE)
		output, error = sb.communicate()

		print("Closing Chrome!")
		target_process = "chrome"
		for line in output.splitlines():
			try:	
				if target_process in str(line):
					pid = int(line.split(None, 1)[0])
					os.kill(pid, 9)
			except:
				continue
		print("Closed Chrome succesfully!")
		sb.terminate()
		
		print("Waiting 5 seconds")
		time.sleep(5)
		
		print("Starting script")
		script = Popen(['python3', 'getProducts.py'])
		
		continue
	else:
		print("Waiting 5 seconds to make sure script isn't in transitionary phase.") 
		time.sleep(5)
		if not running():
			print("Starting script")
			script = Popen(['python3', 'getProducts.py'])
		
