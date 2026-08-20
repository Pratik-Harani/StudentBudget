"""
Allows saving and loading of user data for persistence across app sessions

- Since the app uses an object-oriented structure, saving the User object using pickle is convenient
- However, pickle is not a secure method of data storage as it saves data in binary which can be modified to run malicious code 

- To-do for future versions: Change saving to a JSON format
"""

import pickle
dataFile = "userFile.pkl"


def saveToFile(userObject):
    with open(dataFile, 'wb') as file:
        pickle.dump(userObject, file)
        
        
def loadFromFile():
    try:
        with open(dataFile, 'rb') as file:
            return pickle.load(file)
    except(FileNotFoundError):
        return None
        

