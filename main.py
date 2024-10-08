import json
import os
import yaml
import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.markup import escape
from rich.markdown import Markdown
from rich.text import Text

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
    #console.print(f"[bold yellow]Updated file:[/bold yellow] {filename}")

def call_openai_api(messages):
    try:
        with console.status("[bold green]Thinking...", spinner="dots") as status:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini-2024-07-18",           # "gpt-4" or "gpt-3.5-turbo", depending on your preference
                messages=messages
            )
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
        new_entries = []
        updated_entries = []
        for new_item in new_items:
            if new_item[id_field] not in id_to_item:
                new_entries.append(new_item)
            else:
                updated_entries.append(new_item)
            id_to_item[new_item[id_field]] = new_item
        return list(id_to_item.values()), new_entries, updated_entries

    people, new_people, updated_people = update_or_add(people, data.get('people', []), 'person_id')
    tasks, new_tasks, updated_tasks = update_or_add(tasks, data.get('tasks', []), 'task_id')
    topics, new_topics, updated_topics = update_or_add(topics, data.get('knowledge', []), 'knowledge_id')

    save_json_file('people.json', people)
    save_json_file('tasks.json', tasks)
    save_json_file('topics.json', topics)

    # Display notifications for new and updated entries
    for person in new_people:
        console.print(f"[bold green]Added a new contact:[/bold green] {person['name']} | {person['importance']} priority")
    for person in updated_people:
        console.print(f"[bold yellow]Updated contact:[/bold yellow] {person['name']}")
    
    for task in new_tasks:
        console.print(f"[bold green]Added a new task:[/bold green] {task['description']}")
    for task in updated_tasks:
        console.print(f"[bold yellow]Updated task:[/bold yellow] {task['description']}")
    
    for topic in new_topics:
        console.print(f"[bold green]Added a new knowledge entry:[/bold green] {topic['topic']}")
    for topic in updated_topics:
        console.print(f"[bold yellow]Updated knowledge entry:[/bold yellow] {topic['topic']}")

def get_task_summary():
    context = {
        'people': load_json_file('people.json'),
        'tasks': load_json_file('tasks.json'),
        'topics': load_json_file('topics.json')
    }
    
    messages = [
        {"role": "system", "content": config['system_prompt']},
        {"role": "user", "content": f"Current context: {json.dumps(context)}"},
        {"role": "user", "content": "Provide an overview of all tasks, people, and knowledge entries."}
    ]
    
    response = call_openai_api(messages)
    return response['instructions']['followup'] if response else "Unable to summarize tasks at the moment."

def main():
    system_prompt = config['system_prompt']

    conversation_history = []
    thread_count = 0

    style = Style.from_dict({
        'prompt': 'ansicyan bold',
    })

    session = PromptSession(style=style)

    # Display welcome message and task summary
    console.print(Panel.fit(
        Text("Welcome to Sidekick!", style="bold magenta") + 
        Text("\nYour personal executive assistant", style="italic"),
        title="Sidekick",
        subtitle="Type 'exit' to quit"
    ))

    console.print("Fetching task summary...")
    task_summary = get_task_summary()
    
    # Convert the followup text to a Markdown object
    markdown_summary  = Markdown(task_summary)
    console.print(Panel(markdown_summary, title="Task Summary", border_style="blue"))


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
            'knowledge': load_json_file('knowledge.json')
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current context: {json.dumps(context)}"}
        ] + conversation_history

        llm_response = call_openai_api(messages)

        if llm_response is None:
            console.print("[bold red]An error occurred. Please try again.[/bold red]")
            continue

        instructions = llm_response['instructions']
        data = llm_response['data']

        # Convert the followup text to a Markdown object
        markdown_followup = Markdown(instructions['followup'])
        console.print(Panel(markdown_followup, title="Sidekick", border_style="blue"))


        conversation_history.append({"role": "assistant", "content": json.dumps(llm_response)})

        if instructions['status'] == 'complete':
            process_data(data)
            conversation_history = []
            thread_count = 0
            console.print("[bold green]Thread completed. Starting new conversation.[/bold green]")
            
            if 'new_prompt' in instructions:
                console.print(Panel(escape(instructions['new_prompt']), title="New Suggestion", border_style="green"))

if __name__ == "__main__":
    main()