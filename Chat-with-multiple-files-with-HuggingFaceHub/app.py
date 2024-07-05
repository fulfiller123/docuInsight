import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
import docx  # Library to handle .docx files
import moviepy.editor as mp  # Library to handle video files
import openai
import pandas as pd  # Library to handle Excel and CSV files
import chromadb
import tiktoken

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Placeholder CSS and HTML templates for bot and user messages
css = '''
<style>
body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
header {
    background-color: #ffffff;
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
    padding: 1rem;
    border-right: 1px solid #e0e0e0;
}
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.chat-input {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    background-color: #f1f1f1;
    border-radius: 50px;
}
.chat-input input {
    flex-grow: 1;
    border: none;
    outline: none;
    background: transparent;
    padding: 0.5rem;
    font-size: 1rem;
    border-radius: 25px;
}
.chat-input button {
    border: none;
    background: #6200ee;
    color: #ffffff;
    padding: 0.5rem 1rem;
    border-radius: 50px;
    cursor: pointer;
    transition: background 0.3s ease;
    margin-left: 10px;
}
.chat-input button:hover {
    background: #4500b5;
}
.chat-message {
    display: flex;
    align-items: flex-start;
    margin-bottom: 1rem;
    width: 100%;
}
.chat-message.user {
    justify-content: flex-end;
}
.chat-message.bot {
    justify-content: flex-start;
}
.chat-message .message {
    max-width: 70%;
    padding: 1rem;
    border-radius: 10px;
    background-color: #f8f8f8;  /* Off-white background */
    color: #000000;  /* Black font color */
    text-align: justify;
}
.chat-message .avatar {
    margin: 0 1rem;
}
.chat-message.user .avatar {
    order: 2;
}
.chat-message.bot .avatar {
    order: 1;
}
.chat-message .avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}
.file-list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.file-list-item button {
    background-color: transparent;
    border: none;
    color: #ff4d4d;
    cursor: pointer;
    font-size: 1rem;
}
.file-list-item button:hover {
    color: #ff1a1a;
}
.pagination {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
}
.pagination button {
    background-color: #6200ee;
    color: #ffffff;
    border: none;
    border-radius: 50px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    transition: background 0.3s ease;
    margin: 0 0.5rem;
}
.pagination button:hover {
    background-color: #4500b5;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="images/bot-ai.png" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/rdZC7LZ/Photo-logo-1.png" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_docx_text(docx_docs):
    text = ""
    for docx_file in docx_docs:
        doc = docx.Document(docx_file)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    return text

def get_txt_text(txt_docs):
    text = ""
    for txt_file in txt_docs:
        text += txt_file.read().decode("utf-8") + "\n"
    return text

def get_video_text(video_files):
    text = ""
    for video_file in video_files:
        # Extract audio from video
        video = mp.VideoFileClip(video_file)
        audio_path = "temp_audio.wav"
        video.audio.write_audiofile(audio_path)

        # Transcribe audio using OpenAI's Whisper
        with open(audio_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe("whisper-1", audio_file)
            text += transcription["text"] + "\n"
        
        # Clean up temporary audio file
        os.remove(audio_path)
    return text

def get_excel_text(excel_docs):
    text = ""
    for excel_file in excel_docs:
        df = pd.read_excel(excel_file)
        text += df.to_string(index=False) + "\n"
    return text

def get_csv_text(csv_docs):
    text = ""
    for csv_file in csv_docs:
        df = pd.read_csv(csv_file)
        text += df.to_string(index=False) + "\n"
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = OpenAI(api_key=openai_api_key)
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    if st.session_state.conversation:
        if not st.session_state.chat_history or user_question != st.session_state.chat_history[-1]['content']:
            response = st.session_state.conversation({'question': user_question})
            st.session_state.chat_history.append({'content': user_question, 'sender': 'user'})
            
            # Ensure response is appended only once
            if response and response.get('answer'):
                st.session_state.chat_history.append({'content': response['answer'], 'sender': 'bot'})

    # Display chat history
    st.markdown('<div class="chat-container"><div id="chat-history">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message['sender'] == 'user':
            st.markdown(user_template.replace("{{MSG}}", message['content']), unsafe_allow_html=True)
        else:
            st.markdown(bot_template.replace("{{MSG}}", message['content']), unsafe_allow_html=True)
            if "dataframe" in message['content']:
                df = pd.read_json(message['content'].replace("dataframe:", "").strip())
                st.table(df)
            elif "chart" in message['content']:
                chart_data = pd.read_json(message['content'].replace("chart:", "").strip())
                st.line_chart(chart_data)
    st.markdown('</div></div>', unsafe_allow_html=True)

def delete_file(folder, file):
    os.remove(os.path.join(folder, file))
    st.success(f"Deleted {file}")

def process_file(file_path):
    raw_text = ""
    if file_path.endswith('.pdf'):
        raw_text += get_pdf_text([file_path])
    elif file_path.endswith('.docx'):
        raw_text += get_docx_text([file_path])
    elif file_path.endswith('.txt'):
        raw_text += get_txt_text([file_path])
    elif file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raw_text += get_video_text([file_path])
    elif file_path.endswith('.xlsx'):
        raw_text += get_excel_text([file_path])
    elif file_path.endswith('.csv'):
        raw_text += get_csv_text([file_path])
    
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    st.session_state.conversation = get_conversation_chain(vectorstore)

def main():
    st.set_page_config(page_title="Analyse your data",
                       page_icon=":books:")
    st.markdown(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "page" not in st.session_state:
        st.session_state.page = 0

    st.sidebar.header("DOCUINSIGHT AI")
    
    st.header("Analyse your data")

    with st.form(key='user_input_form', clear_on_submit=True):
        user_input_col, submit_button_col = st.columns([4, 1])
        with user_input_col:
            user_question = st.text_input("Your message:", key='user_input', placeholder="Type your message here...", label_visibility="collapsed")
        with submit_button_col:
            submit_button = st.form_submit_button(label="Submit", use_container_width=True)

    if submit_button and user_question:
        handle_userinput(user_question)

    st.markdown("""
        <div class="chat-container">
            <div id="chat-history">
    """, unsafe_allow_html=True)

    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message['sender'] == 'user':
                st.markdown(user_template.replace("{{MSG}}", message['content']), unsafe_allow_html=True)
            else:
                st.markdown(bot_template.replace("{{MSG}}", message['content']), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Your documents")
        st.text_input("Enter folder name:", key="folder_name")
        create_folder_button = st.button("Create Folder")
        if create_folder_button:
            folder_name = st.session_state.folder_name
            if folder_name and not os.path.exists(folder_name):
                os.makedirs(folder_name)
                st.success(f"Folder '{folder_name}' created.")
            elif folder_name:
                st.warning(f"Folder '{folder_name}' already exists.")
            else:
                st.error("Folder name cannot be empty.")
        
        created_folders = [d for d in os.listdir() if os.path.isdir(d) and d not in ['__pycache__', 'images']]
        selected_folder = st.selectbox("Select folder to upload files to:", options=created_folders, key="selected_folder")

        if selected_folder:
            st.markdown(f"### Files in {selected_folder}")
            files_in_folder = os.listdir(selected_folder)
            num_files = len(files_in_folder)
            files_per_page = 10
            num_pages = (num_files // files_per_page) + (1 if num_files % files_per_page > 0 else 0)
            
            page = st.session_state.page

            if num_files > 0:
                start_idx = page * files_per_page
                end_idx = min(start_idx + files_per_page, num_files)
                for file in files_in_folder[start_idx:end_idx]:
                    file_path = os.path.join(selected_folder, file)
                    col1, col2 = st.columns([8, 1])
                    with col1:
                        if st.checkbox(file, key=file_path, on_change=process_file, args=(file_path,)):
                            pass
                    with col2:
                        if st.button("🗑️", key=f"delete_{file}"):
                            delete_file(selected_folder, file)
                            st.experimental_rerun()
                
                st.markdown("<div class='pagination'>", unsafe_allow_html=True)
                if page > 0:
                    if st.button("Previous Page"):
                        st.session_state.page -= 1
                        st.experimental_rerun()
                if page < num_pages - 1:
                    if st.button("Next Page"):
                        st.session_state.page += 1
                        st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("No files in this folder.")
            
            st.subheader("Upload your documents")
            uploaded_files = st.file_uploader(
                "Upload your documents here", accept_multiple_files=True, type=['pdf', 'docx', 'txt', 'mp4', 'avi', 'mov', 'mkv', 'xlsx', 'csv'])

            if st.button("Upload Files"):
                if uploaded_files and selected_folder:
                    for uploaded_file in uploaded_files:
                        with open(os.path.join(selected_folder, uploaded_file.name), "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    st.success("Files uploaded successfully.")
                else:
                    st.error("Please select a folder and upload files.")

if __name__ == '__main__':
    main()
