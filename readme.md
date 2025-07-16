🤖 SVG Animator AI
Breathe life into your static SVG graphics with the power of AI. This tool uses Azure OpenAI to transform your text descriptions into complex, character-rich SMIL animations—right in your browser.

Forget complex animation software. Simply describe the desired personality ("Make the robot look curious!") and watch as the AI creates a unique, "Clippy"-style animation.


Table of Contents
🚀 Features

🛠️ How It Works

🏁 Quick Start

💡 Pro-Tips for Best Results

🤝 Contributing

📄 License

🚀 Features
AI-Powered Animation: Converts natural language into complex SMIL animations.

Creative Animator Mode: The AI acts not as a mere code generator, but as a creative animator that builds personality and character.

Complex Animations: Generates chained and staggered animations that tell a short story.

Advanced Technique Support: Masters path morphing (animating the d attribute), transformations, and color changes.

Interactive UI: An easy-to-use interface built with Streamlit.

Live Preview: Instantly see the animated SVG within the app.

Download Functionality: Download the final, validated SVG file.

Intelligent Error Correction: Automatically cleans up common errors in AI-generated code to ensure compatibility.

🛠️ How It Works
The application combines a Streamlit UI with the power of an Azure OpenAI language model.

Input: You paste your SVG code and a text description of the desired animation.

System Prompt: A specially designed system prompt instructs the AI to behave like a creative animator. It includes detailed rules for complex animation techniques and the correct handling of SVG structures.

API Call: The inputs are sent to the Azure OpenAI API.

Generation: The AI analyzes the SVG, interprets your instructions, and injects the corresponding SMIL animation tags into the code.

Cleaning & Display: The result is automatically checked for common errors and corrected before being displayed in the Streamlit app and made available for download.

🏁 Quick Start
Follow these steps to get the project running locally in minutes.

Prerequisites

Python 3.8+

An Azure account with access to the Azure OpenAI Service.

Installation & Setup

Clone the Repository:

git clone https://github.com/YOUR-USERNAME/svg-animator-ai.git
cd svg-animator-ai

Install Dependencies:
(Create a requirements.txt file with the content below, then run the command.)

# requirements.txt
streamlit
openai

pip install -r requirements.txt

Configure Environment Variables:
(This is the most secure method. Do not commit your keys to GitHub.)

For Linux/macOS:

export AZURE_OPENAI_ENDPOINT="YOUR_ENDPOINT_URL"
export AZURE_OPENAI_API_KEY="YOUR_API_KEY"
export AZURE_OPENAI_DEPLOYMENT_NAME="YOUR_DEPLOYMENT_NAME"

For Windows (PowerShell):

$env:AZURE_OPENAI_ENDPOINT="YOUR_ENDPOINT_URL"
$env:AZURE_OPENAI_API_KEY="YOUR_API_KEY"
$env:AZURE_OPENAI_DEPLOYMENT_NAME="YOUR_DEPLOYMENT_NAME"

Run the Application:

streamlit run main.py

Your browser should automatically open and display the application.

💡 Pro-Tips for Best Results
Use IDs: Give the SVG elements you want to animate clear and descriptive id attributes (e.g., <g id="left-eye">...</g>). This helps the AI identify the correct parts.

Be Creative, Not Technical: Instead of "Rotate by 10 degrees," write "Make the head bob curiously." Describe a mood or a story.

Iterate: Not every animation will be perfect on the first try. Use the result as a starting point and adjust your instructions to refine the animation.

Start Simple: First, test simple animations on a single element to get a feel for how the AI responds to your instructions.

🤝 Contributing
Contributions are welcome! If you have ideas for new features, find bugs, or want to improve the documentation, please create an issue or a pull request.

Fork the repository.

Create a new branch (git checkout -b feature/new-animation).

Make your changes.

Commit your changes (git commit -m 'Add new animation feature').

Push to the branch (git push origin feature/new-animation).

Open a Pull Request.

📄 License
This project is licensed under the MIT License. See the LICENSE file for more details.