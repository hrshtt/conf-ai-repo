from datetime import datetime
import time

class time_tracker:

    # Initializer / Instance Attributes
    def __init__(self):
        self.start_time = time.time()

    # instance method
    def total_time(self):
    	total = ("%s" % (time.time() - self.start_time))
    	return '%.2f' % float(total)

def timestamp():
    dateTimeObj = datetime.now()
 
    timestampStr = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
 
    return '[' + timestampStr + ']'

def timestamp_simple():
    dateTimeObj = datetime.now()
 
    timestampStr = dateTimeObj.strftime("%Y-%m-%d_%H-%M-%S")
 
    return timestampStr

if __name__ == '__main__':
   
	# Instantiate the Dog object
	x = time_tracker()

	# call our instance methods
	print(x.total_time())