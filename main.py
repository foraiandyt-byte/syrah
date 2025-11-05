import streamlit as st
import google.generativeai as genai
import os
from PIL import Image # We need this to handle the image file

API_KEY = "AIzaSyCPSoTZUvlXRkKq0kK1snpO6Mpl-hKqcmo" 

# Configure the generative AI library
try:
    genai.configure(api_key=AIzaSyCPSoTZUvlXRkKq0kK1snpO6Mpl-hKqcmo)
except Exception as e:
    st.error(f"Error configuring the Gemini API: {e}")
    st.stop()

# --- Model Initialization ---

# Create the Gemini model
# You can swap 'gemini-1.5-flash' for 'gemini-pro' or other models
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Error initializing the generative model: {e}")
    st.stop()

# --- Streamlit App UI ---

st.set_page_config(
    page_title="Syrah",
    page_icon="@",
    layout="centered"
)

# Initialize chat history in session state if it doesn't exist
# History now supports an optional 'image' key for multimodal messages
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("Syrah.Ace")
st.caption("Made wit love of Harris.")

# --- File Uploader Section ---
uploaded_file = st.file_uploader("Upload an image (JPG or PNG) for the AI to analyze:", type=["jpg", "jpeg", "png"])
image_part = None

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Image Ready for Analysis", use_column_width=True)
    try:
        # Open the image using PIL (required for Gemini API)
        image_part = Image.open(uploaded_file)
    except Exception as e:
        st.error(f"Could not process the uploaded file as an image: {e}")
        uploaded_file = None # Reset the file to prevent errors

# --- Chat Interface ---

# Display existing chat messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        # If the user message included an image in history, display it
        if message["role"] == "user" and message.get("image"):
            # Load image data from bytes
            try:
                # Use io.BytesIO to read the stored bytes
                from io import BytesIO
                history_image = Image.open(BytesIO(message["image"]))
                st.image(history_image, caption="User's Input Image", width=200)
            except Exception:
                st.write("*Image previously uploaded but could not be displayed.*")
        st.markdown(message["content"])

# Get user input
prompt = st.chat_input("What would you like to ask about the image, or general question?")

if prompt:
    
    # 1. Construct the contents list for the API
    contents_for_api = []
    
    # If an image was uploaded in the current run, add it to the API call
    if image_part is not None:
        contents_for_api.append(image_part)
    
    # Add the text prompt
    contents_for_api.append(prompt)

    # 2. Prepare user message for history and display
    history_entry = {"role": "user", "content": prompt}
    
    # Store the image data (bytes) in history for persistence across reruns
    if uploaded_file is not None:
        # We need BytesIO to read the uploaded file more than once (e.g., for display and storage)
        from io import BytesIO
        uploaded_file.seek(0) # Go to the start of the file
        history_entry["image"] = uploaded_file.read() # Store bytes
        
    st.session_state.chat_history.append(history_entry)
    
    # Immediately display the user's new message
    with st.chat_message("user"):
        if uploaded_file is not None:
            # Re-display the image from the uploaded file object
            st.image(uploaded_file, caption="Your Input Image", width=200)
        st.markdown(prompt)

    # 3. Generate and display the AI's response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Call the model with the multimodal list
                response = model.generate_content(contents_for_api)
                
                if response and response.text:
                    ai_response = response.text
                    st.markdown(ai_response)
                    # Add AI response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                else:
                    st.error("The model did not return a valid text response.")
    
    except Exception as e:
        st.error(f"An error occurred while generating the response: {e}")
