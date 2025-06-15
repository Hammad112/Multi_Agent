import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

import warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv(override=True)


# Streamlit app
def main():
    st.title("Flux.1-dev Image Generator")
    st.write("Generate images using NVIDIA's Flux.1-dev model. Enter your prompt and parameters below.")
    
    api_key = st.text_input('Enter your API key', type='password')
    

    # API endpoint
    invoke_url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"

    # Headers
    headers = {
        "Authorization":f"Bearer {api_key}",
        "Accept": "application/json",
    }

    # User inputs
    prompt = st.text_input("Prompt:", value="a simple coffee shop interior")
    cfg_scale = st.sidebar.slider("CFG Scale:", min_value=1.0, max_value=10.0, value=3.5, step=0.1)
    steps = st.sidebar.number_input("Steps:", min_value=1, max_value=100, value=50)

    if st.button("Generate Image"):
        with st.spinner("Generating image..."):
            # Payload
            payload = {
                "prompt": prompt,
                "mode": "base",
                "cfg_scale": cfg_scale,
                "steps": int(steps)
            }

            # Make API request
            try:
                response = requests.post(invoke_url, headers=headers, json=payload)
                response.raise_for_status()
                response_body = response.json()
                # Try common keys or nested structures
                image_data = None
                if "image" in response_body:
                    image_data = response_body["image"]
                elif "artifacts" in response_body and len(response_body["artifacts"]) > 0:
                    image_data = response_body["artifacts"][0].get("base64")
                elif "data" in response_body:
                    image_data = response_body["data"].get("image")

                if not image_data:
                    st.error("No image data found in response. Check the API response structure above.")
                    return

                # Decode and display image
                try:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    st.image(image, caption=f"Generated image: {prompt}", use_column_width=True)

                    # Download button
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    st.download_button(
                        label="Download Image",
                        data=buffered.getvalue(),
                        file_name="generated_image.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"Failed to process image: {str(e)}")
                    st.json(response_body)

            except requests.exceptions.HTTPError as e:
                st.error(f"HTTP Error: {str(e)} (Status Code: {e.response.status_code})")
                st.write(f"Response Text: {e.response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Request Error: {str(e)}")
            except ValueError as e:
                st.error(f"JSON Decode Error: {e}")
                st.write(f"Response Text: {response.text}")

if __name__ == "__main__":
    main()
