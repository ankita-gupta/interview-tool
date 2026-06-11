import streamlit as st
# from dotenv import load_dotenv
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval
import os
# load_dotenv()

st.title('Chatbot')
st.subheader('Personal Information', divider='rainbow')

if 'setup_complete' not in st.session_state:
    st.session_state['setup_complete'] = False
if 'user_message_count' not in st.session_state:
    st.session_state['user_message_count'] = 0
if 'feedback_shown' not in st.session_state:
    st.session_state['feedback_shown'] = False
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'chat_complete' not in st.session_state:
    st.session_state['chat_complete'] = False

def show_feedback():
    st.session_state['feedback_shown'] =True
def setupComplete():
    st.session_state['setup_complete'] = True
if not st.session_state['setup_complete']:
    if 'name' not in st.session_state:
        st.session_state['name']= ""
    if 'experience' not in st.session_state:
        st.session_state['experience']= ""
    if 'skills' not in st.session_state:
        st.session_state['skills']= ""
    st.session_state['name'] = st.text_input(label="Name", max_chars=40,value=st.session_state['name'], placeholder="Enter your name")
    st.session_state['experience'] = st.text_area(label="Experience", max_chars=200,value=st.session_state['experience'], placeholder="Enter your experience")
    st.session_state['skills'] = st.text_area(label="Skills", max_chars=200, value=st.session_state['skills'],placeholder="Enter your Skills")

    st.write(f'**Your Name:** {st.session_state['name']}')
    st.write(f'**Your Experience:** {st.session_state['experience']}')
    st.write(f'**Your Skills:** {st.session_state['skills']}')

    st.subheader('Company and Position', divider='rainbow')
    if 'level' not in st.session_state:
        st.session_state['level']= "Junior"
    if 'position' not in st.session_state:
        st.session_state['position']= "Data Scientist"
    if 'company' not in st.session_state:
        st.session_state['company']= "Amazon"
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['level']=st.radio("Choose level",key='visibility',options=["Junior","Mid-Level","Senior"])
    with col2:
        st.session_state['position']=st.selectbox("Select a position",options=("Technical Lead","Data Scientist","Data Engineer", "ML Engineer","BI Analyst","Financial Analyst"))

    st.session_state['company'] = st.selectbox("Choose a company",options=("Amazon","Meta","Google","Infosys","Udemy","LinkedIn","Spotify"))

    st.write(f'**Your Information:** {st.session_state['level']} {st.session_state['position']} at {st.session_state['company']}')
    if st.button('Start Interview', on_click=setupComplete):
        st.write('Setup complete. Starting Interview...')

if st.session_state.setup_complete and not st.session_state['feedback_shown'] and not st.session_state['chat_complete']:
    st.info('Start by introducing yourself')
    client =OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    if 'openai_model' not in st.session_state:
        st.session_state['openai_model']= 'gpt-4o-mini'

    if not st.session_state['messages']:
        st.session_state['messages'] = [{'role':'system','content':f'You are an HR executive that interviews an interviewee called {st.session_state['name']} with experience {st.session_state['experience']} and skills {st.session_state['skills']}. You should interview them for the position {st.session_state['position']} {st.session_state['level']} at the company {st.session_state['company']}.'}]

    for message in st.session_state.messages:
        if message['role'] != 'system':
            with st.chat_message(message['role']):
                st.markdown(message['content'])
    if st.session_state['user_message_count'] < 5 :
        if prompt := st.chat_input('Your answer:', max_chars=1000):
            st.session_state.messages.append({'role':'user', 'content':prompt})
            with st.chat_message('user'):
                st.markdown(prompt)
            if st.session_state['user_message_count'] < 4:
                with st.chat_message('assistant'):
                    stream = client.responses.create(
                        model=st.session_state.openai_model,
                        input=[{'role':m['role'], 'content':m['content']} for m in st.session_state['messages']],
                        stream=True
                        )
                    def text_generator():
                        for chunk in stream:
                            # The Responses API streams text updates under delta or text properties
                            if hasattr(chunk, "text") and chunk.text:
                                yield chunk.text
                    response = st.write_stream(text_generator())
                st.session_state.messages.append({'role':'assistant', 'content':response})

            st.session_state['user_message_count'] += 1

    if st.session_state['user_message_count'] >= 5:
        st.session_state['chat_complete'] = True

if not st.session_state.feedback_shown and st.session_state.chat_complete:
    if st.button('Get Feedback', on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader('Feedback')
    conversation_history= '\n'.join([f"{m['role']}:{m['content']} "for m in st.session_state.messages])

    feedback_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    feedback_completion = client.responses.create(
        model='gpt-4o-mini',
        input=[{'role':'system', 'content':'''You are a helpful tool that provides feedback on an interview performance.
                Before the feedback give a score of 1 to 10.
                Follow this format:
                Overall score:
                Feedback:
                Give only feedback.Do not ask any additional questions.'''},
                {'role':'user', 'content':f'This is the interview you need to evaluate.Keep in mind that you are only a tool. And you should not engage in any conversation:{conversation_history}'}]
                )
    st.write(feedback_completion.output_text)

    if st.button('Restart Interview', type='primary'):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

#Debate simulator
#with st.chat_message('user'):
#    st.write('Hello there!')

#prompt = st.chat_input('Type your message')
#if prompt:
#   st.write(f'user message:{prompt}')