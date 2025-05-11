
For this phase, we'll use **Streamlit**. It's a Python library that allows you to create and share custom web apps for machine learning and data science projects with incredible ease.

---

**Phase 6: Simple User Interface with Streamlit**

**1. Introduction to Streamlit:**

* **What:** Streamlit is an open-source Python library that makes it easy to create beautiful, custom web applications for machine learning and data science. You write Python scripts, and Streamlit renders them as interactive web UIs.
* **Why use Streamlit for this project?**
    * **Python-Native:** You can write the UI entirely in Python.
    * **Fast Development:** It's designed for rapid prototyping. You can create a useful UI with very few lines of code.
    * **Interactive Widgets:** Comes with built-in widgets like text inputs, buttons, sliders, etc.
    * **Easy Integration:** We can easily make HTTP requests from our Streamlit app to our FastAPI backend.
    * **Focus on Functionality:** Allows us to quickly build a way to interact with our chatbot without getting bogged down in complex frontend development.
* **Key Concepts:**
    * **App Script:** A Streamlit app is just a Python script.
    * **Widgets:** UI elements like `st.text_input()`, `st.button()`, `st.write()`.
    * **State Management (Implicit):** Streamlit re-runs your script from top to bottom when a user interacts with a widget, making it easy to manage simple app states. For more complex state (like conversation history), Streamlit offers `st.session_state`.

**2. Installation:**

* **What:** Install the `streamlit` library and `requests` (to make HTTP calls to our FastAPI backend).
* **Why:** `streamlit` provides the UI framework, and `requests` is a standard library for making HTTP requests in Python.
* **Commands (ensure your virtual environment `(venv)` is active):**
    If you don't have `requests` installed already (it's very common, so you might), this will install or update it.
    ```bash
    pip install streamlit requests
    ```
    After installation, remember to update your `requirements.txt`:
    ```bash
    pip freeze > requirements.txt
    git add requirements.txt
    git commit -m "Add streamlit and requests for UI"
    git push origin master
    ```

**3. Designing the Simple UI:**

Our UI will be straightforward:
1.  A title for the application (e.g., "My RAG Chatbot").
2.  A text input box where the user can type their question.
3.  A "Send" button to submit the question.
4.  An area to display the chatbot's response.
5.  (Optional, for a slightly better experience): We can maintain a simple conversation history within the session.

**4. Creating the Streamlit App (`streamlit_app.py`):**

* **File:** Create a new Python file in the root of your project: `rag_chatbot_coeo/streamlit_app.py`.
* **Code:**

```python
# rag_chatbot_coeo/streamlit_app.py

import streamlit as st
import requests
import json # For parsing JSON response if necessary

# Configuration for the FastAPI backend
# This should match the address where your FastAPI app is running.
FASTAPI_BACKEND_URL = "http://127.0.0.1:8000/chat/" 

# --- UI Setup ---
st.set_page_config(page_title="My RAG Chatbot", layout="wide")
st.title("💬 My RAG Chatbot")
st.caption("Ask questions and get answers from the local RAG-powered AI!")

# --- Initialize Conversation History in Session State ---
# Streamlit's session_state allows us to preserve variables across reruns (user interactions)
if "messages" not in st.session_state:
    st.session_state.messages = [] # List to store {'role': 'user'/'assistant', 'content': 'message'}

# --- Display Existing Messages ---
# Loop through the messages in session_state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]): # 'user' or 'assistant'
        st.markdown(message["content"])

# --- User Input Handling ---
# `st.chat_input` provides a specialized input field at the bottom of the app
user_query = st.chat_input("Ask your question here:")

if user_query:
    # 1. Add user's message to history and display it
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Get chatbot's response
    try:
        # Display a spinner while waiting for the backend
        with st.spinner("Thinking..."):
            payload = {"query": user_query}
            response = requests.post(FASTAPI_BACKEND_URL, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
            response_data = response.json() # Parse JSON response
            bot_answer = response_data.get("answer", "Sorry, I couldn't get a proper answer.")

        # 3. Add chatbot's response to history and display it
        st.session_state.messages.append({"role": "assistant", "content": bot_answer})
        with st.chat_message("assistant"):
            st.markdown(bot_answer)

    except requests.exceptions.RequestException as e:
        error_message = f"Error connecting to the chatbot API: {e}"
        st.error(error_message)
        # Add error to chat so user sees it
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"): # Display error in assistant's bubble
            st.error(error_message) # Using st.error for visual distinction
            
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"):
             st.error(error_message)
```

