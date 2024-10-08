import json
import os
import yaml
import openai

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()
openai.api_key = config['openai_api_key']

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
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo", depending on your preference
            messages=messages
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("Error: Unable to parse OpenAI response as JSON.")
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

    while True:
        user_input = input("Enter your command (or 'exit' to quit): ")
        
        if user_input.lower() == 'exit':
            break

        conversation_history.append({"role": "user", "content": user_input})

        context = {
            'people': load_json_file('people.json'),
            'tasks': load_json_file('tasks.json'),
            'topics': load_json_file('topics.json')
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current context: {json.dumps(context)}"}
        ] + conversation_history

        llm_response = call_openai_api(messages)

        if llm_response is None:
            print("An error occurred. Please try again.")
            continue

        instructions = llm_response['instructions']
        data = llm_response['data']

        print(f"Sidekick: {instructions['followup']}")

        conversation_history.append({"role": "assistant", "content": json.dumps(llm_response)})

        if instructions['status'] == 'complete':
            process_data(data)
            conversation_history = []  # Reset conversation history

if __name__ == "__main__":
    main()