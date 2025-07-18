# main.py
# Run this app with the command: streamlit run main.py

import streamlit as st
import os
from openai import AzureOpenAI
import re
import dotenv

dotenv.load_dotenv()  # Lädt Umgebungsvariablen aus der .env-Datei
# --- Configuration ---
# Enter your Azure OpenAI credentials here.
# It is recommended to use environment variables for better security.
# If the environment variables are set, they will be used automatically.
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "YOUR_AZURE_OPENAI_ENDPOINT_URL")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "YOUR_AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "YOUR_DEPLOYMENT_NAME")
API_VERSION = "2024-02-01" # Current recommended API version


# --- System Prompt for the LLM (Improved for Creativity) ---
# This prompt instructs the LLM on how to behave.
SYSTEM_PROMPT = """
You are a creative and whimsical SVG animator, like the team that designed the famous Microsoft Office Assistant 'Clippy'. 
Your goal is to bring static SVGs to life with personality, character, and complex, engaging animations. Don't just move elements; make them tell a small story.

Follow these rules strictly:
1.  **Think like an animator:** Analyze the user's request for a mood or personality (e.g., "curious," "sleepy," "happy"). Translate this into a sequence of animations. A "curious" robot might tilt its head, look left and right, and then have its antenna twitch.
2.  **Create Complex Sequences:** Do not create simple, single, infinite loops. Chain animations together using `begin` attributes (e.g., `anim1.end`, `anim2.end + 0.5s`). Create a short, interesting, and looping story.
3.  **Use Advanced Techniques:**
    -   Employ `animateTransform` for expressive movements (rotation, scaling, translation).
    -   Use `<animate>` to change attributes like `fill` for color changes.
    -   Stagger animations. Not everything should move at once. Create a natural rhythm.
    -   **Path Morphing (`d` attribute):** This is crucial for effects like "waving" or "thinking". To animate a path's shape, you MUST animate the `d` attribute.
        -   Identify the key points (start, end) of the line segment to be animated.
        -   Create one or more intermediate path shapes using cubic Bézier curves (`C`) to create the wave.
        -   Use the `values` attribute in the `<animate>` tag to list the different `d` attribute strings, separated by semicolons. The animation should start with the original path, morph to the waved path, and then return to the original.
        -   Example for a line from (10,80) to (90,80): `<animate attributeName="d" dur="2s" repeatCount="indefinite" values="M10 80 L 90 80; M10 80 C 40 40, 60 120, 90 80; M10 80 L 90 80;" />`
4.  **Respect Transformations (Crucial):** When applying an `<animateTransform>` (like `rotate`, `scale`), you MUST respect the element's existing `transform` attribute.
    -   To prevent the element from jumping to the origin (0,0), use `additive="sum"`.
    -   For rotations (`type="rotate"`), you MUST calculate or estimate the element's center point (cx, cy) and specify it in the animation (e.g., `from="0 cx cy"` `to="360 cx cy"`) to rotate it in place.
5.  **Identify and ID Elements:** Prioritize descriptive `id` attributes (e.g., `id="left-eye"`). If they don't exist, add unique IDs to the elements you need to animate.
6.  **Output Clean Code:** The final output MUST be ONLY the complete, raw, and valid SVG code. All attribute values must be enclosed in double quotes. Do not include comments, explanations, or Markdown fences.
7.  **CRITICAL VALIDATION:** Ensure every attribute has a valid, non-empty value. An attribute like `from=""` or `to=""` is invalid and MUST NOT be generated. Every animation attribute requires a specific value.
"""

# --- Helper Functions ---

def clean_svg_response(response_text):
    """
    Cleans the LLM response to ensure it's valid SVG code.
    1. Removes Markdown code fences.
    2. Removes non-breaking spaces.
    3. Fixes unquoted attributes.
    4. Removes empty attributes that cause validation errors.
    """
    if not response_text:
        return ""
    
    # 1. Remove Markdown fences
    match = re.search(r'```(?:svg)?\s*(<svg.*?</svg>)\s*```', response_text, re.DOTALL | re.IGNORECASE)
    if match:
        cleaned_text = match.group(1)
    else:
        cleaned_text = response_text

    # 2. Remove non-breaking spaces and strip whitespace
    cleaned_text = cleaned_text.replace('\xa0', ' ').strip()
    
    # 3. Fix unquoted attributes. Example: transform=scale(...) -> transform="scale(...)"
    cleaned_text = re.sub(r'([a-zA-Z0-9\-:]+=)([^"\s>]+)', r'\1"\2"', cleaned_text)

    # 4. Remove empty attributes that cause validation errors (e.g., from="", to="")
    cleaned_text = re.sub(r'\s+([a-zA-Z0-9\-:]+)=""', '', cleaned_text)

    return cleaned_text

