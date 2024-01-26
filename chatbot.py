import streamlit as st
import time
from openai import OpenAI
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

assistantID = "asst_83l5JM9MBepz3y8AMbH83ykq"

thread = client.beta.threads.create()

def generateResponse(messageBody):
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=messageBody
    )
    
    newMessage = runAssistant(thread)
    return newMessage
    
def runAssistant(thread):
    assistant = client.beta.assistants.retrieve(assistantID)
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    newMessage = messages.data[0].content[0].text.value
    
    return newMessage

st.title("Dlubal Chatbot | DE")

if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant",
         "content": """Guten Tag! Mein Name ist Mia, Ihr persönlicher KI-Assistent von Dlubal. 
                    Ich bin hier, um Ihre Fragen zur Dlubal Statiksoftware zu beantworten und 
                    Unterstützung bei unseren Softwareprodukten und -lösungen zu bieten."""
                    }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fragen Sie mich etwas über Dlubal Produkte..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    loading_placeholder = st.empty()
    with st.chat_message("assistant"):
        loading_placeholder.status("Bitte warten, ich hole die Antwort...")
        message_placeholder = st.empty()
        full_response = generateResponse(prompt)
        assistant_response = prompt
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        loading_placeholder.empty()
        message_placeholder.markdown(full_response)        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    


