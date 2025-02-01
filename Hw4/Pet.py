#Create the class
class Pet:
    species = "" #Setting my class variable
    
    #Setting up the dictionary of animals for the following formulas
    def lifespan(self): 
        lifespans = {
            "dog": 13,
            "cat": 15,
            "lion":16
        }
        return lifespans.get(self.species, "Unknown")

    def __init__(self, name, age):
        self.name = name
        self.age = age

    #Method to calculate the human years 
    def humanyears(self):
        if self.species == "dog":
            return self.age * 7
        elif self.species =="cat":
            return 24 + (self.age - 2) * 4 if self.age > 1 else 15
        elif self.species == "lion":
            return self.age * 7

    def set_species(self, species):
        self.species = species

    def get_lifespan(self):
        return self.lifespan()

#My objects       
mypet = Pet("Legend", 8)
mypet.set_species("dog")

wifespet =  Pet("Elfie", 3)
wifespet.set_species("cat")

zoopet = Pet("Leo", 4)
zoopet.set_species("lion")

pets = [mypet, wifespet, zoopet]

#Printing the human age and lifespan (Looping for)
for pet in pets:
    print(f"{pet.name} is {pet.humanyears()} human years old.")
    print(f"Average lifespan of a {pet.species}: {pet.get_lifespan()} years.")


#Chat GPT PROMPTS

#Prompt 1:
#  I am trying to create a class variable called species in my code (set to empty). And then have a method that finds the species of my pet and returns its average lifespan. Is there a way to do that without including species within the attributes of my parent class Pet?

#Prompt 2: 
#ok so the method of average_lifespan is creating a dictionary to pull the different lifespans from?

#Prompt 3: Ok cool that all makes sense. The only thing that I am caught up on is that my objects only include the name of the pet and its age. How will it know its species without adding anything to my class?

#Prompt 4: does that follow these guidlines?  Implement a method within the class that takes the species of the pet as input and returns the average lifespan for that species.