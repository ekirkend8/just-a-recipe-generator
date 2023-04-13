import os
import time
import copy
import tensorflow as tf


class RNNModel(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, rnn_units):
        super().__init__(self)
        tf.keras.backend.set_image_data_format("channels_last") # formats data to prevent error
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim) # input layer
        self.gru = tf.keras.layers.GRU(rnn_units, # type of RNN
                                       return_sequences=True,
                                       return_state=True)
        self.dense = tf.keras.layers.Dense(vocab_size) # output layer

    def call(self, inputs, states=None, return_state=False, training=False):
        x = inputs
        x = self.embedding(x, training=training)
        if states is None:
            states = self.gru.get_initial_state(x)
        x, states = self.gru(x, initial_state=states, training=training)
        x = self.dense(x, training=training)

        if return_state:
            return x, states
        else:
            return x


class OneStep(tf.keras.Model):
    """Make a single step prediction for next character and its new state."""
    def __init__(self, model, chars_from_ids, ids_from_chars, temperature=1.0):
        super().__init__()
        self.temperature = temperature
        self.model = model
        self.chars_from_ids = chars_from_ids
        self.ids_from_chars = ids_from_chars

        # Create a mask to prevent "[UNK]" from being generated.
        skip_ids = self.ids_from_chars(['[UNK]'])[:, None]
        sparse_mask = tf.SparseTensor(
            # Put a -inf at each bad index.
            values=[-float('inf')]*len(skip_ids),
            indices=skip_ids,
            # Match the shape to the vocabulary
            dense_shape=[len(ids_from_chars.get_vocabulary())])
        self.prediction_mask = tf.sparse.to_dense(sparse_mask)

    @tf.function
    def generate_one_step(self, inputs, states=None):
        # Convert strings to token IDs.
        input_chars = tf.strings.unicode_split(inputs, 'UTF-8')
        input_ids = self.ids_from_chars(input_chars).to_tensor()

        # Run the model.
        # predicted_logits.shape is [batch, char, next_char_logits]
        predicted_logits, states = self.model(
            inputs=input_ids, states=states, return_state=True
        )
        # Only use the last prediction.
        predicted_logits = predicted_logits[:, -1, :]
        predicted_logits = predicted_logits/self.temperature
        # Apply the prediction mask: prevent "[UNK]" from being generated.
        predicted_logits = predicted_logits + self.prediction_mask

        # Sample the output logits to generate token IDs.
        predicted_ids = tf.random.categorical(predicted_logits, num_samples=1)
        predicted_ids = tf.squeeze(predicted_ids, axis=-1)

        # Convert from token ids to characters
        predicted_chars = self.chars_from_ids(predicted_ids)

        # Return the characters and model state.
        return predicted_chars, states

    
def prep_checkpoints(checkpoint_dir='./training_checkpoints', checkpoint_epoch="checkpoint_{epoch}"):
    # Name of the checkpoint files
    checkpoint_prefix = os.path.join(checkpoint_dir, checkpoint_epoch)

    os.makedirs(checkpoint_dir, exist_ok=True)

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_prefix,
        save_weights_only=True
    )

    return checkpoint_callback


def train_rnn_model(dataset, ids_from_chars, vocab, embedding_dim=256, rnn_units=1024, epochs=20):
    # Length of the vocabulary in chars
    vocab_size = len(vocab)

    checkpoint_callback = prep_checkpoints()

    model = RNNModel(
        # Be sure the vocabulary size matches the `StringLookup` layers.
        vocab_size=len(ids_from_chars.get_vocabulary()),
        embedding_dim=embedding_dim,
        rnn_units=rnn_units
    )
    # logits: model returns probabilities / numbers btwn 0 and 1
    loss = tf.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer='adam', loss=loss)

    history = model.fit(dataset, epochs=epochs, callbacks=[checkpoint_callback])

    return history, model


def create_one_step_model(model, chars_from_ids, ids_from_chars):
    one_step_model = OneStep(model, chars_from_ids, ids_from_chars)
    return one_step_model


def apply_one_step_model(model, steps=1000):
    """Run the one-step RNN model in a loop to generate text."""
    start = time.time()
    states = None
    next_char = tf.constant(['Ingredients:'])
    result = [next_char]

    for n in range(steps):
        next_char, states = one_step_model.generate_one_step(next_char, states=states)
        result.append(next_char)

    result = tf.strings.join(result)
    end = time.time()
    print(result[0].numpy().decode('utf-8'), '\n\n' + '_'*80)
    print('\nRun time:', end - start)


def save_model(model, location="one_step"):
    tf.saved_model.save(one_step_model, location)
    return None


def retrieve_model(location):
    saved_model = tf.saved_model.load(
        location, tags=None, options=None
    )
    return saved_model