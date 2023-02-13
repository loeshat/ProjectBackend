'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''
import pickle
FILE_LOCATION = "datastore.p"

initial_object = {
    'users': {},
    'channels': {},
    'messages': {},
    'dms': {},
    'notifications': {},
    'user_stats': {},
    'server_stats': {},
    'reset_codes':{}
}

def pickle_and_store(object_to_persist: dict):
    with open(FILE_LOCATION, "wb") as file:
        pickle.dump(object_to_persist, file)


def unpickle_and_load() -> dict:
    data_contents = {}
    with open(FILE_LOCATION, "rb") as file:
        data_contents = pickle.load(file)
    for user in data_contents['users'].values():
        user['sessions'] = []
    return data_contents


class Datastore:
    def __init__(self):
       # print("Creating Data Store")
        try:
            self.__store = unpickle_and_load()
        except:
            self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        #print("Setting Data Store")
        self.__store = store
        pickle_and_store(self.__store)

#print('Loading Datastore...')

global data_store
data_store = Datastore()
