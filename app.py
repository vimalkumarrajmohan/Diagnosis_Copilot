import os
import io
import re
import sys
import yaml
import pandas as pd
from PIL import Image
import streamlit as st


from crew import DiagnosisCrew
from dotenv import load_dotenv
from streamlit_chat import message
from agents import StreamToExpander

result = None
load_dotenv()

st.set_page_config(page_title = "Diagnosis Copilot",
                   layout = "wide",
                   initial_sidebar_state = "expanded")

st.title("Diagnosis Copilot")


if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = {}
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None
if "selected_file_name" not in st.session_state:
    st.session_state.selected_file_name = ''
if "metadata" not in st.session_state:
    st.session_state.metadata = ''
if "messages" not in st.session_state:
    st.session_state.messages = []


def generate_metadata(path, sample_size=3):

    df = pd.read_csv(path)

    metadata = {'Number of columns': df.shape[1],
                'Column names': list(df.columns),
                'Column datatype': {col: str(df[col].dtype) for col in df.columns},
                'Column description': {},
                'Sample data': df.head(sample_size).to_dict(orient='records')}

    for col in df.columns:
        unique_values = df[col].dropna().unique()
        col_metadata = {'data_type': str(df[col].dtype),
                        'description': f'{col} column in the dataset'}

        if df[col].dtype.kind not in ['i', 'f']:  # Non-numeric types
            if len(unique_values) <= 10:
                col_metadata['column_values'] = list(unique_values)
            else:
                col_metadata['column_values'] = 'Categorical values'
        else:
            col_metadata['column_values'] = 'Continuous values'

        metadata['Column description'][col] = col_metadata

    return metadata




with st.sidebar:
    st.header("Upload and Display CSV File")
    uploaded_files = st.file_uploader("Upload CSV Files", accept_multiple_files=True, type=['csv'])

    if uploaded_files:
        selected_file_name = st.selectbox("Select a CSV file", options=[file.name for file in uploaded_files])
        selected_file = next((file for file in uploaded_files if file.name == selected_file_name), None)

        if selected_file:
            save_path = os.path.join(os.getcwd(), selected_file_name)
            with open(save_path, "wb") as f:
                f.write(selected_file.getbuffer())
        
        st.success(f"File saved successfully: {save_path}")
        if st.button("Select File"):
            for file in uploaded_files:
                if file.name == selected_file_name:
                    st.session_state['selected_file_name'] = file.name
                    st.session_state['selected_file'] = pd.read_csv(file)
                    st.success(f"Loaded file: {selected_file_name}")

        if st.session_state['selected_file'] is not None:
            st.dataframe(st.session_state['selected_file'])

            if st.session_state['metadata'] is not None:
                st.write("Metadata")
                st.session_state['metadata'] = generate_metadata(selected_file_name)
                st.write(st.session_state['metadata'])

    if st.button("Clear Cache", key="clear_cache"):
        st.session_state.clear()




if st.session_state['messages'] is not None and uploaded_files and st.session_state['selected_file'] is not None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "image":
                st.image(message["content"], caption="Output Image", use_container_width=True)
            elif message["type"] == "dataframe":
                st.dataframe(message["content"])
            else:
                st.markdown(message["content"])
            # if message["content"].strip() == "output.png":
            #     image = Image.open("output.png")
            #     st.image(image, caption="Output Image", use_container_width=True)
            # elif message["content"].strip() == "output.csv":
            #     df = pd.read_csv("output.csv")
            #     st.dataframe(df)
            # else:
            #     st.markdown(message["content"])
            st.markdown(message["codes"])

    if prompt := st.chat_input("Ask Anything"):
        st.session_state.messages.append({"role": "user",
                                            "content": prompt,
                                            "codes": '',
                                            "type": ''})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            diagnosis_crew = DiagnosisCrew(query = prompt,
                                            metadata = st.session_state['metadata'], 
                                            csv_path = st.session_state['selected_file_name'])
            response = diagnosis_crew.run()

            try:
                code_response = response.raw
                code_pattern = r"```python\n(.*?)```"
                match = re.search(code_pattern, code_response, re.DOTALL)
                if match:
                    code = match.group(1)
                    output_buffer = io.StringIO()
                    sys.stdout = output_buffer
                    exec(code)
                    sys.stdout = sys.__stdout__
                    code_result = output_buffer.getvalue()
                else:
                    code_result = "Error!!.. Retry Once Again"

                if code_result.strip() == "output.png":
                    image = Image.open("output.png")
                    code_result = image
                    st.image(image, caption="Output Image", use_container_width = True)
                    type = "image"
                elif code_result.strip() == "output.csv":
                    df = pd.read_csv("output.csv")
                    code_result = df
                    st.dataframe(df)
                    type = "dataframe"
                else:
                    st.markdown(code_result)
                    type = "text"
                st.markdown(code_response)

            except Exception as e:
                code_result = str(e)
                st.markdown(code_result)
                code_result = "Error!!.. Retry Once Again"
                code_response = ''
                type = "text"

        st.session_state.messages.append({"role": "assistant", 
                                            "content": code_result,
                                            "codes": code_response,
                                            "type": type})

