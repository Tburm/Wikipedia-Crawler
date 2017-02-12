import threading
import time

stop = False

def func1():
	global stop
	counter = 1

	for i in range(100):
		if stop:
			print counter
			break
		else:
			counter += 1
			time.sleep(1)
	pass

threading.Thread(target = func1).start()

raw_input('Prompt')
stop = True
