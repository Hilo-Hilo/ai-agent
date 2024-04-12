# AI Assistant for Carbon Linking

This repository contains a Python script designed to operate as an intelligent AI assistant for the company Carbon Linking. This assistant is capable of handling various tasks including searching the internet, generating images, and creating text content like articles. The script integrates multiple AI models and tools, with a focus on providing support for enhancing carbon literacy and promoting green actions.

## Features

- **Search Functionality**: Leverages the Tavily search client to perform internet searches based on user queries.
- **Image Generation**: Utilizes OpenAI's DALL-E model to generate images that correspond to specific prompts, aiding in visual content creation.
- **Text Generation**: Employs GPT-3.5-turbo model from OpenAI to generate high-quality text content in Markdown format, suitable for publications like blog posts.
- **Interactive User Queries**: Asks users for additional information when necessary to refine task execution.
- **Environment Variable Management**: Uses `.env` for managing sensitive data like API keys securely.

## Setup

### Requirements

- Python 3.8+
- OpenAI API key
- Tavily API key
- `python-dotenv`: To load environment variables
- `openai`: To interact with OpenAI services
- `PIL`: For image handling
- `hashlib`, `base64`: For encoding and file management

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourgithubusername/ai-agent.git
   cd ai-agent
   ```
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the root directory of the project.
2. Add the following lines to the `.env` file, replacing `your_tavily_api_key` and `your_openai_api_key` with your actual API keys:
   ```
   TAVILY_API_KEY=your_tavily_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```
3. Ensure the path to the directory for saving files (`path_to_files`) is correctly set in the script.

## Usage

Run the script using:

```bash
python path_to_the_script.py
```

The script operates in an interactive mode, receiving inputs through the terminal and responding accordingly. It is designed to handle complex tasks iteratively by communicating with the user and utilizing various tools as per the requirements.

## Cost Management

The script includes detailed tracking of API usage to manage costs effectively. It calculates the cost based on the number of tokens processed, converting this into a financial cost based on current rates.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributors

- Hanson Wen

## Acknowledgements

Thanks to Carbon Linking for the opportunity to contribute to environmental sustainability through technology.

