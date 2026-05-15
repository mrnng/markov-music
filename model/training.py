import json
import tensorflow.keras as keras
from model.data_processing import generate_training_sequences
from model.data_processing import SEQUENCE_LENGTH, SINGLE_FILE_DATASET_PATH, MAPPING_PATH

with open(MAPPING_PATH, "r") as f:
    OUTPUT_UNITS = len(json.load(f))

NUM_UNITS = [256]
LOSS = "sparse_categorical_crossentropy"
LEARNING_RATE = 0.001
EPOCHS = 2
BATCH_SIZE = 64
SAVE_MODEL_PATH = "model.weights.h5"

def build_model(output_units, num_units, loss, learning_rate):
    # INTEGER INPUTS
    input_layer = keras.layers.Input(shape=(SEQUENCE_LENGTH,))

    # EMBEDDING LAYER
    x = keras.layers.Embedding(
        input_dim=output_units,
        output_dim=128
    )(input_layer)

    x = keras.layers.LSTM(num_units[0])(x)
    x = keras.layers.Dropout(0.2)(x)

    # OUTPUT
    output_layer = keras.layers.Dense(
        output_units,
        activation="softmax"
    )(x)

    # COMPILE MODEL
    model = keras.Model(input_layer, output_layer)

    model.compile(
        loss=loss,
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        metrics=["accuracy"]
    )

    model.summary()

    return model

def train(output_units, num_units, loss, learning_rate, epochs, batch_size, save_model_path):
    # 1. GENERATE THE TRAINING SEQUENCES
    inputs, targets = generate_training_sequences(SEQUENCE_LENGTH, SINGLE_FILE_DATASET_PATH, MAPPING_PATH)
    # 2. BUILD THE NETWORK
    model = build_model(output_units, num_units, loss, learning_rate)
    # 3. TRAIN THE MODEL
    checkpoint = keras.callbacks.ModelCheckpoint(
        filepath="checkpoint_epoch_{epoch:02d}.weights.h5",
        save_weights_only=True,
        save_freq="epoch"
    )
    model.fit(
        inputs,
        targets,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[checkpoint]
    )
    # 4. SAVE THE MODEL
    model.save_weights(save_model_path)

if __name__ == "__main__":
    train(OUTPUT_UNITS, NUM_UNITS, LOSS, LEARNING_RATE, EPOCHS, BATCH_SIZE, SAVE_MODEL_PATH)