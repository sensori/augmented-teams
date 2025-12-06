import random
import datetime

random_num = random.randint(1, 1000)
timestamp = datetime.datetime.now().isoformat()
message = f"Hello, World! Random number: {random_num} | Timestamp: {timestamp}"

print(message)
