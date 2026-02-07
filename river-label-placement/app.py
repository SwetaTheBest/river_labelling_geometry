import streamlit as st
from src.label_placement import place_river_label

st.set_page_config(
    page_title="River Label Placement Demo",
    layout="centered"
)

st.title("Cartographic River Label Placement")
st.write(
    "Upload a WKT file (river or any polygon) to visualize "
    "automatic, cartographically correct label placement."
)

uploaded_file = st.file_uploader(
    "Upload a .wkt file",
    type=["wkt", "txt"]
)

if uploaded_file is not None:
    try:
        wkt_text = uploaded_file.read().decode("utf-8")

        with st.spinner("Placing label..."):
            fig = place_river_label(wkt_text)

        st.pyplot(fig)

    except Exception as e:
        st.error("Failed to process the WKT file.")
        st.exception(e)
