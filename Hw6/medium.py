import time

lst = [30,8,12,15,5,76,8]

# O(n^2)
start = time.time()

for x in range(len(lst)-1):
    for i in range(len(lst)-1):
        #compare two elements and swap if elemnt 1 is greater
        if lst[i] > lst[i+1]:
            lst[i], lst[i+1] = lst[i+1], lst[i]

second_largest = lst[-2]
end = time.time()  

print("The 2nd largest number was: ", second_largest)
print("The runtime was ", end-start, "seconds")

#I used class examples again to help me