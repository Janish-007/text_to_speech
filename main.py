"""
Text-to-Speech Streamlit Application with Translation
Translate and convert text into natural-sounding speech
"""

import streamlit as st
from gtts import gTTS
from gtts.lang import tts_langs
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
import base64
from io import BytesIO
import time

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Page configuration
st.set_page_config(
    page_title="Text-to-Speech with Translation",
    page_icon="speaker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .translation-box {
        padding: 1rem;
        border: 2px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    </style>
""", unsafe_allow_html=True)

# Supported translation languages
TRANSLATION_LANGUAGES = {
    'auto': 'Auto-detect',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'pl': 'Polish',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'el': 'Greek',
    'he': 'Hebrew',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'ur': 'Urdu',
    'fa': 'Persian',
    'ro': 'Romanian',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'uk': 'Ukrainian'
}


def get_audio_download_link(audio_bytes, filename="audio.mp3"):
    """Generate download link for audio file"""
    b64 = base64.b64encode(audio_bytes).decode()
    return f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download Audio File</a>'


def get_supported_languages():
    """Get dictionary of supported languages"""
    try:
        return tts_langs()
    except:
        # Fallback to common languages
        return {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh-cn': 'Chinese (Simplified)',
            'hi': 'Hindi',
            'ar': 'Arabic'
        }


def detect_language(text):
    """Detect language of the text"""
    try:
        lang = detect(text)
        return lang
    except:
        return None


def translate_text(text, source_lang='auto', target_lang='en'):
    """Translate text from source language to target language"""
    try:
        # Detect language if auto
        detected_lang = None
        if source_lang == 'auto':
            detected_lang = detect_language(text)
            if detected_lang:
                source_lang = detected_lang
            else:
                source_lang = 'en'
        
        # Don't translate if source and target are the same
        if source_lang == target_lang:
            return text, source_lang, None
        
        # Handle Chinese variants
        if target_lang == 'zh-cn':
            target_lang = 'zh-CN'
        elif target_lang == 'zh-tw':
            target_lang = 'zh-TW'
        
        # Translate using GoogleTranslator
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        
        return translated, source_lang, None
        
    except Exception as e:
        return None, None, str(e)


def convert_text_to_speech(text, lang='en', slow=False, tld='com'):
    """Convert text to speech and return audio bytes"""
    try:
        # Create TTS object
        tts = gTTS(text=text, lang=lang, slow=slow, tld=tld)
        
        # Save to BytesIO instead of file
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        # Get audio data
        audio_data = audio_bytes.read()
        
        # Calculate file size
        file_size = len(audio_data) / 1024  # KB
        
        return audio_data, file_size, None
        
    except Exception as e:
        return None, None, str(e)


# Header
st.markdown('<h1 class="main-header">Text-to-Speech with Translation</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Translate and convert your text into natural-sounding speech</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Get supported languages
    languages = get_supported_languages()
    
    # Translation settings
    st.subheader("Translation")
    
    enable_translation = st.checkbox("Enable Translation", value=False, 
                                     help="Translate text before converting to speech")
    
    if enable_translation:
        # Source language
        source_lang_options = {name: code for code, name in TRANSLATION_LANGUAGES.items()}
        
        selected_source = st.selectbox(
            "From Language",
            options=list(source_lang_options.keys()),
            index=0,
            help="Source language (Auto-detect recommended)"
        )
        source_lang = source_lang_options[selected_source]
    
    # Target/Output language selection
    language_options = {f"{name} ({code})": code for code, name in sorted(languages.items(), key=lambda x: x[1])}
    
    selected_lang = st.selectbox(
        "To Language" if enable_translation else "Output Language",
        options=list(language_options.keys()),
        index=0,
        help="Target language for translation and speech"
    )
    lang_code = language_options[selected_lang]
    
    # Accent selection (for English)
    if lang_code == 'en':
        accent_options = {
            'US English': 'com',
            'UK English': 'co.uk',
            'Canadian English': 'ca',
            'Australian English': 'com.au',
            'Indian English': 'co.in'
        }
        selected_accent = st.selectbox(
            "Accent",
            options=list(accent_options.keys())
        )
        tld = accent_options[selected_accent]
    else:
        tld = 'com'
    
    # Speech speed
    slow_speech = st.checkbox("Slow Speech", value=False, help="Slower speech for learning")
    
    st.divider()
    
    # Info
    st.header("Features")
    st.info("""
    **Core Features:**
    - 100+ languages for TTS
    - Auto language detection
    - Text translation
    - Multiple English accents
    - Slow speech option
    - Batch processing
    - Download audio files
    """)

# Main content - Single tab
st.header("Convert Text to Speech")

if enable_translation:
    st.info(f"Translation enabled: {selected_source} → {selected_lang.split('(')[0].strip()}")

# Text input
text_input = st.text_area(
    "Enter your text:",
    height=200,
    placeholder="Type or paste your text here...\n\nExample: Hello! This tool can translate and convert your text into speech in multiple languages.",
    help="Enter the text you want to convert to speech. Maximum 5000 characters."
)

# Character count
char_count = len(text_input)
col1, col2 = st.columns([3, 1])
with col1:
    if char_count > 5000:
        st.error(f"Text too long: {char_count}/5000 characters")
    else:
        st.info(f"Characters: {char_count}/5000")

# Convert button
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    convert_button = st.button("Convert to Speech", type="primary", use_container_width=True)
with col2:
    if text_input:
        if st.button("Clear Text", use_container_width=True):
            st.rerun()

if convert_button:
    if not text_input or not text_input.strip():
        st.error("Please enter some text to convert!")
    elif char_count > 5000:
        st.error("Text is too long. Please reduce to 5000 characters or less.")
    else:
        # Step 1: Translation (if enabled)
        translated_text = text_input
        detected_lang = None
        
        if enable_translation:
            with st.spinner("Translating text..."):
                translated_text, detected_lang, trans_error = translate_text(
                    text_input,
                    source_lang=source_lang,
                    target_lang=lang_code
                )
                
                if trans_error:
                    st.error(f"Translation error: {trans_error}")
                    st.info("Converting original text to speech instead...")
                    translated_text = text_input
                else:
                    # Show translation result
                    st.success("Translation successful!")
                    
                    # Show translated text
                    st.markdown("**Translated Text:**")
                    st.markdown(f'<div class="translation-box">{translated_text}</div>', 
                              unsafe_allow_html=True)
        
        # Step 2: Convert to speech
        with st.spinner("Converting to speech..."):
            audio_data, file_size, error = convert_text_to_speech(
                translated_text, 
                lang=lang_code, 
                slow=slow_speech,
                tld=tld
            )
            
            if error:
                st.error(f"Error: {error}")
                st.info("Tip: Make sure you have an internet connection. gTTS requires internet to work.")
            else:
                st.success("Conversion successful!")
                
                # Display audio player
                st.audio(audio_data, format='audio/mp3')
                
                # File info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{file_size:.2f} KB")
                with col2:
                    st.metric("Output Language", languages.get(lang_code, lang_code))
                with col3:
                    word_count = len(translated_text.split())
                    st.metric("Approx Duration", f"~{word_count * 0.5:.1f} sec")
                
                # Download link
                st.markdown(get_audio_download_link(audio_data, "audio.mp3"), unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Text-to-Speech with Translation</p>
        <p>Translate and convert text into speech in 100+ languages</p>
    </div>

""", unsafe_allow_html=True)
