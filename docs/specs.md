# **Updated Project Specification: Sidekick – Your Executive Assistant**

## **Introduction**

Sidekick is an intelligent personal assistant for executives, functioning as a second brain to enhance productivity and reliability. This updated specification refines the implementation plan based on the current system prompt and main.py file, focusing on a JSON-based interaction model and local file storage.

## **Objectives**

- **Natural Language Interaction**: Enable users to communicate with Sidekick using natural language inputs.
- **Intelligent Processing**: Utilize a Large Language Model (LLM) to interpret inputs, classify them, and extract structured information.
- **JSON-based Communication**: Implement a standardized JSON structure for all interactions between the user, Sidekick, and the LLM.
- **Local Document Management**: Store and manage data in structured JSON files within the same folder as the agent.
- **Task, People, and Context Management**: Efficiently handle tasks, contacts, and contextual information.
- **Workflow Automation**: Define specific workflows for major actions, utilizing the LLM for intelligent processing.

## **System Architecture**

### **1. Core Components**

- **Command-Line Interface (CLI)**: The primary interface for user interaction.
- **LLM Integration**: Utilizes OpenAI's GPT-4 or GPT-3.5-turbo for natural language processing.
- **Local Storage**: JSON files for storing tasks, people, and context information.
- **Configuration Management**: YAML file for storing API keys and system prompts.

### **2. File Structure**

- `main.py`: The main application file.
- `config.yaml`: Configuration file for API keys and system prompts.
- `tasks.json`: Stores all task entries.
- `people.json`: Stores all people profiles.
- `topics.json`: Stores all context/knowledge base entries.

### **3. Data Models**

#### Task
```json
{
  "task_id": "<unique_identifier>",
  "type": "<1|2|3|4>",
  "description": "<task_description>",
  "status": "<active|pending|completed>",
  "actions": ["<action1>", "<action2>", ...],
  "people": {
    "owner": "<name>",
    "final_beneficiary": "<name>",
    "stakeholders": ["<name1>", "<name2>", ...]
  },
  "dependencies": ["<dependency1>", "<dependency2>", ...],
  "schedule": "<YYYY-MM-DD HH:MM>",
  "priority": "<high|medium|low>"
}
```

#### Person
```json
{
  "person_id": "<unique_identifier>",
  "name": "<full_name>",
  "designation": "<job_title>",
  "relationship": "<relationship_to_user>",
  "importance": "<high|medium|low>",
  "notes": "<additional_information>",
  "contact": {
    "email": "<email_address>",
    "phone": "<phone_number>"
  }
}
```

#### Knowledge
```json
{
  "knowledge_id": "<unique_identifier>",
  "topic": "<topic_name>",
  "description": "<detailed_description>",
  "keywords": ["<keyword1>", "<keyword2>", ...],
  "related_people": ["<person_name1>", "<person_name2>", ...],
  "related_tasks": ["<task_id1>", "<task_id2>", ...]
}
```

## **Interaction Flow**

1. **User Input**: The user enters a natural language query or command.
2. **Context Gathering**: Sidekick loads the current context from local JSON files.
3. **LLM Processing**: The input and context are sent to the LLM for processing.
4. **Response Generation**: The LLM generates a structured JSON response.
5. **Data Update**: If necessary, Sidekick updates the local JSON files with new or modified information.
6. **User Feedback**: Sidekick presents the processed information or actions to the user.

## **Key Functionalities**

### **1. Natural Language Processing**

- Sidekick uses the LLM to interpret the user's natural language inputs.
- The system classifies inputs into categories: Task, Person, Knowledge, Advice, or Browse.
- Relevant information is extracted to populate the structured data models.

### **2. Task Management**

- Create, update, and list tasks with various attributes (type, priority, schedule, etc.).
- Automatically assign task IDs and manage task dependencies.
- Provide task summaries and prioritized to-do lists.

### **3. Contact Management**

- Add and update contact information for people relevant to the executive's work.
- Associate people with tasks and contexts.
- Manage relationship information and importance levels.

### **4. Context/Knowledge Management**

- Store and retrieve contextual information related to projects, topics, or domains.
- Link contexts with relevant tasks and people.
- Provide quick access to important information during decision-making processes.

### **5. Intelligent Recommendations**

- Offer task prioritization based on deadlines, importance, and dependencies.
- Suggest next actions or focus areas based on the current context and workload.
- Provide reminders for upcoming deadlines or important events.

## **Implementation Details**

### **1. Configuration Management**

- Use `config.yaml` to store the OpenAI API key and system prompt.
- Load configuration at application startup.

### **2. LLM Integration**

- Utilize OpenAI's API to interact with GPT-4 or GPT-3.5-turbo.
- Construct prompts that include the current context and user input.
- Parse LLM responses and extract structured data.

### **3. Data Persistence**

- Use JSON files (`tasks.json`, `people.json`, `knowledge.json`) for local storage.
- Implement functions to load, update, and save data to these files.
- Ensure data integrity and handle concurrent access if needed.

### **4. User Interface**

- Implement a command-line interface using the `prompt_toolkit` library.
- Display formatted output using the `rich` library for enhanced readability.
- Provide visual indicators for processing status and data updates.

### **5. Error Handling and Logging**

- Implement robust error handling for API calls and data processing.
- Provide clear error messages to the user.
- Log errors and important events for debugging and auditing.

## **Workflows**

### **1. Adding a New Task**

1. User provides task details in natural language.
2. Sidekick processes the input through the LLM.
3. LLM extracts task information and suggests a structured task object.
4. Sidekick presents the extracted information to the user for confirmation.
5. Upon confirmation, Sidekick adds the task to `tasks.json`.
6. Sidekick provides confirmation and any relevant follow-up questions.

### **2. Updating Existing Information**

1. User requests an update to a task, person, or knowledge entry.
2. Sidekick identifies the relevant entry using provided IDs or contextual information.
3. LLM processes the update request and suggests modifications.
4. Sidekick presents the proposed changes to the user for confirmation.
5. Upon confirmation, Sidekick updates the relevant JSON file.
6. Sidekick provides confirmation of the update.

### **3. Generating Reports or Summaries**

1. User requests a summary or report (e.g., task list, contact information).
2. Sidekick retrieves relevant information from JSON files.
3. LLM processes the data and generates a structured summary.
4. Sidekick presents the summary to the user in a formatted manner.

## **Future Enhancements**

- **GUI Development**: Create a graphical user interface for improved user experience.
- **Integration with External Tools**: Connect with calendars, email clients, and project management tools.
- **Advanced Analytics**: Implement data analysis features for productivity insights.
- **Mobile Application**: Develop a mobile version for on-the-go access.
- **Voice Interface**: Add voice recognition and synthesis for hands-free operation.

## **Conclusion**

This updated specification for Sidekick outlines a powerful, AI-driven executive assistant that leverages natural language processing and structured data management. By focusing on a JSON-based interaction model and local file storage, Sidekick provides a flexible and efficient solution for managing tasks, contacts, and contextual information. The system's ability to understand and process natural language inputs, combined with its structured data handling, positions it as a valuable tool for enhancing executive productivity and decision-making.