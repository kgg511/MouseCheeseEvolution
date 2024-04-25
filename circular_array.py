from collections import deque

class CircularArray:
    def __init__(self, items):
        self.circular_array = deque(maxlen=len(items))
        self.current_index = 0
        self.circular_array.extend(items) # add items to the deque (WE DON'T KNOW WHICH WILL BE USED YET)
        self.length = 0 # set when behavior tree created
        self.listVersion = None #To be set later by convertToList when behavior tree created
    
    def convertToList(self):
        return [self.get(i) for i in range(self.length)]

    def enqueue(self, item):
        self.circular_array.append(item)
        self.length += 1

    def dequeue(self): # remove item from array
        return self.circular_array.popleft()
    
    def get(self, index):
        if index > self.length - 1: # keep the abstraction
            raise IndexError("Index out of bounds")
        return self.circular_array[index % len(self.circular_array)]
    
    def get_element(self): # get current element and progress forward to next
        if len(self.circular_array) == 0:
            print("Circular array is empty")
        else:
            value = self.circular_array[self.current_index]
            next_index = (self.current_index + 1) % len(self.circular_array) 
            self.current_index = next_index
            self.length += 1
            return value