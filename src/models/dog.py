"""https://realpython.com/python3-object-oriented-programming/#what-is-object-oriented-programming-in-python"""
class Dog:
    # class attributes:
    #   same value for all class instances
    species = "Canis familiaris"

    # instance attributes:
    #   properties that all Dog objs must have
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # instance methods
    # dunder method: used to customize classes
    def __str__(self):
        return f"{self.name} is {self.age} years old"
    
    def speak(self, sound):
        return f"{self.name} says {sound}"


class Goldendoodle(Dog):
    # override method from parent class
    def speak(self, sound="WOOF"):
        return f"{self.name} says {sound}"
