import pickle


def save_pickle(big_object, pickle_path):
    with open(pickle_path, "wb") as pickle_file:
        pickle.dump(big_object, pickle_file, protocol=4)
    print(f"Saving pickle to {pickle_path}...")


def load_pickle(load_object, pickle_path):
    with open(pickle_path, "rb") as pickle_file:
        load_object = pickle.load(pickle_file)
    print(f"Loading {pickle_path} for consumption...")

    return load_object
