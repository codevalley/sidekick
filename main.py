import json
import os
import yaml
import openai
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.markup import escape
from rich.markdown import Markdown
from rich.text import Text


# Load configuration from YAML file
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


# Load configuration and set OpenAI API key
config = load_config()
openai.api_key = config["openai_api_key"]

# Initialize Rich console for enhanced output
console = Console()


# Load JSON data from a file
def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []


# Save JSON data to a file
def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


# Call OpenAI API with given messages
def call_openai_api(system_prompt, datastore, conversation_history):
    try:
        with console.status("[bold green]Thinking...", spinner="dots"):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"Datastore: {json.dumps(datastore)}"},
            ]
            messages.extend(conversation_history)

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini-2024-07-18", messages=messages
            )

        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        console.print(
            "[bold red]Error:[/bold red] Unable to parse OpenAI response as JSON."
        )
        return None


# Process data received from the LLM
def process_data(data):
    # Load existing data from JSON files
    people = load_json_file("people.json")
    tasks = load_json_file("tasks.json")
    topics = load_json_file("topics.json")

    # Helper function to update or add new items to a list
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

    # Update people, tasks, and topics
    people, new_people, updated_people = update_or_add(
        people, data.get("people", []), "person_id"
    )
    tasks, new_tasks, updated_tasks = update_or_add(
        tasks, data.get("tasks", []), "task_id"
    )
    topics, new_topics, updated_topics = update_or_add(
        topics, data.get("topics", []), "topics_id"
    )

    # Save updated data to JSON files
    save_json_file("people.json", people)
    save_json_file("tasks.json", tasks)
    save_json_file("topics.json", topics)

    # Print updates to console
    for person in new_people:
        console.print(
            f"[bold green]Added a new contact:[/bold green] {person['name']} | {person['importance']} priority"
        )
    for person in updated_people:
        console.print(f"[bold yellow]Updated contact:[/bold yellow] {person['name']}")

    for task in new_tasks:
        console.print(
            f"[bold green]Added a new task:[/bold green] {task['description']}"
        )
    for task in updated_tasks:
        console.print(f"[bold yellow]Updated task:[/bold yellow] {task['description']}")

    for topic in new_topics:
        console.print(
            f"[bold green]Added a new topics entry:[/bold green] {topic['topic']}"
        )
    for topic in updated_topics:
        console.print(
            f"[bold yellow]Updated topics entry:[/bold yellow] {topic['topic']}"
        )


# Construct datastore for the LLM
def construct_datastore():
    return {
        "people": load_json_file("people.json"),
        "tasks": load_json_file("tasks.json"),
        "topics": load_json_file("topics.json"),
    }


# Get a summary of tasks, people, and topics entries
def get_task_summary():
    datastore = construct_datastore()
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conversation_history = [
        {"role": "user", "content": f"Current date and time: {current_datetime}"},
        {
            "role": "user",
            "content": "Provide an overview of all tasks, people, and topics entries.",
        },
    ]

    response = call_openai_api(config["system_prompt"], datastore, conversation_history)

    return (
        response["instructions"]["followup"]
        if response
        else "Unable to summarize tasks at the moment."
    )


# Main function to run the Sidekick assistant
def main():
    conversation_history = []
    thread_count = 0

    # Set up prompt style
    style = Style.from_dict(
        {
            "prompt": "ansicyan bold",
        }
    )

    session = PromptSession(style=style)

    # Display welcome message
    console.print(
        Panel.fit(
            Text("Welcome to Sidekick!", style="bold magenta")
            + Text("\nYour personal executive assistant", style="italic"),
            title="Sidekick",
            subtitle="Type 'exit' to quit",
        )
    )

    # Fetch and display initial task summary
    console.print("Fetching task summary...")
    task_summary = get_task_summary()

    markdown_summary = Markdown(task_summary)
    console.print(Panel(markdown_summary, title="Task Summary", border_style="blue"))

    # Main interaction loop
    while True:
        thread_indicator = f"[{thread_count}] " if thread_count > 0 else ""
        user_input = session.prompt(f"{thread_indicator}You: ")

        if user_input.lower() == "exit":
            break

        conversation_history.append({"role": "user", "content": user_input})
        thread_count += 1

        datastore = construct_datastore()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversation_history.append(
            {"role": "system", "content": f"Current date and time: {current_datetime}"}
        )

        # Get response from LLM
        llm_response = call_openai_api(
            config["system_prompt"], datastore, conversation_history
        )
        print(llm_response)
        if llm_response is None:
            console.print("[bold red]An error occurred. Please try again.[/bold red]")
            continue

        instructions = llm_response["instructions"]
        data = llm_response["data"]

        # Display LLM response
        markdown_followup = Markdown(instructions["followup"])
        console.print(Panel(markdown_followup, title="Sidekick", border_style="blue"))

        conversation_history.append(
            {"role": "assistant", "content": json.dumps(llm_response)}
        )

        # Process data if the conversation is complete
        if instructions["status"] == "complete":
            process_data(data)
            conversation_history = []
            thread_count = 0
            console.print(
                "[bold green]Thread completed. Starting new conversation.[/bold green]"
            )

            if "new_prompt" in instructions:
                console.print(
                    Panel(
                        escape(instructions["new_prompt"]),
                        title="New Suggestion",
                        border_style="green",
                    )
                )


if __name__ == "__main__":
    main()
