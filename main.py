import json
import os
import yaml
import openai
from openai import OpenAI
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from pydantic import BaseModel, Field
from typing import List, Literal
import argparse
import time


# Load configuration from YAML file
def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Initialize Rich console for enhanced output
console = Console()


# Load JSON data from a file
def load_json_file(filename):
    """
    Load JSON data from a file. If the file doesn't exist,
    return an empty list.
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# Save JSON data to a file
def save_json_file(filename, data):
    """
    Save JSON data to a file with proper indentation.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Pydantic models for structured outputs
class PersonContact(BaseModel):
    """
    Model for storing contact information of a person.
    """
    email: str
    phone: str


class Person(BaseModel):
    """
    Model for storing information about a person in the People Directory.
    """
    person_id: str
    name: str
    designation: str
    relationship: str
    importance: Literal["high", "medium", "low"]
    notes: str
    contact: PersonContact


class TaskPeople(BaseModel):
    """
    Model for storing people associated with a task.
    """
    owner: str
    final_beneficiary: str
    stakeholders: List[str]


class Task(BaseModel):
    """
    Model for storing task information.
    """
    task_id: str
    # Corresponds to the four task types defined in the blueprint
    type: Literal["1", "2", "3", "4"]
    description: str
    status: Literal["active", "pending", "completed"]
    actions: List[str]
    people: TaskPeople
    dependencies: List[str]
    schedule: str
    priority: Literal["high", "medium", "low"]


class Topic(BaseModel):
    """
    Model for storing knowledge base entries.
    """
    topic_id: str
    name: str
    description: str
    keywords: List[str]
    related_people: List[str]
    related_tasks: List[str]


class AffectedEntities(BaseModel):
    """
    Model for storing affected entities from the LLM response.
    """
    tasks: List[str] = Field(default_factory=list)
    people: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)


class Instructions(BaseModel):
    """
    Model for storing instructions from the LLM response.
    """
    status: Literal["incomplete", "complete"]
    followup: str
    new_prompt: str
    write: bool
    affected_entities: AffectedEntities


class Data(BaseModel):
    """
    Model for storing structured data from the LLM response.
    """
    tasks: List[Task] = Field(default_factory=list)
    people: List[Person] = Field(default_factory=list)
    topics: List[Topic] = Field(default_factory=list)


class LLMResponse(BaseModel):
    """
    Model for the complete LLM response, including instructions and data.
    """
    instructions: Instructions
    data: Data


# Load configuration and initialize OpenAI client
config = load_config()
client = OpenAI(api_key=config["openai_api_key"])


# Call OpenAI API with given messages
def call_openai_api(system_prompt, datastore, conversation_history,
                    verbose=False):
    """
    Call the OpenAI API with the given system prompt, datastore, and
    conversation history.
    Returns a structured LLMResponse object.
    """
    start_time = time.time()
    try:
        with console.status(
            "[bold green]Thinking...", spinner="dots"
        ) as status:
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "system",
                    "content": f"Datastore: {json.dumps(datastore)}",
                },
            ]
            messages.extend(conversation_history)

            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                response_format=LLMResponse,
            )

            end_time = time.time()
            elapsed_time = end_time - start_time

            status.update(
                f"[bold green]Completed in {elapsed_time:.2f} seconds"
            )
            time.sleep(1)  # Give users a moment to see the completion message

            token_summary = print_token_usage(completion.usage, verbose)
            console.print(
                f"[italic cyan]Sidekick took {elapsed_time:.2f} seconds to "
                f"respond. {token_summary}[/italic cyan]"
            )

            return completion.choices[0].message.parsed
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return None


# Process data received from the LLM
def process_data(data, affected_entities):
    """
    Process the data received from the LLM, updating the JSON files for
    people, tasks, and topics.
    """
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

    try:
        # Update people, tasks, and topics
        people, new_people, updated_people = update_or_add(
            people, [person.dict() for person in data.people], "person_id"
        )
        tasks, new_tasks, updated_tasks = update_or_add(
            tasks, [task.dict() for task in data.tasks], "task_id"
        )
        topics, new_topics, updated_topics = update_or_add(
            topics, [topic.dict() for topic in data.topics], "topic_id"
        )

        # Save updated data to JSON files
        save_json_file("people.json", people)
        save_json_file("tasks.json", tasks)
        save_json_file("topics.json", topics)

        # Print updates to console only if there are writes
        if affected_entities.people:
            print_updates("contact", new_people, updated_people)
        if affected_entities.tasks:
            print_updates("task", new_tasks, updated_tasks)
        if affected_entities.topics:
            print_updates("topic", new_topics, updated_topics)

    except Exception as e:
        console.print(f"[bold red]Error processing data:[/bold red] {str(e)}")
        console.print("No changes were made to the data files.")