def get_animated_svg(svg_code, description, animation_instructions):
    """
    Calls the Azure OpenAI API to get the animated SVG.

    Args:
        svg_code (str): The original SVG code.
        description (str): Description of the static SVG.
        animation_instructions (str): Instructions for the animation.

    Returns:
        str: The animated SVG code, or an error message.
    """
    # Clean the input SVG code of problematic characters
    cleaned_svg_code = svg_code.replace('\xa0', ' ')

    if not all([AZURE_OPENAI_ENDPOINT != "YOUR_AZURE_OPENAI_ENDPOINT_URL",
                AZURE_OPENAI_API_KEY != "YOUR_AZURE_OPENAI_API_KEY",
                AZURE_OPENAI_DEPLOYMENT_NAME != "YOUR_DEPLOYMENT_NAME"]):
        st.error("Error: Azure OpenAI credentials are not configured. Please set the variables in the code or use environment variables.")
        return None

    try:
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=API_VERSION
        )

        user_prompt = f"""
        Here is the SVG code:
        ---
        {cleaned_svg_code}
        ---

        Description of what the graphic shows:
        ---
        {description}
        ---

        Animation instructions:
        ---
        {animation_instructions}
        ---
        """

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6, # Increased temperature for more creativity
            max_tokens=4000
        )

        animated_svg = response.choices[0].message.content
        return clean_svg_response(animated_svg)

    except Exception as e:
        st.error(f"An error occurred with the API request: {e}")
        return None


# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="SVG Animator AI")

# Application Title
st.title("🤖 SVG Animator AI with Azure OpenAI")
st.markdown("Paste your SVG code, describe the desired animation, and let the AI do the rest.")

# Column layout for a better overview
col1, col2 = st.columns(2, gap="large")

