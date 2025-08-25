import os
import streamlit as st

st.set_page_config(page_title="Healthcheck", layout="centered")

st.title("Streamlit Healthcheck")

st.write("If you can see this page in your browser, Streamlit is working.")

st.info(
    "Reporting uses metric tonnes (t) for display; source data remains in lbs. "
    "Ensure conversions occur at render time."
)

# Show environment context helpful for debugging
st.subheader("Environment")
col1, col2 = st.columns(2)
with col1:
    st.write("Python:", os.getenv("PYTHON_VERSION", "unknown"))
    st.write("Streamlit version:")
    try:
        import streamlit
        st.code(streamlit.__version__)
    except Exception as e:
        st.error(f"Cannot read Streamlit version: {e}")
with col2:
    st.write("Working Directory:")
    st.code(os.getcwd())

st.success("Healthcheck app loaded.")

