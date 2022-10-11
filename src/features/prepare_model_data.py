import tensorflow as tf


def ingredients_to_text(recipe_dict):
    """Convert dict of recipes into a string"""
    all_ingredients = []

    for recipe_ingredients in list(recipe_dict.values()):
        all_ingredients.extend(["Ingredients:"])
        all_ingredients.extend(recipe_ingredients)

    ingredients_text = ""

    ingredients_text = ""

    for ingredient in all_ingredients:
        if ingredient == "Ingredients:":
            ingredients_text += "\n"
        ingredient_words = ingredient.split(" ")
        ingredients_text += ("\n " + " ".join(ingredient_words))

    ingredients_text = ingredients_text.lstrip()

    return ingredients_text


def tokenize_text(text):
    vocab = sorted(set(text))

    # split text into tokens to convert tokens to charcter ID's
    ids_from_chars = tf.keras.layers.StringLookup(
        vocabulary=vocab, mask_token=None
    )

    chars_from_ids = tf.keras.layers.StringLookup(
        vocabulary=ids_from_chars.get_vocabulary(),
        invert=True, mask_token=None
    )

    return vocab, ids_from_chars, chars_from_ids


def text_from_ids(ids, chars_from_ids):
  return tf.strings.reduce_join(chars_from_ids(ids), axis=-1).numpy()


def create_sequences(text, ids_from_chars, seq_length=100):
    all_ids = ids_from_chars(tf.strings.unicode_split(text, 'UTF-8'))

    ids_dataset = tf.data.Dataset.from_tensor_slices(all_ids)
    sequences = ids_dataset.batch(seq_length+1, drop_remainder=True)
    return sequences


def split_input_target(sequence):
    """Duplicates and shifts a sequence to align the input and label for each timestep"""
    input_text = sequence[:-1]
    target_text = sequence[1:]

    return input_text, target_text


def make_training_data(dataset0):
    # Batch size
    BATCH_SIZE = 64

    # Buffer size to shuffle the dataset
    # (TF data is designed to work with possibly infinite sequences,
    # so it doesn't attempt to shuffle the entire sequence in memory. Instead,
    # it maintains a buffer in which it shuffles elements).
    BUFFER_SIZE = 10000

    dataset = (
        dataset0
        .shuffle(BUFFER_SIZE)
        .batch(BATCH_SIZE, drop_remainder=True)
        .prefetch(tf.data.experimental.AUTOTUNE)
    )

    return dataset