with col1:
    st.header("1. Input")
    st.markdown("Provide the details of your SVG graphic here.")

    # Example SVG code for the user
    sample_svg = """<svg width="100%" height="100%" viewBox="0 0 1000 1000" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;">
    <g transform="matrix(2,0,0,-2,0,1000)">
        <g id="Gesicht" transform="matrix(1,0,0,1,61.5,123.472)">
            <path d="M310.524,252.056L66.476,252.056C30.431,252.056 1,222.625 1,186.58L1,116.474C1,80.429 30.431,50.998 66.476,50.998L133.44,50.998C151.463,51.659 151.463,77.618 133.44,78.114L66.476,78.114C45.312,78.114 28.282,95.31 28.282,116.309L28.282,186.415C28.282,207.579 45.478,224.609 66.476,224.609L310.524,224.609C331.688,224.609 348.718,207.413 348.718,186.415L348.718,114.49L268.361,34.133L230.828,73.65C228.348,76.296 225.041,77.784 221.403,77.949C209.664,78.445 202.72,63.399 211.152,54.966L258.275,5.198C263.235,-0.259 272.66,-0.424 277.786,4.867L372.032,99.113C374.512,101.593 376,105.231 376,108.703L376,186.249C376,222.294 346.569,251.726 310.524,251.726L310.524,252.056Z" style="fill:rgb(33,253,255);fill-rule:nonzero;"/>
        </g>
        <g id="Auge-rechts" serif:id="Auge rechts" transform="matrix(1,0,0,1,266.998,226.768)">
            <path d="M96.387,48.282C96.387,74.395 75.034,95.563 48.694,95.563C22.353,95.563 1,74.395 1,48.282C1,22.169 22.353,1 48.694,1C75.034,1 96.387,22.169 96.387,48.282Z" style="fill-rule:nonzero;"/>
        </g>
        <g id="Auge-links" serif:id="Auge liinks" transform="matrix(1,0,0,1,130.26,226.768)">
            <path d="M96.387,48.282C96.387,74.395 75.034,95.563 48.694,95.563C22.353,95.563 1,74.395 1,48.282C1,22.169 22.353,1 48.694,1C75.034,1 96.387,22.169 96.387,48.282Z" style="fill-rule:nonzero;"/>
        </g>
        <g id="Pupille-links" serif:id="Pupille links" transform="matrix(1,0,0,1,167.502,267.46)">
            <path d="M41.198,19.182C41.198,29.224 32.199,37.364 21.099,37.364C9.999,37.364 1,29.224 1,19.182C1,9.14 9.999,1 21.099,1C32.199,1 41.198,9.14 41.198,19.182Z" style="fill:white;fill-rule:nonzero;"/>
        </g>
        <g id="Pupille-rechts" serif:id="Pupille rechts" transform="matrix(1,0,0,1,304.24,267.46)">
            <path d="M41.198,19.182C41.198,29.224 32.199,37.364 21.099,37.364C9.999,37.364 1,29.224 1,19.182C1,9.14 9.999,1 21.099,1C32.199,1 41.198,9.14 41.198,19.182Z" style="fill:white;fill-rule:nonzero;"/>
        </g>
        <g id="Antenne-rechts" serif:id="Antenne rechts" transform="matrix(1,0,0,1,260,374.528)">
            <path d="M4.317,1C4.317,1.811 4.201,2.341 2.864,7.725C1.861,11.764 1.314,14.609 1.09,17.682C0.296,28.576 4.731,37.208 15.85,41.872L15.357,41.642L35.624,52.064L42.026,39.613L21.758,29.192C21.597,29.109 21.432,29.032 21.265,28.962C16.125,26.806 14.669,23.972 15.053,18.699C15.205,16.612 15.626,14.423 16.451,11.099C16.566,10.638 16.978,9.005 17.059,8.678C17.301,7.707 17.48,6.959 17.637,6.242C18.081,4.209 18.317,2.583 18.317,1L4.317,1Z" style="fill:url(#_Linear1);fill-rule:nonzero;"/>
        </g>
        <g id="Antenne-links" serif:id="Antenne links" transform="matrix(1,0,0,1,191.576,374.528)">
            <path d="M24.754,1C24.754,2.59 24.987,4.23 25.429,6.284C25.585,7.011 25.763,7.771 26.004,8.757C26.086,9.089 26.498,10.752 26.612,11.222C27.44,14.617 27.864,16.857 28.017,18.998C28.407,24.445 26.917,27.397 21.764,29.597C21.596,29.669 21.43,29.748 21.267,29.833L1,40.441L7.492,52.845L27.76,42.236L27.262,42.472C38.368,37.73 42.769,29.01 41.981,17.999C41.759,14.888 41.213,12.004 40.213,7.904C38.868,2.387 38.754,1.857 38.754,1L24.754,1Z" style="fill:url(#_Linear2);fill-rule:nonzero;"/>
        </g>
        <g id="Mund" transform="matrix(1,0,0,1,219.65,192.272)">
            <path d="M1,24.924C2.578,24.924 3.672,24.272 4.2,23.057C4.543,22.267 4.601,21.598 4.601,20.018C4.601,17.775 4.755,17.421 5.892,17.421C6.794,17.421 7.182,19.641 7.182,25.596C7.182,29.171 7.234,30.659 7.505,32.209C7.927,34.622 8.911,36.081 10.783,36.081C12.78,36.081 13.664,34.229 14.07,30.951C14.333,28.826 14.384,26.747 14.384,21.752C14.384,13.33 14.829,9.734 15.675,9.734C15.864,9.734 16.392,11.167 16.665,14.021C16.915,16.636 16.965,19.285 16.965,25.642C16.965,32.083 17.017,34.765 17.276,37.483C17.676,41.668 18.484,43.861 20.566,43.861C22.7,43.861 23.46,41.41 23.858,36.462C24.116,33.251 24.167,30.069 24.167,22.43C24.167,14.863 24.218,11.708 24.469,8.584C24.625,6.655 24.85,5.2 25.147,4.24C25.284,3.798 25.429,3.489 25.558,3.326C25.592,3.283 25.543,3.31 25.458,3.31C25.347,3.31 25.291,3.276 25.329,3.329C25.467,3.52 25.619,3.873 25.761,4.371C26.063,5.433 26.29,7.031 26.446,9.147C26.698,12.56 26.749,16.001 26.749,24.256C26.749,32.577 26.8,36.042 27.057,39.536C27.455,44.921 28.192,47.512 30.35,47.512C32.507,47.512 33.245,44.921 33.642,39.536C33.9,36.042 33.951,32.577 33.951,24.256C33.951,16.001 34.001,12.56 34.253,9.147C34.409,7.031 34.636,5.433 34.938,4.371C35.08,3.873 35.232,3.52 35.37,3.329C35.408,3.276 35.353,3.31 35.241,3.31C35.156,3.31 35.107,3.283 35.141,3.326C35.27,3.489 35.415,3.798 35.552,4.24C35.85,5.2 36.075,6.655 36.23,8.584C36.481,11.708 36.532,14.863 36.532,22.43C36.532,30.069 36.583,33.251 36.841,36.462C37.239,41.41 37.999,43.861 40.133,43.861C42.215,43.861 43.023,41.668 43.423,37.483C43.683,34.765 43.734,32.083 43.734,25.642C43.734,19.285 43.785,16.636 44.034,14.021C44.307,11.167 44.835,9.734 45.024,9.734C45.87,9.734 46.315,13.33 46.315,21.752C46.315,26.747 46.367,28.826 46.63,30.951C47.035,34.229 47.919,36.081 49.916,36.081C51.789,36.081 52.773,34.622 53.194,32.209C53.465,30.659 53.517,29.171 53.517,25.596C53.517,19.641 53.905,17.421 54.808,17.421C55.945,17.421 56.098,17.775 56.098,20.018C56.098,21.598 56.156,22.267 56.5,23.057C57.028,24.272 58.122,24.924 59.699,24.924L59.699,22.614C58.562,22.614 58.409,22.261 58.409,20.018C58.409,18.437 58.351,17.768 58.007,16.978C57.479,15.763 56.385,15.111 54.808,15.111C52.935,15.111 51.951,16.57 51.53,18.983C51.259,20.533 51.207,22.021 51.207,25.596C51.207,31.551 50.819,33.771 49.916,33.771C49.837,33.771 49.728,33.681 49.545,33.296C49.28,32.743 49.07,31.858 48.922,30.668C48.676,28.676 48.626,26.638 48.626,21.752C48.626,16.758 48.574,14.678 48.311,12.554C47.905,9.276 47.021,7.423 45.024,7.423C42.942,7.423 42.134,9.616 41.734,13.801C41.475,16.519 41.423,19.201 41.423,25.642C41.423,31.999 41.373,34.649 41.123,37.263C40.85,40.117 40.322,41.55 40.133,41.55C40.218,41.55 40.267,41.578 40.233,41.535C40.104,41.372 39.959,41.063 39.822,40.621C39.524,39.661 39.299,38.206 39.144,36.277C38.893,33.152 38.842,29.998 38.842,22.43C38.842,14.792 38.791,11.61 38.533,8.399C38.135,3.451 37.375,1 35.241,1C33.084,1 32.346,3.591 31.949,8.977C31.691,12.47 31.64,15.936 31.64,24.256C31.64,32.512 31.589,35.952 31.338,39.366C31.182,41.481 30.955,43.08 30.652,44.142C30.511,44.64 30.359,44.993 30.221,45.184C30.183,45.236 30.238,45.202 30.35,45.202C30.461,45.202 30.516,45.236 30.479,45.184C30.34,44.993 30.189,44.64 30.047,44.142C29.745,43.08 29.518,41.481 29.362,39.366C29.11,35.952 29.059,32.512 29.059,24.256C29.059,15.936 29.008,12.47 28.75,8.977C28.353,3.591 27.615,1 25.458,1C23.325,1 22.564,3.451 22.166,8.399C21.908,11.61 21.857,14.792 21.857,22.43C21.857,29.998 21.806,33.152 21.555,36.277C21.4,38.206 21.175,39.661 20.877,40.621C20.74,41.063 20.595,41.372 20.466,41.535C20.433,41.578 20.481,41.55 20.566,41.55C20.377,41.55 19.849,40.117 19.576,37.263C19.327,34.649 19.276,31.999 19.276,25.642C19.276,19.201 19.225,16.519 18.965,13.801C18.565,9.616 17.757,7.423 15.675,7.423C13.678,7.423 12.794,9.276 12.388,12.554C12.125,14.678 12.074,16.758 12.074,21.752C12.074,30.175 11.629,33.771 10.783,33.771C9.881,33.771 9.493,31.551 9.493,25.596C9.493,22.021 9.441,20.533 9.17,18.983C8.748,16.57 7.764,15.111 5.892,15.111C4.314,15.111 3.22,15.763 2.692,16.978C2.349,17.768 2.291,18.437 2.291,20.018C2.291,22.261 2.137,22.614 1,22.614L1,24.924Z" style="fill-rule:nonzero;"/>
        </g>
    </g>
    <defs>
        <linearGradient id="_Linear1" x1="0" y1="0" x2="1" y2="0" gradientUnits="userSpaceOnUse" gradientTransform="matrix(2.64208e-15,-43.1485,43.1485,2.64208e-15,23.3236,45.1108)"><stop offset="0" style="stop-color:white;stop-opacity:1"/><stop offset="1" style="stop-color:rgb(33,253,255);stop-opacity:1"/></linearGradient>
        <linearGradient id="_Linear2" x1="0" y1="0" x2="1" y2="0" gradientUnits="userSpaceOnUse" gradientTransform="matrix(2.69102e-15,-43.9476,43.9476,2.69102e-15,19.7462,45.9105)"><stop offset="0" style="stop-color:white;stop-opacity:1"/><stop offset="1" style="stop-color:rgb(33,253,255);stop-opacity:1"/></linearGradient>
    </defs>
</svg>"""

    svg_code_input = st.text_area(
        "Paste SVG code here",
        height=300,
        value=sample_svg,
        help="Paste the full code of your SVG file here. Tip: Give important elements an 'id' (e.g., id='left-eye') for better results."
    )

    description_input = st.text_area(
        "What does the graphic show?",
        height=100,
        value="A robot-like face (id='Gesicht') with two black eyes (id='Auge-links', 'Auge-rechts'), two pupils (id='Pupille-links', 'Pupille-rechts), and two antennas (id='Antenne-links', 'Antenne-rechts').",
        help="A brief description of the graphic's content."
    )

    animation_input = st.text_area(
        "How should the animation look?",
        height=150,
        value="Bring the robot to life! The long straight line at the top of its face (inside the 'Gesicht' group) should dynamically wave as if the robot is thinking, and then become straight again.",
        help="Describe the desired personality or a short story."
    )

    # Button to start the process
    animate_button = st.button("✨ Animate SVG", type="primary", use_container_width=True)

