import time

lst = [30,8,12,15,5,76,8]

# O(n)
start = time.time()
total = 0
for i in lst:
    total += i

end = time.time()  
print("The sum is: ", total)
print("The runtime was ", end-start, "seconds")

#I just used class examples here to help me