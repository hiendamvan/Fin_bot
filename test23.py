# Q1: LATE BINDING 
# def create_multipliers():
#     multipliers = []
#     for i in range(4): 
#         def multiplier(x):
#             return i * x
#         multipliers.append(multiplier)
#     return multipliers
        
# funcs = create_multipliers()
# results = [f(10) for f in funcs]
# print(results)


# Q2: THREADING 
# import threading
# import time

# def count():
#     x = 0
#     for _ in range(10**2):
#         x += 1

# t1 = threading.Thread(target=count)
# t2 = threading.Thread(target=count)
# start = time.time()
# t1.start(); t2.start()
# t1.join(); t2.join()
# print("Time:", time.time() - start)

# Q3: EXCEPTION HANDLING 
def system_check():
    try: 
        return "Check passed"
    except:
        return "Error"
    finally: 
        return "KiiKii"
    
message = system_check()
print(message)