with col2:
    st.header("2. Result")
    st.markdown("The animated SVG graphic will be displayed here.")

    # Placeholder for the output
    result_placeholder = st.empty()
    result_placeholder.info("The result will be shown here after you click 'Animate SVG'.")

# --- Logic ---
if animate_button:
    # Check if all inputs are provided
    if not svg_code_input or not description_input or not animation_input:
        st.warning("Please fill in all fields to continue.")
    else:
        with st.spinner("The AI is getting creative and bringing your SVG to life... This might take a moment."):
            # API call
            animated_svg_result = get_animated_svg(svg_code_input, description_input, animation_input)

        if animated_svg_result and animated_svg_result.strip().startswith('<svg'):
            st.success("Animation created successfully!")

            # Display the animated SVG
            # We add CSS to ensure the SVG does not overflow its container.
            display_html = f"""
            <div style="border: 1px solid #ccc; border-radius: 8px; padding: 20px; text-align: center; background-color: #f9f9f9;">
                <div style="max-width: 100%; height: auto;">
                    {animated_svg_result}
                </div>
            </div>
            """
            result_placeholder.markdown(display_html, unsafe_allow_html=True)

            # Download button for the animated SVG
            st.download_button(
                label="⬇️ Download Animated SVG",
                data=animated_svg_result.encode('utf-8'),
                file_name="animated_graphic.svg",
                mime="image/svg+xml",
                use_container_width=True
            )

            # Expander to show the generated code
            with st.expander("Show Generated SVG Code"):
                st.code(animated_svg_result, language='xml')
        else:
            # Error handling if the API does not return a valid SVG
            result_placeholder.error("Could not create a valid SVG animation. Please try a different description or check your original SVG code.")
            if animated_svg_result:
                st.code(animated_svg_result, language='text')
