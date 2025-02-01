#Create the class
class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width

    #Method to calculate the area    
    def area(self):
        return self.length * self.width
        
#My object       
myshape = Rectangle(5,3)

#Printing the area
print("My Shapes area is:", myshape.area())