# Print token usage information
def print_token_usage(usage, verbose=False):
    """
    Print the token usage information from the API response
    and return a summary string.
    """
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens
    cached_tokens = usage.prompt_tokens_details.cached_tokens
    cached_percentage = (cached_tokens / prompt_tokens) * 100 \
        if prompt_tokens > 0 else 0

    summary = (f"{completion_tokens} tokens out, {prompt_tokens} tokens in "
               f"({cached_percentage:.1f}% cached)")

    if verbose:
        console.print("[bold cyan]Token Usage:[/bold cyan]")
        console.print(f"  Prompt tokens: {prompt_tokens}")
        console.print(f"  Completion tokens: {completion_tokens}")
        console.print(f"  Cached tokens: {cached_tokens}")
        console.print(f"  Total tokens: {total_tokens}")
        console.print(f"  Cached percentage: {cached_percentage:.1f}%")

    return summary


# Print updates to the console
def print_updates(entity_type, new_entries, updated_entries):
    """
    Print information about new and updated entries to the console.
    """
    for entry in new_entries:
        name = entry.get('name', entry.get('description', 'Unknown'))
        console.print(
            f"[bold green]Added a new {entity_type}:[/bold green] {name}"
        )
    for entry in updated_entries:
        name = entry.get('name', entry.get('description', 'Unknown'))
        console.print(
            f"[bold yellow]Updated {entity_type}:[/bold yellow] {name}"
        )


# Construct datastore for the LLM
def construct_datastore():
    """
    Construct the datastore by loading data from JSON files.
    """
    return {
        "people": load_json_file("people.json"),
        "tasks": load_json_file("tasks.json"),
        "topics": load_json_file("topics.json"),
    }


# Get a summary of tasks, people, and topics entries
def get_task_summary(verbose=False):
    """
    Get a summary of all tasks, people, and topics entries from the LLM.
    """
    datastore = construct_datastore()
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conversation_history = [
        {
            "role": "user",
            "content": f"Current date and time: {current_datetime}",
        },
        {
            "role": "user",
            "content": (
                "Provide an overview of all tasks, people, and topics entries."
            ),
        },
    ]

    response = call_openai_api(
        config["system_prompt"], datastore, conversation_history, verbose
    )

    return (
        response.instructions.followup
        if response
        else "Unable to summarize tasks at the moment."
    )


# Main function to run the Sidekick assistant
def main(verbose=False):
    """
    Main function to run the Sidekick assistant. Handles user interaction
    and LLM communication.
    """
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
            "Welcome to Sidekick!\nYour personal executive assistant",
            title="Sidekick",
            subtitle="Type 'exit' to quit",
        )
    )

    # Fetch and display initial task summary
    console.print("Fetching task summary...")
    task_summary = get_task_summary(verbose)

    markdown_summary = Markdown(task_summary)
    console.print(
        Panel(markdown_summary, title="Task Summary", border_style="blue")
    )

    # Main interaction loop
    while True:
        thread_indicator = f"[{thread_count}] " if thread_count > 0 else ""
        user_input = session.prompt(f"{thread_indicator}You: ")

        if user_input.lower() == "exit":
            break
        if user_input.strip() == "":
            continue
        conversation_history.append({"role": "user", "content": user_input})
        thread_count += 1

        datastore = construct_datastore()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversation_history.append(
            {
                "role": "system",
                "content": f"Current date and time: {current_datetime}",
            }
        )

        # Get response from LLM
        llm_response = call_openai_api(
            config["system_prompt"], datastore, conversation_history, verbose
        )
        if llm_response is None:
            console.print(
                "[bold red]An error occurred. Please try again.[/bold red]"
            )
            continue

        instructions = llm_response.instructions
        data = llm_response.data

        # Display LLM response
        markdown_followup = Markdown(instructions.followup)
        console.print(
            Panel(markdown_followup, title="Sidekick", border_style="blue")
        )

        conversation_history.append(
            {"role": "assistant", "content": llm_response.json()}
        )

        # Process data if the conversation is complete
        if instructions.status == "complete":
            try:
                process_data(data, instructions.affected_entities)
                conversation_history = []
                thread_count = 0
                console.print(
                    "[bold green]Thread completed. "
                    "Starting new conversation.[/bold green]"
                )

                if instructions.new_prompt:
                    console.print(
                        Panel(
                            instructions.new_prompt,
                            title="New Suggestion",
                            border_style="green",
                        )
                    )
            except Exception as e:
                console.print(
                    f"[bold red]Error processing data:[/bold red] {str(e)}"
                )
                console.print(
                    "The conversation will continue, but no changes were "
                    "made to the data."
                )


if __name__ == "__main__":
    # Load configuration and set OpenAI API key
    config = load_config()
    openai.api_key = config["openai_api_key"]

    # Add argument parsing for verbose flag
    parser = argparse.ArgumentParser(
        description="Sidekick: Your personal executive assistant"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()
    main(verbose=args.verbose)
