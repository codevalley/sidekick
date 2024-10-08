# Sidekick: Your Executive Assistant

Sidekick is an AI-powered personal assistant designed to enhance productivity and reliability for executives. It functions as a second brain, managing tasks, relationships, and knowledge through natural language interaction.

## Features

- Natural language interaction for task management and information retrieval
- Intelligent task classification and prioritization
- Dynamic knowledge base management
- Relationship-aware task handling
- Proactive assistance and recommendations

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sidekick.git
   cd sidekick
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your configuration:
   - Copy `config.yaml.example` to `config.yaml`
   - Add your OpenAI API key to `config.yaml`

## Usage

Run the main script to start Sidekick:

```
python main.py
```

Interact with Sidekick using natural language. Type 'exit' to quit the application.

## File Structure

- `main.py`: The main application file
- `config.yaml`: Configuration file for API keys and system prompts
- `tasks.json`: Stores all task entries
- `people.json`: Stores all people profiles
- `topics.json`: Stores all context/knowledge base entries

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.