import streamlit as st
from groq import Groq
import pandas as pd
import os

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Dataset Analyzer",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# 2. GROQ API CONFIGURATION
# =====================================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)

except (KeyError, FileNotFoundError):
    st.error(
        "Groq API key not found. "
        "Please configure .streamlit/secrets.toml"
    )
    st.stop()


# =====================================================
# 3. APPLICATION HEADER
# =====================================================

left_co, cent_co, right_co = st.columns([1, 1, 1])

with cent_co:
    if os.path.exists("logo.png"):
        st.image(
            "logo.png",
            caption="AI AGENTS",
            use_container_width=True
        )

st.title("🤖 AI Dataset Analyzer")

st.write(
    "Upload your dataset, provide instructions, "
    "and let your AI Agent analyze your data."
)

st.divider()


# =====================================================
# 4. USER INFORMATION
# =====================================================

nm = st.sidebar.text_input("Enter your Name:")

if nm:
    st.sidebar.success(f"Have a nice day, {nm}!")


# =====================================================
# 5. DATASET UPLOAD
# =====================================================

st.subheader("📂 Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Choose an Excel or CSV file",
    type=["xlsx", "xls", "csv"]
)

dataset = None
act_data = None

if uploaded_file is not None:

    try:

        if uploaded_file.name.lower().endswith(".csv"):

            act_data = pd.read_csv(uploaded_file)

        else:

            excel_file = pd.ExcelFile(uploaded_file)

            src_data = st.selectbox(
                "Select an Excel Sheet:",
                excel_file.sheet_names
            )

            act_data = pd.read_excel(
                uploaded_file,
                sheet_name=src_data
            )

        dataset = act_data

        st.success("Dataset uploaded successfully!")

        # ---------------------------------------------
        # DATASET PREVIEW
        # ---------------------------------------------

        st.subheader("📊 Dataset Preview")

        st.dataframe(
            act_data.head(100),
            use_container_width=True
        )

        # ---------------------------------------------
        # DATASET INFORMATION
        # ---------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Rows", act_data.shape[0])

        with col2:
            st.metric("Total Columns", act_data.shape[1])

        with col3:
            st.metric(
                "Missing Values",
                int(act_data.isnull().sum().sum())
            )

    except Exception as e:

        st.error(f"Error reading file: {e}")
        st.stop()


# =====================================================
# 6. USER INSTRUCTIONS
# =====================================================

st.divider()

st.subheader("📝 Give Instructions to Your AI Agent")

instruction = st.text_area(
    "What would you like the AI Agent to do?",
    placeholder=(
        "Example: Analyze this dataset, summarize it, "
        "identify important trends, find missing values "
        "and provide useful business insights."
    ),
    height=150
)


# =====================================================
# 7. AI AGENT EXECUTION
# =====================================================

if st.button("🚀 Execute Task", type="primary"):

    if uploaded_file is None:

        st.warning("Please upload a dataset first!")

    elif dataset is None:

        st.warning("Unable to read the uploaded dataset.")

    elif not instruction.strip():

        st.warning("Please provide an instruction!")

    else:

        try:

            with st.spinner(
                "🤖 AI Agent is analyzing your dataset..."
            ):

                # -------------------------------------
                # CONVERT DATASET INTO TEXT
                # -------------------------------------

                dataset_text = dataset.to_csv(index=False)

                # -------------------------------------
                # DATASET SIZE CHECK
                # -------------------------------------

                max_chars = 50000

                if len(dataset_text) > max_chars:

                    dataset_text = dataset_text[:max_chars]

                    st.warning(
                        "Large dataset detected. "
                        "Only the first portion of the dataset "
                        "will be sent to the AI model."
                    )

                # -------------------------------------
                # GROQ API REQUEST
                # -------------------------------------

                response = client.chat.completions.create(

                    model="openai/gpt-oss-120b",

                    messages=[

                        {
                            "role": "system",

                            "content": """
You are an expert Data Analyst AI Agent.

Your job is to analyze the dataset according
to the user's instructions.

Analyze the actual data and provide meaningful
insights instead of simply repeating the dataset.

Depending on the user's instructions, provide:

1. Dataset summary.
2. Important observations.
3. Trends and patterns.
4. Statistical insights.
5. Missing value analysis.
6. Anomalies and unusual observations.
7. Business insights.
8. Conclusions and recommendations.

Important rules:

- Use only the provided dataset for data-related findings.
- Never invent statistics or values.
- Clearly mention if the available data is insufficient.
- Explain your findings in simple language.
- Follow the user's instructions carefully.
- Use Markdown formatting for your response.
                            """
                        },

                        {
                            "role": "user",

                            "content": f"""
USER INSTRUCTION:

{instruction}


DATASET:

{dataset_text}
                            """
                        }

                    ],

                    temperature=0.3,

                    max_tokens=3000

                )

                # -------------------------------------
                # EXTRACT AI RESPONSE
                # -------------------------------------

                result = response.choices[0].message.content

            # -----------------------------------------
            # DISPLAY RESULT
            # -----------------------------------------

            st.success("Dataset Analysis Completed Successfully!")

            st.divider()

            st.subheader("🤖 AI Agent Analysis")

            st.markdown(result)

        except Exception as e:

            st.error(f"An error occurred: {e}")


# =====================================================
# 8. FOOTER
# =====================================================

st.divider()

st.caption(
    "AI Dataset Analyzer | Powered by Streamlit, "
    "Pandas and Groq API"
)