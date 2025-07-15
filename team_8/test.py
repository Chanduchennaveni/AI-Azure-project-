import streamlit as st

st.title("Streamlit is working!")
uploaded_file = st.file_uploader("Upload a file")
if uploaded_file:
    st.write("File uploaded:", uploaded_file.name)
