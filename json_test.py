import json

#create example dicitionary and save as json
dct = {}
dct["name"] = "tyson" #add to dictionary
dct["major"] = "data analytics"

#mutable so this gets changed in memory
dct["favorite_song"] = "crazy frog axel f"
dct['favorite_song'] = "i barely knew you"

print(dct)

#convert to a JSON file (the w allows you to create a new file)
file = open("tyson_info.json", "w")
json.dump(dct,file, indent = 4) #indent makes it have python style
#that file didn't have a path so it just saves to the main folder at the bottom

#loading the json back (needs to be in read mode ("r"))
file = open("tyson_info.json", "r")
dct2 = json.load(file)

#adding something new
dct2["favorite_animal"] = "dog"

print(dct2)

#re-creating it
file = open("tyson_info.json", "w") #this one has read access
json.dump(dct2,file, indent = 4)

#This down here does exception handling and is better practice than what I did
#with open(file) as file:
    #dump here

#with open(file) as file: (this has built in exception handling rather than a try)
    #dct2 = load stuff