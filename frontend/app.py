import streamlit as st
import requests

# Set up the page layout
st.set_page_config(page_title="Calendar NLP", page_icon="📅")
st.title("📅 Smart Calendar Assistant")
st.write("Type a natural language command to generate a structured API payload.")

# The input box
user_input = st.text_input(
    "Command",
    placeholder="e.g., Schedule a retrospective with Alice next Friday at 3pm",
)

# The submit button
if st.button("Generate JSON"):
    if not user_input.strip():
        st.warning("Please enter a command first.")
    else:
        with st.spinner("Running inference..."):
            try:
                import os
                api_url = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/parse")
                response = requests.post(
                    api_url,
                    json={"command": user_input},
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success("Successfully parsed!")
                    st.json(data["parsed_json"])

                elif response.status_code == 422:
                    # FastAPI wraps HTTPException detail under the "detail" key.
                    # When we raise HTTPException(detail={...}), the shape is:
                    #   {"detail": {"message": "...", "raw_output": "..."}}
                    detail = response.json().get("detail", {})

                    # Unprocessable Entity from FastAPI's own validator arrives as
                    # {"detail": [{"loc": [...], "msg": "...", "type": "..."}]}
                    # so guard for both shapes.
                    if isinstance(detail, dict):
                        raw = detail.get("raw_output", "No raw output available")
                        msg = detail.get("message", "Model failed to generate valid JSON.")
                    else:
                        raw = str(detail)
                        msg = "Model failed to generate valid JSON."

                    st.error(msg)
                    st.code(raw)

                else:
                    st.error(f"Backend Error: {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Failed to connect. Is your FastAPI server running on port 8000?")