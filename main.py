import streamlit as st
import tensorflow as tf
from PIL import Image
from keras.applications.resnet import preprocess_input, decode_predictions
import redis
import pickle

# Redis Cache
redis_db = redis.Redis(host="redis_service", port=6379, username="default", password="password", db=0)


def get_prediction(input_image, model):
    # preprocess the input image
    img = input_image.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    img_array = preprocess_input(img_array)

    # predict the image
    predictions = model.predict(img_array)
    label = decode_predictions(predictions, top=1)[0][0][1]
    return label


# Cache the model
@st.cache_resource
def load_model():
    # Load the pre-trained ResNet50 model and set weights
    model = tf.keras.applications.ResNet50(weights='imagenet')
    return model


def main():
    st.title("Image object prediction")
    st.write("This application can predict objects in an image.")

    model = load_model()

    image_file = st.file_uploader("Upload an image", type=['jpeg'])

    if image_file:
        input_image = Image.open(image_file)
        # Display the uploaded image
        st.image(input_image, caption="Uploaded image", use_column_width=True)
        pred_button = st.button("Predict")

        if pred_button:
            # Convert image to bytes for caching
            input_image_bytes = pickle.dumps(input_image)

            # Check if prediction already cached
            if redis_db.exists(input_image_bytes):
                prediction = pickle.loads(redis_db.get(input_image_bytes))
            else:
                prediction = get_prediction(input_image, model)
                # Cache the prediction
                redis_db.set(input_image_bytes, pickle.dumps(prediction))

            st.title("Prediction")
            st.write(prediction)


if __name__ == '__main__':
    main()
