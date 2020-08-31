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


if running():
	print("Waiting 5 seconds before terminating the script...")
	time.sleep(5)

	print("Terminating script...")
	sb = Popen(['ps', '-a'], stdout=subprocess.PIPE)
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
	
	print("Closing Python!")
	target_process = "python3"
	for line in output.splitlines():
		try:	
			if target_process in str(line):
				pid = int(line.split(None, 1)[0])
				os.kill(pid, 9)
		except:
			continue
			
	print("Closed Python succesfully!")
	
	sb.terminate()
	
exit()
