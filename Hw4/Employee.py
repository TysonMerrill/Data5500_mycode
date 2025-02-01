#Create the class
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    #Method to calculate the increase of salary  
    def increase(self):
        return self.salary * 1.1
        
#My object       
emp1 = Employee("John", 5000)

#Printing the new salary
print(emp1.name + "'s salary with the increase is:", emp1.increase())