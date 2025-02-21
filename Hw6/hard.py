import time

lst = [30,8,12,15,5,76,8]

# O(n)
high = lst[0]
low = lst[0]
start = time.time()

for i in lst:
    if i > high:
        high = i 
    if i < low:
        low = i

difference = high - low
end = time.time()  

print("The largest difference in numbers was: ", difference)
print("The runtime was ", end-start, "seconds")

#Chat prompt

#is there an easier way to get the high and low of a list without running a sort?