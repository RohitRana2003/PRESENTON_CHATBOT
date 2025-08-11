import streamlit as st
import requests
import json
import os

# --- Configuration ---
# Your local Presenton API URL
PRESENTON_API_URL = "http://localhost:5000/api/v1/ppt/presentation/generate"
PRESENTON_BASE_URL = "http://localhost:5000"

# --- Page Setup ---
st.set_page_config(page_title="Presenton Chatbot", page_icon="🤖")
st.title("Presenton AI Presentation Chatbot")
st.caption("Start a conversation, then click 'Create Presentation' to generate a PPTX from the chat history.")

# --- Session State for Chat History ---
# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Functions ---

def generate_presentation_from_chat():
    """
    Generates a presentation using the Presenton API based on the full chat history.
    """
    with st.spinner("Generating presentation... this may take a moment."):
        # Construct a single prompt from the entire chat history
        chat_summary_prompt = "Based on the following conversation, create a presentation:\n\n"
        for msg in st.session_state.messages:
            chat_summary_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        st.write(f"Sending prompt to API: {chat_summary_prompt[:100]}...")

        # Prepare the form data as a dictionary
        # The 'requests' library handles multipart/form-data for us with the 'files' parameter
        # even for simple string data.
        data = {
            "prompt": (None, chat_summary_prompt),
            "n_slides": (None, "5"),
            "language": (None, "English"),
            "layout": (None, "general"),
            "export_as": (None, "pptx")
        }

        try:
            # Make the API call to your local Presenton server
            response = requests.post(PRESENTON_API_URL, files=data)
            
            # Raise an exception for bad status codes
            response.raise_for_status()

            # Process the successful response
            response_json = response.json()
            st.success("Presentation created successfully!")

            # Display a download link
            if response_json.get("path"):
                download_path = response_json["path"]
                # Create a clickable download link
                st.markdown(f"**[Download your presentation]({PRESENTON_BASE_URL + download_path})**")
            
            # Display an edit link
            if response_json.get("edit_path"):
                edit_path = response_json["edit_path"]
                st.markdown(f"**[Edit your presentation]({PRESENTON_BASE_URL + edit_path})**")

        except requests.exceptions.RequestException as e:
            st.error(f"Error calling Presenton API: {e}")
            st.error("Please ensure the Presenton server is running on http://localhost:5000")
            st.error(f"API Response: {response.text}")

# --- Chat Interface ---

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What do you want to talk about?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simulate an AI response and add it to history
    # For this example, we'll just acknowledge the message
    with st.chat_message("assistant"):
        response = f"Received your message: '{prompt}'. You can continue the conversation or click 'Create Presentation'."
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Presentation Generation Button ---
st.divider()
if st.button("Create Presentation from Chat History", type="primary"):
    if st.session_state.messages:
        generate_presentation_from_chat()
    else:
        st.warning("Please start a conversation first.")
