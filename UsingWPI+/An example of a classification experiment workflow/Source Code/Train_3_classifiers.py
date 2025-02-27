import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, GlobalAveragePooling1D, GlobalMaxPooling1D, Concatenate, LayerNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.metrics import BinaryAccuracy
from transformers import AutoTokenizer, TFAutoModel
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
import sklearn.metrics as metrics

# Set constants
device_index = 3
max_len = 128 # 256 for part = 1 & 2
epochs = 3
batch_size = 4
dropout_rate = 0.1
learning_rate = 1e-5
dense_hidden_1 = 768 
dense_hidden_2 = 1024
model_name = "anferico/bert-for-patents"
parts=[0, 1, 2]

# File paths
file_train = "/PATH/CLTSep_VP_ipcr_1_train_dataset(processed).csv"
file_test = "/PATH/CLTSep_VP_ipcr_1_test_dataset(processed).csv"

# Set GPU
os.environ["CUDA_VISIBLE_DEVICES"] = str(device_index)

# Load dataset
def load_data(filepath, part):

    df = pd.read_csv(filepath, header=0, sep=";")
    
    if part == 0:
        df['text']= df['title_lang_en'] + " " + df['abstract_lang_en']
    elif part == 1:
        df=df.rename(columns={'description_lang_en': 'text'})
        del df['title_lang_en'], df['abstract_lang_en'], df['claims_lang_en']
    elif part == 2:
        df=df.rename(columns={'claims_lang_en': 'text'})
        del df['title_lang_en'], df['abstract_lang_en'], df['description_lang_en']   
    else: 
        print("Give a valid part number")
        
    print("Load")
    return df
    
# Label encoding
def encode_labels(df_train, df_test):
    labels_train = df_train["labels"].str.split(",") 
    labels_test = df_test["labels"].str.split(",")
    labels=pd.concat([labels_train,labels_test])
    
    encoder = MultiLabelBinarizer()
    encoded=encoder.fit_transform(labels)         
    encoded_train= encoded[0:labels_train.shape[0], :]   
    encoded_test= encoded[labels_train.shape[0]:labels_train.shape[0]+labels_test.shape[0], :]
    
    print(encoded_train.shape, encoded_test.shape)
    
    return encoded_train, encoded_test

#Convert the targets to probabilities
def calculate_probabilities(multihop_encoded_train):

    a = np.zeros((multihop_encoded_train.shape))

    for i in range(len(multihop_encoded_train)):
        sum_of_secondary_codes=sum(multihop_encoded_train[i])
        #print(sum_of_secondary_codes)

        for j in range(len(multihop_encoded_train[i])):
            if multihop_encoded_train[i][j]==1:
                a[i][j]=float(1/sum_of_secondary_codes)
    print('calculate_probabilities-Done! \n')

    return a

 # Tokenization function
def tokenize_texts(texts, tokenizer, max_length):
    return tokenizer(
        text=texts.tolist(),
        add_special_tokens=True,
        max_length=max_length,
        truncation=True,
        padding=True,
        return_tensors="tf",
        return_token_type_ids=False,
        return_attention_mask=True,
    )
    
# Model definition
def build_model(bert_model, num_labels, dropout_rate, dense_1, dense_2, is_multilabel=True ):
    input_ids = Input(shape=(max_len,), dtype=tf.int32, name="input_ids")
    attention_mask = Input(shape=(max_len,), dtype=tf.int32, name="attention_mask")

    embeddings = bert_model(input_ids, attention_mask=attention_mask)[0]
    avg_pool = GlobalAveragePooling1D()(embeddings)
    max_pool = GlobalMaxPooling1D()(embeddings)
    concat = Concatenate()([avg_pool, max_pool])
    
    x = LayerNormalization(epsilon=1e-7)(concat)
    x = Dense(dense_1, activation="relu")(x)
    x = Dropout(dropout_rate)(x)
    x = Dense(dense_2, activation="relu")(x)
    if is_multilabel:
        output = Dense(num_labels, activation="sigmoid")(x)
    else:
        output = Dense(num_labels, activation="softmax")(x)

    model = Model(inputs=[input_ids, attention_mask], outputs=output)
    return model

# Metric computation
def evaluate_model(y_true, y_pred, num_labels):
    y_pred_binary = np.zeros_like(y_pred)
    top_k = 1  # Change to desired k value

    for i in range(len(y_pred)):
        top_indices = np.argsort(y_pred[i])[-top_k:]
        y_pred_binary[i, top_indices] = 1

    print("Micro Metrics:")
    print("Precision:", metrics.precision_score(y_true, y_pred_binary, average="micro") * 100)
    print("Recall:", metrics.recall_score(y_true, y_pred_binary, average="micro") * 100)
    print("F1 Score:", metrics.f1_score(y_true, y_pred_binary, average="micro") * 100)

# Evaluation function suggested by chatgpt
def evaluate_model_2(y_true, y_pred):
    y_pred_binary = (y_pred > 0.5).astype(int)
    print("Micro Metrics:")
    print("Precision:", metrics.precision_score(y_true, y_pred_binary, average="micro") * 100)
    print("Recall:", metrics.recall_score(y_true, y_pred_binary, average="micro") * 100)
    print("F1 Score:", metrics.f1_score(y_true, y_pred_binary, average="micro") * 100)

for i, part in enumerate(parts):
   
    if part == 1 or part == 2:
        max_len = 256
    
    # Load data
    train_df = load_data(file_train, part)
    test_df = load_data(file_test, part)

    # Encode labels
    y_train, y_test = encode_labels(train_df, test_df)

    num_labels = y_test.shape[1]

    # Tokenize text
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    bert_model = TFAutoModel.from_pretrained(model_name)
    X_train = tokenize_texts(train_df["text"], tokenizer, max_len)
    X_test = tokenize_texts(test_df["text"], tokenizer, max_len)

    # Unfreeze last 4 layers (more adaptable)
    for layer in bert_model.layers[8:]:  
        layer.trainable = True
       
    # Build model
    model = build_model(bert_model, num_labels, dropout_rate, dense_hidden_1, dense_hidden_2, True)

    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss=BinaryCrossentropy(from_logits=False),
        metrics=["accuracy"],
    )

    # Train model
    history = model.fit(
        {"input_ids": X_train["input_ids"], "attention_mask": X_train["attention_mask"]},
        y_train,
        validation_data=(
            {"input_ids": X_test["input_ids"], "attention_mask": X_test["attention_mask"]},
            y_test,
        ),
        epochs=epochs,
        batch_size=batch_size,
    )

    # Predictions
    y_pred = model.predict({"input_ids": X_test["input_ids"], "attention_mask": X_test["attention_mask"]})
    
    #Store final predictions
    #print("Save final predictions")
    #df=pd.DataFrame(y_pred)
    #df.sort_values(by=0, axis=1, ascending=False)
    #df.to_csv("wpi_multi_part"+str(part)+".csv", header=False, index=False)   
    #if part==0:
    #    df=pd.DataFrame(y_test)
    #    df.sort_values(by=0, axis=1, ascending=False)
    #    df.to_csv('qrel.csv', header=False, index=False)
    
    print("Evaluation @1 all labels")
    evaluate_model(y_test, y_pred, num_labels)
    
    print("Evaluation with 0.5 threshold")
    evaluate_model_2(y_test, y_pred)