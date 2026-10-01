import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
from io import StringIO

# Streamlit Page Config
st.set_page_config(page_title="Plumbing List OCR to Excel", layout="centered")

st.title("🔧 Gujarati Plumbing Notes to Excel Converter")
st.write("Upload your handwritten Gujarati plumbing note, and AI will convert it into a structured Excel file.")

# 1. API Key Input (Securely input your Gemini API Key)
api_key = st.text_input("Enter your Google Gemini API Key:", type="password")

# 2. File Uploader Component
uploaded_file = st.file_uploader("Choose an image of your notes...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Note", use_column_width=True)
    
    if st.button("Convert to Excel"):
        if not api_key:
            st.error("Please enter your Gemini API Key first!")
        else:
            with st.spinner("Reading Gujarati handwriting and translating... Please wait."):
                try:
                    # Configure Gemini API
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    # Prompt for structural extraction
                    prompt = """
                    You are an expert procurement assistant specializing in plumbing hardware (PVC and UPVC fittings).
                    Analyze this handwritten note (which is in Gujarati mixed with numbers). 
                    Translate all item names into clear English.
                    Extract every single line item and format it strictly as a CSV with the following 4 columns:
                    PVC_UPVC,Item,Size,QTY
                    
                    Rules:
                    - PVC_UPVC: Specify if it is PVC or UPVC.
                    - Item: Translate to English (e.g., Pipe, Elbow, Tee, Coupler, Reducer, Solution, etc.).
                    - Size: Extract the size (e.g., 4", 1", 0.5", 2.5", etc.).
                    - QTY: Extract quantity with units (e.g., 80 Feet, 15 Nos, 1 Kg, etc.).
                    
                    Return ONLY raw CSV data with headers. Do not include markdown ticks like ```csv.
                    """

                    # Generate content using Gemini Vision
                    response = model.generate_content([prompt, image])
                    raw_text = response.text.replace("```csv", "").replace("```", "").strip()

                    # Convert CSV text to Pandas DataFrame
                    df = pd.read_csv(StringIO(raw_text))

                    # Convert DataFrame to Excel bytes for download
                    output_file = "Plumbing_List.xlsx"
                    df.to_excel(output_file, index=False)

                    st.success("Conversion successful!")
                    
                    # Show preview table in UI
                    st.subheader("Extracted Data Preview:")
                    st.dataframe(df)

                    # Download Button
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel File",
                            data=f,
                            file_name="Plumbing_List.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.text("Raw AI Response (for debugging):")
                    st.text(response.text if 'response' in locals() else "No response generated.")