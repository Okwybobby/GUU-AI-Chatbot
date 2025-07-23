import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import random

# With this:
import os
api_key = st.secrets["api_key"]


# Expanded FAQ as a single string (20+ Q&A)
FAQ_LIST = [
    ("What are the accomodations options?", "Gregory University offers on-campus accommodations."),
    ("Is the accomodations guaranteed, especially for first year students?", "The accommodations for students are guaranteed as long as part or full payment of school fees has been made."),
    ("Is there a gym or recreational facilities?", "Yes, Gregory University has a gym for its students."),
    ("What is the process for confirming receipts of payment?", "Payment of fees are confirmed from the bursar's office. After payment is made, send your receipt to the bursar for confirmation."),
    ("How do I go about payment of fees?", "You will be given the school account details and school fees amount."),
    ("Can I pay school fees in part?", "Yes, in Gregory University you can pay at least 75% of your school fees for them to resume."),
    ("Where is the university located?", "Gregory University Uturu is a private university located in Uturu, Abia State, Nigeria. It was established to provide quality education in various fields."),
    ("What are the applications deadlines?", "Application deadline varies from year to year. For detailed information, visit the school's admission page."),
    ("What academic programs are offered?", "GUU offers a wide range of undergraduate programs in areas such as Medicine, Law, Engineering, Arts, Humanities, Agriculture, Education, Mass Communications, Business Administration, Computer Science, and more. Additionally, we offer postgraduate programs across various disciplines, including science, arts, business, and technology. You can find a comprehensive list on our Department page."),
    ("How accessible are faculty and staff?", "The faculty and staff are always available from 9 to 5 during the weekdays."),
    ("What is the grading system?", "GUU like other Nigerian universities use the first class, second class upper, second class lower and third class for grading its scholars."),
    ("Can you obtain a bachelor's and master's degree at the same time?", "No, you can only obtain them one at a time."),
    ("What is the motto of Gregory University?", "The motto of Gregory University is 'Knowledge for Tomorrow'."),
    ("When was Gregory University established?", "Gregory University was established in 2012."),
    ("Who is the founder of Gregory University?", "The founder of Gregory University is Professor Gregory Ibe."),
    ("Is Gregory University a public or private institution?", "Gregory University is a private university."),
    ("What are some of the colleges at Gregory University?", "Gregory University has colleges including Medicine and Health Sciences, Law, Engineering, Agriculture, Environmental Sciences, Humanities, Natural and Applied Sciences, and Social and Management Sciences."),
    ("Does Gregory University offer postgraduate programs?", "Yes, Gregory University offers both undergraduate and postgraduate programs."),
    ("What is the admission policy of Gregory University?", "Gregory University has a selective admission policy based on entrance examinations."),
    ("Are international students welcome at Gregory University?", "Yes, international students are welcome to apply for admission at Gregory University."),
    ("What is the religious affiliation of Gregory University?", "Gregory University is affiliated with the Christian-Catholic religion."),
    ("What is the size of the student population at Gregory University?", "Gregory University has over 2,000 students."),
    ("What are some of the departments at Gregory University?", "Departments include Medicine and Surgery, Law, Engineering, Computer Science, Business Administration, Mass Communication, and many more."),
    ("What is the university’s ranking in Nigeria?", "Gregory University is ranked 94th in Nigeria according to uniRank 2024."),
]

# Convert to FAQ_TEXT for Gemini context
FAQ_TEXT = "Gregory University FAQ:\n\n"
for i, (q, a) in enumerate(FAQ_LIST, 1):
    FAQ_TEXT += f"Q{i}: {q}\nA{i}: {a}\n\n"

# System instruction for Gemini
system_instruction = (
    "You are a helpful assistant for Gregory University. "
    "Only answer questions using the following FAQ. "
    "If the answer is not in the FAQ, say 'Sorry, I can only answer questions from the official FAQ.'\n\n"
    + FAQ_TEXT
)

# Title
st.title("🤖 Gregory University FAQ Chatbot")
st.markdown("Chat with Gregory University's AI model, restricted to the official FAQ.")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input(
        "Enter your Gemini API Key:",
        value=api_key,
        type="password",
        help="Get your API key from https://aistudio.google.com/app/apikey"
    )
    model_name = st.selectbox(
        "Select Model:",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )
    st.markdown("---")
    st.header("Sample FAQ Questions")
    # Show only 5 random questions each time
    for q, _ in random.sample(FAQ_LIST, 5):
        st.markdown(f"- {q}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.caption(f"*{message['timestamp']}*")

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar to start chatting.")
        st.stop()
    
    # Add user message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": timestamp
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"*{timestamp}*")
    
    # Generate AI response
    with st.chat_message("assistant"):
        try:
            # Prepare conversation history with system instruction and FAQ
            contents = [
                {
                    "role": "user",
                    "parts": [{"text": system_instruction}]
                }
            ]
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

            # Initialize client
            client = genai.Client(api_key=api_key)
            
            # Stream the response
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    temperature=1,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            
            # Display streaming response
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            # Final response without cursor
            response_placeholder.markdown(full_response)
            
            # Add timestamp
            response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"*{response_timestamp}*")
            
            # Save to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "timestamp": response_timestamp
            })
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Please check your API key and try again.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center'>"
    "<p><small>Get your free API key at "
    "<a href='https://aistudio.google.com/app/apikey' target='_blank'>Google AI Studio</a></small></p>"
    "</div>", 
    unsafe_allow_html=True
)