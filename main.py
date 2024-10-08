import json
import os
import yaml
import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markup import escape

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()
openai.api_key = config['openai_api_key']

console = Console()

def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def call_openai_api(messages):
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Creating query...", total=None)
            progress.add_task(description="Sending query to OpenAI...", total=None)
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo", depending on your preference
                messages=messages
            )
            progress.add_task(description="Parsing response...", total=None)
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/bold red] Unable to parse OpenAI response as JSON.")
        return None

def process_data(data):
    people = load_json_file('people.json')
    tasks = load_json_file('tasks.json')
    topics = load_json_file('topics.json')

    def update_or_add(existing_list, new_items, id_field):
        id_to_item = {item[id_field]: item for item in existing_list}
        for new_item in new_items:
            id_to_item[new_item[id_field]] = new_item
        return list(id_to_item.values())

    people = update_or_add(people, data.get('people', []), 'person_id')
    tasks = update_or_add(tasks, data.get('tasks', []), 'task_id')
    topics = update_or_add(topics, data.get('contexts', []), 'context_id')

    save_json_file('people.json', people)
    save_json_file('tasks.json', tasks)
    save_json_file('topics.json', topics)

def main():
    system_prompt = config['system_prompt']

    conversation_history = []
    thread_count = 0

    style = Style.from_dict({
        'prompt': 'ansicyan bold',
    })

    session = PromptSession(style=style)

    while True:
        thread_indicator = f"[{thread_count}] " if thread_count > 0 else ""
        user_input = session.prompt(f"{thread_indicator}You: ")
        
        if user_input.lower() == 'exit':
            break

        conversation_history.append({"role": "user", "content": user_input})
        thread_count += 1

        context = {
            'people': load_json_file('people.json'),
            'tasks': load_json_file('tasks.json'),
            'topics': load_json_file('topics.json')
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current context: {json.dumps(context)}"}
        ] + conversation_history

        with console.status("[bold green]Thinking...") as status:
            llm_response = call_openai_api(messages)

        if llm_response is None:
            console.print("[bold red]An error occurred. Please try again.[/bold red]")
            continue

        instructions = llm_response['instructions']
        data = llm_response['data']

        console.print(Panel(escape(instructions['followup']), title="Sidekick", border_style="blue"))

        conversation_history.append({"role": "assistant", "content": json.dumps(llm_response)})

        if instructions['status'] == 'complete':
            process_data(data)
            conversation_history = []
            thread_count = 0
            console.print("[bold green]Thread completed. Starting new conversation.[/bold green]")

if __name__ == "__main__":
    main()