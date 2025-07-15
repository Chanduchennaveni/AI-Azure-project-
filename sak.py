import streamlit as st
import os
import io
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import azure.cognitiveservices.speech as speechsdk

# Azure credentials — replace with your own keys
VISION_KEY = "YOUR_COMPUTER_VISION_KEY"
VISION_ENDPOINT = "YOUR_COMPUTER_VISION_ENDPOINT"
SPEECH_KEY = "YOUR_SPEECH_KEY"
SPEECH_REGION = "YOUR_SPEECH_REGION"

# Create Computer Vision client
computervision_client = ComputerVisionClient(
    VISION_ENDPOINT, CognitiveServicesCredentials(VISION_KEY)
)

# Generate caption from image bytes
def get_image_caption(image_bytes):
    description_result = computervision_client.describe_image_in_stream(
        io.BytesIO(image_bytes), max_candidates=1
    )
    if description_result.captions:
        return description_result.captions[0].text
    else:
        return "Sorry, I couldn't generate a caption."

# Convert text to speech and save audio
def text_to_speech(text, output_path="outputs/description.mp3"):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return output_path
    else:
        st.error("Text-to-Speech synthesis failed.")
        return None

# Streamlit app entry
def main():
    st.set_page_config(page_title="Vision Assistant", page_icon="👁️‍🗨️")
    st.title("👁️‍🗨️ Vision Assistant for Visually Impaired")
    st.markdown("Upload an image and get a description read aloud.")

    uploaded_file = st.file_uploader("Upload an image (jpg, jpeg, png)", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="Uploaded Image", use_column_width=True)

        if st.button("Generate Caption & Read Aloud"):
            with st.spinner("Generating caption..."):
                caption = get_image_caption(image_bytes)
                st.markdown("### Caption:")
                st.write(f"> {caption}")

            with st.spinner("Converting text to speech..."):
                audio_path = text_to_speech(caption)
                if audio_path:
                    audio_file = open(audio_path, "rb").read()
                    st.audio(audio_file, format="audio/mp3")
                    st.success(f"Audio saved as `{audio_path}`")

# Create output folder and launch app
if __name__ == "__main__":
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    main()