**Explanation of `streamlit_app.py`:**

* **`import streamlit as st`**: Standard alias for Streamlit.
* **`import requests`**: To make HTTP POST requests to our FastAPI backend.
* **`FASTAPI_BACKEND_URL`**: The URL where your FastAPI `/chat/` endpoint is running. Make sure this matches.
* **`st.set_page_config(...)`**: Sets browser tab title and layout.
* **`st.title(...)` and `st.caption(...)`**: Display a title and a small caption.
* **Session State for Messages (`st.session_state.messages`)**:
    * Streamlit re-runs the script on every interaction. To remember things like conversation history, we use `st.session_state`.
    * We initialize `st.session_state.messages` as an empty list if it doesn't exist. This list will store dictionaries, each representing a message with a `role` (`user` or `assistant`) and `content`.
* **Displaying Past Messages**: The script iterates through `st.session_state.messages` and uses `st.chat_message(role)` to display each message in a chat-like format.
* **`user_query = st.chat_input(...)`**: This creates a text input field specifically designed for chat applications. It's usually fixed at the bottom of the screen. When the user types something and hits Enter, the script re-runs, and `user_query` will contain the typed text.
* **`if user_query:` block**: This code runs only if the user has submitted a query.
    * The user's query is added to `st.session_state.messages` and displayed.
    * A `POST` request is made to your FastAPI backend using `requests.post()`. The user's query is sent as JSON in the request body.
    * `response.raise_for_status()`: This is important for catching HTTP errors (like 404 Not Found, 500 Internal Server Error, etc.) from the backend.
    * The JSON response from the backend is parsed, and the `answer` field is extracted.
    * The chatbot's answer is then added to `st.session_state.messages` and displayed.
    * **Error Handling**: Includes `try-except` blocks to catch issues like connection errors to the backend API or other unexpected problems, displaying an error message in the UI.
* **`st.spinner("Thinking...")`**: Provides visual feedback to the user while the app is waiting for the backend to respond.

**5. Running the Streamlit App:**

* **What:** Use the `streamlit run` command to start your Streamlit web application.
* **Important Pre-requisites:**
    1.  **FastAPI Backend Must Be Running:** Your FastAPI application (from Phase 5, using `uvicorn app.main:app --reload`) must be running in a separate terminal. The Streamlit UI needs to connect to it.
    2.  **Ollama Server Must Be Running:** And your chosen LLM model must be available to Ollama, as the FastAPI backend relies on it.
    3.  **Virtual Environment Active:** Ensure your `(venv)` is active in the terminal where you run Streamlit.
* **Command (run from the root of your project, `rag_chatbot_coeo/`):**
    ```bash
    streamlit run streamlit_app.py
    ```
    Streamlit will typically open a new tab in your default web browser automatically, pointing to an address like `http://localhost:8501`. Your terminal will also display the local URL and network URL.

**6. Interaction:**

1.  Open the Streamlit app URL in your browser (e.g., `http://localhost:8501`).
2.  You should see the title and the chat input field at the bottom.
3.  Type a question into the input field and press Enter or click the send icon.
4.  You should see your question appear, then a "Thinking..." spinner, and finally, the chatbot's response should appear.
5.  The conversation will build up on the screen.

**7. Alternatives to Streamlit:**

* **Basic HTML/JavaScript Frontend:** More flexible and customizable, but requires knowledge of HTML, CSS, and JavaScript, and significantly more effort to build and connect to the backend.
* **Other Python UI Frameworks:**
    * **Gradio:** Similar to Streamlit, also good for quickly creating UIs for ML models.
    * **Dash (by Plotly):** More powerful for building complex analytical dashboards, can be overkill for a simple chat UI.
* **No UI / API-Only:** For many backend projects or MLOps pipelines, a UI might not be necessary. Interaction could be purely through the API using tools like Postman, `curl`, or other programmatic clients.

---

This concludes Phase 6. You now have a simple but functional web interface to chat with your RAG application! This makes demonstrating and testing your chatbot much more user-friendly.

**Key Takeaways:**
* Streamlit allows for very rapid UI development for Python applications.
* `st.session_state` is key for maintaining state (like conversation history) across user interactions in Streamlit.
* The UI (Streamlit) and the backend (FastAPI) are separate processes that communicate over HTTP. They must both be running.
