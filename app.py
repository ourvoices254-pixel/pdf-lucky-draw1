import random
import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(page_title="M-Pesa Lucky Draw Picker", page_icon="🎉", layout="centered")

st.title("🎉 M-Pesa Statement Lucky Draw")
st.write("Upload your M-Pesa statement PDF, pick the column containing your participants (e.g., Names or Details), and choose a winner!")

# File uploader
uploaded_file = st.file_uploader("Upload M-Pesa Statement (PDF)", type=["pdf"])

if uploaded_file is not None:
    @st.cache_data
    def extract_tables_from_pdf(file):
        all_rows = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Clean cells to remove None values or empty strings
                        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                        if any(cleaned_row): # Ignore completely empty rows
                            all_rows.append(cleaned_row)
        return all_rows

    with st.spinner("Reading tables from M-Pesa statement... 📄"):
        raw_data = extract_tables_from_pdf(uploaded_file)

    if raw_data:
        # Assume the first row or a row with text contains headers; fallback to generic column indices if needed
        # Let's clean and structure into a Pandas DataFrame
        df = pd.DataFrame(raw_data)
        
        # Drop rows where everything is empty
        df = df.dropna(how='all')
        
        st.success("PDF tables successfully loaded!")
        
        st.write("### 1. Select the Column with Participants")
        st.write("Preview of your statement structure:")
        st.dataframe(df.head(5), use_container_width=True)

        # Let user choose which column index to target
        column_options = {f"Column {i} (Sample: {df.iloc[1, i] if len(df) > 1 else 'N/A'})": i for i in range(df.shape[1])}
        selected_col_label = st.selectbox("Choose the column that has the names/phone numbers:", options=list(column_options.keys()))
        
        selected_col_index = column_options[selected_col_label]

        # Extract items from that specific column, dropping header/empty fields
        participants = df.iloc[1:, selected_col_index].dropna().tolist()
        # Clean whitespaces and filter out empty strings or typical headers
        participants = [p.strip() for p in participants if p.strip() and not p.lower().startswith("details") and not p.lower().startswith("receipt")]
        
        # Remove duplicates option
        remove_duplicates = st.checkbox("Remove duplicate entries (keep unique names/numbers only)", value=True)
        if remove_duplicates:
            participants = list(dict.fromkeys(participants))

        st.info(f"Total unique entries found in this column: **{len(participants)}**")

        if participants:
            with st.expander("Preview Selected Participants"):
                st.write(participants)

            st.divider()
            if st.button("🎲 Pick a Winner from this Column!", type="primary", use_container_width=True):
                with st.spinner("Spinning the wheel... 🥁"):
                    winner = random.choice(participants)
                
                st.balloons()
                st.markdown(f"""
                ### 🏆 And the winner is...
                # **{winner}**! 🎊
                """)
        else:
            st.warning("No valid entries found in this column. Please try choosing a different column.")

    else:
        st.error("Could not find structured tables in this PDF. Ensure it's a valid text-based M-Pesa statement.")
