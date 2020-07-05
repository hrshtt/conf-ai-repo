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

class checkpoint_tracker:

    def __init__(self):
        self.performance_tracker = {}

    def get_performance(self):
        return self.performance_tracker

    def create_checkpoint(self, header):
        def store_header_wrapper(func):
            def wrapper(*args, **kwargs):
                checkpoint_start_time = time.time()
                print(f"[INFO] Running {header} @ {timestamp()}")
                val = func(*args, **kwargs)
                print(f"[INFO] Completed {header} @ {timestamp()}")
                print(f"\n{'####'*20}\n")
                total = (time.time() - checkpoint_start_time)
                self.performance_tracker[header] = total
                return val
            return wrapper
            store_header_wrapper.__name__=func.__name__
            store_header_wrapper.__doc__=func.__doc__
        return store_header_wrapper

def timestamp():
    dateTimeObj = datetime.now()
 
    timestampStr = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
 
    return '[' + timestampStr + ']'

def timestamp_simple():
    dateTimeObj = datetime.now()
 
    timestampStr = dateTimeObj.strftime("%Y-%m-%d_%H-%M-%S")
 
    return timestampStr

def pretty_timestamp(text):
    print("----"*20)
    print(f"{text} at: {timestamp()}")
    print("----"*20)

if __name__ == '__main__':
   
	# Instantiate the Dog object
	x = time_tracker()

	# call our instance methods
	print(x.total_time())