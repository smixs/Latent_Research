import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from termcolor import colored
import asyncio
from datetime import datetime
import shutil
import re
import sys
import locale

# Set up proper encoding for input/output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# CONSTANTS
MODEL = "google/gemini-2.0-pro-exp-02-05:free"
MAX_TOKENS = 2048  # Adjusted for Gemini Pro
BUDGET_TOKENS = 1600  # Adjusted for Gemini Pro
OUTPUT_DIR = "research_outputs"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_BASE = "https://openrouter.ai/api/v1"

# Configure OpenAI client for OpenRouter
client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENAI_API_BASE,
    default_headers={
        "HTTP-Referer": "https://github.com/yourusername/latent-research",  # Optional
        "X-Title": "Latent Research Assistant",  # Optional
    }
)

# System messages for generating research questions
QUESTION_GENERATOR_SYSTEM = """You are a research question generator. 
Your task is to analyze the user's input and generate exactly 3 different research questions that would help explore the topic more deeply.
Each question should approach the topic from a unique angle. 
Format your response with clear numbering and separate each question with a line break.
Start each question with "QUESTION 1:", "QUESTION 2:", and "QUESTION 3:" to make them easy to parse.
After providing the questions, provide a brief explanation of why each question is important.
RESPOND IN RUSSIAN LANGUAGE.
"""

# System messages for each researcher
SCIENTIFIC_SYSTEM = """You are a scientific researcher focused on empirical evidence and the natural world.
Approach the research question through the lens of physics, biology, chemistry, astronomy, or other natural sciences.
Provide specific scientific facts, theories, and empirical research relevant to the question.
Cite relevant research and scientific principles when appropriate.
Your goal is to provide a scientific understanding of the question based on our current knowledge.
RESPOND IN RUSSIAN LANGUAGE.
"""

PHILOSOPHICAL_SYSTEM = """You are a philosophical researcher examining fundamental questions about knowledge, reality, and existence.
Approach the research question through various philosophical traditions and frameworks.
Discuss relevant philosophical concepts, arguments, paradoxes, or thought experiments.
Reference major philosophical thinkers and schools of thought when appropriate.
Your goal is to provide a nuanced philosophical analysis that explores deeper meanings and implications.
RESPOND IN RUSSIAN LANGUAGE.
"""

MATHEMATICAL_SYSTEM = """You are a mathematical researcher focused on patterns, structures, and logical relationships.
Approach the research question through the lens of mathematics, statistics, logic, or computational thinking.
Explain relevant mathematical concepts, formulas, or models that could help answer the question.
Use precise mathematical reasoning and quantitative analysis when appropriate.
Your goal is to provide a rigorous, logical approach to understanding the question.
RESPOND IN RUSSIAN LANGUAGE.
"""

# Colors for display
SCIENTIFIC_COLOR = "green"
PHILOSOPHICAL_COLOR = "magenta"
MATHEMATICAL_COLOR = "cyan"
QUESTION_COLOR = "yellow"

def setup_environment():
    """Set up the environment for the application."""
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(colored(f"Created output directory: {OUTPUT_DIR}", "green"))
    except Exception as e:
        print(colored(f"Error setting up environment: {e}", "red"))
        exit(1)

def get_async_client():
    """Get the OpenRouter client configuration."""
    try:
        if not OPENROUTER_API_KEY:
            print(colored("OPENROUTER_API_KEY environment variable not set!", "red"))
            exit(1)
        return {}  # Возвращаем пустой словарь, так как заголовки уже установлены в клиенте
    except Exception as e:
        print(colored(f"Error initializing OpenRouter client: {e}", "red"))
        exit(1)

async def get_completion_with_thinking(messages, system=None):
    """Get completion from OpenRouter API with thinking simulation."""
    try:
        if system:
            messages = [{"role": "system", "content": system}] + messages

        completion = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS
        )
        
        # Simulate thinking content from the response
        thinking_content = f"Analyzing with {MODEL}..."
        response_content = completion.choices[0].message.content

        return {
            "thinking": thinking_content,
            "content": [{
                "type": "thinking",
                "thinking": thinking_content
            }, {
                "type": "text",
                "text": response_content
            }]
        }
    except Exception as e:
        print(colored(f"Error getting completion: {e}", "red"))
        return {
            "thinking": f"Error: {str(e)}",
            "content": [{
                "type": "text",
                "text": f"Error: {str(e)}"
            }]
        }

def save_research_to_json(research_data, session_id):
    """Save the research data to a JSON file."""
    try:
        filename = f"{OUTPUT_DIR}/research_session_{session_id}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(research_data, f, indent=2, ensure_ascii=False)
        
        print(colored(f"Saved research to {filename}", "green"))
    except Exception as e:
        print(colored(f"Error saving research to JSON: {e}", "red"))

def get_terminal_width():
    """Get the width of the terminal."""
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except Exception:
        return 120  # Default width if unable to determine

def format_for_column(text, column_width):
    """Format text to fit within a column."""
    lines = []
    current_line = ""
    
    for word in text.split():
        if len(current_line) + len(word) + 1 <= column_width:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line.ljust(column_width))
            current_line = word
    
    if current_line:
        lines.append(current_line.ljust(column_width))
    
    return lines

def print_side_by_side(scientific_text, philosophical_text, mathematical_text):
    """Print the three texts side by side in columns."""
    terminal_width = get_terminal_width()
    column_width = terminal_width // 3 - 2
    
    scientific_lines = format_for_column(scientific_text, column_width)
    philosophical_lines = format_for_column(philosophical_text, column_width)
    mathematical_lines = format_for_column(mathematical_text, column_width)
    
    # Ensure all columns have the same number of lines
    max_lines = max(len(scientific_lines), len(philosophical_lines), len(mathematical_lines))
    
    while len(scientific_lines) < max_lines:
        scientific_lines.append(" " * column_width)
    while len(philosophical_lines) < max_lines:
        philosophical_lines.append(" " * column_width)
    while len(mathematical_lines) < max_lines:
        mathematical_lines.append(" " * column_width)
    
    # Print header
    print("\n" + "=" * terminal_width)
    print(colored("SCIENTIFIC".center(column_width), SCIENTIFIC_COLOR) + " | " + 
          colored("PHILOSOPHICAL".center(column_width), PHILOSOPHICAL_COLOR) + " | " + 
          colored("MATHEMATICAL".center(column_width), MATHEMATICAL_COLOR))
    print("=" * terminal_width)
    
    # Print content
    for i in range(max_lines):
        print(colored(scientific_lines[i], SCIENTIFIC_COLOR) + " | " + 
              colored(philosophical_lines[i], PHILOSOPHICAL_COLOR) + " | " + 
              colored(mathematical_lines[i], MATHEMATICAL_COLOR))
    
    print("=" * terminal_width + "\n")

def extract_research_questions(text):
    """Extract the three research questions from the model's response."""
    questions = []
    
    # Look for questions with the specific format
    pattern = r"QUESTION\s+(\d):\s+(.*?)(?=QUESTION\s+\d:|$)"
    matches = re.finditer(pattern, text, re.DOTALL)
    
    for match in matches:
        question_num = match.group(1)
        question_text = match.group(2).strip()
        questions.append(question_text)
    
    # If regex didn't work, try simple line-based extraction as fallback
    if not questions:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("QUESTION") and ":" in line:
                question_text = line.split(":", 1)[1].strip()
                questions.append(question_text)
    
    return questions[:3]  # Return at most 3 questions

async def get_research_questions(topic):
    """Get research questions based on the topic."""
    try:
        print(colored("\nGenerating research questions...", "yellow"))
        
        messages = [{"role": "user", "content": f"Generate 3 research questions about: {topic}"}]
        response = await get_completion_with_thinking(messages, QUESTION_GENERATOR_SYSTEM)
        
        # Extract the three research questions
        questions = extract_research_questions(response["content"][1]["text"])
        
        # If we couldn't extract 3 questions, try again with a more explicit prompt
        if len(questions) < 3:
            print(colored("Trouble extracting questions, trying with a more explicit prompt...", "yellow"))
            
            messages = [{"role": "user", "content": f"Generate exactly 3 research questions about: {topic}. Format them as: 'QUESTION 1: [question]', 'QUESTION 2: [question]', 'QUESTION 3: [question]'."}]
            response = await get_completion_with_thinking(messages, QUESTION_GENERATOR_SYSTEM)
            
            questions = extract_research_questions(response["content"][1]["text"])
        
        # If we still don't have 3 questions, create placeholders
        while len(questions) < 3:
            questions.append(f"Additional research direction for {topic}")
        
        return {
            "thinking": response["thinking"],
            "response": response["content"][1]["text"],
            "questions": questions[:3]  # Ensure we only take 3 questions
        }
        
    except Exception as e:
        print(colored(f"Error generating research questions: {e}", "red"))
        return {
            "thinking": "Error occurred during question generation",
            "response": f"Error: {str(e)}",
            "questions": [
                f"Research aspect 1 of {topic}",
                f"Research aspect 2 of {topic}",
                f"Research aspect 3 of {topic}"
            ]
        }

async def get_research_response(question, system_message, researcher_type):
    """Get a research response for a specific question from a researcher."""
    try:
        print(colored(f"\nStarted {researcher_type} research on: {question[:50]}...", "yellow"))
        
        messages = [{"role": "user", "content": f"Research question: {question}"}]
        response = await get_completion_with_thinking(messages, system_message)
        
        print(colored(f"Completed {researcher_type} research on: {question[:50]}", "green"))
        
        if not response or "content" not in response or len(response["content"]) < 2:
            raise ValueError("Invalid response format from API")
            
        return {
            "thinking": response.get("thinking", f"Analyzing {researcher_type} perspective..."),
            "response": response["content"][1]["text"]
        }
        
    except Exception as e:
        error_msg = f"Error in {researcher_type} analysis: {str(e)}"
        print(colored(f"Error getting {researcher_type} response: {e}", "red"))
        return {
            "thinking": error_msg,
            "response": error_msg
        }

async def conduct_research(topic, session_id):
    """Conduct research on a topic from multiple perspectives."""
    # Get research questions
    questions_result = await get_research_questions(topic)
    
    # Display the generated questions
    terminal_width = get_terminal_width()
    print("\n" + "=" * terminal_width)
    print(colored("GENERATED RESEARCH QUESTIONS".center(terminal_width), QUESTION_COLOR, attrs=["bold"]))
    print("=" * terminal_width)
    
    for i, question in enumerate(questions_result["questions"]):
        print(colored(f"QUESTION {i+1}: {question}", QUESTION_COLOR))
    
    print("=" * terminal_width + "\n")
    
    # Initialize research data
    research_data = {
        "session_id": session_id,
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "questions_generation": {
            "response": questions_result["response"],
            "questions": questions_result["questions"]
        },
        "research_results": []
    }
    
    print(colored("\n🚀 LAUNCHING ALL RESEARCH TASKS IN PARALLEL...", "yellow", attrs=["bold"]))
    
    # Create all 9 tasks at once (3 questions × 3 perspectives)
    all_tasks = []
    task_info = []
    
    # Create all 9 tasks
    for i, question in enumerate(questions_result["questions"]):
        # Scientific perspective
        all_tasks.append(get_research_response(question, SCIENTIFIC_SYSTEM, "scientific"))
        task_info.append({
            "question_index": i,
            "perspective": "scientific",
            "color": SCIENTIFIC_COLOR
        })
        
        # Philosophical perspective
        all_tasks.append(get_research_response(question, PHILOSOPHICAL_SYSTEM, "philosophical"))
        task_info.append({
            "question_index": i,
            "perspective": "philosophical",
            "color": PHILOSOPHICAL_COLOR
        })
        
        # Mathematical perspective
        all_tasks.append(get_research_response(question, MATHEMATICAL_SYSTEM, "mathematical"))
        task_info.append({
            "question_index": i,
            "perspective": "mathematical",
            "color": MATHEMATICAL_COLOR
        })
    
    # Run all tasks concurrently
    print(colored("\n📊 RESEARCH PROGRESS DASHBOARD:", "white", attrs=["bold"]))
    print(colored("─" * terminal_width, "white"))
    
    # Print a header for the progress dashboard
    for i, question in enumerate(questions_result["questions"]):
        print(colored(f"Q{i+1}: ", "white", attrs=["bold"]) + colored(f"{question[:50]}...", "white"))
        print(colored(f"  ├─ {colored('Scientific', SCIENTIFIC_COLOR)}: ", "white") + colored("⏳ In progress", SCIENTIFIC_COLOR))
        print(colored(f"  ├─ {colored('Philosophical', PHILOSOPHICAL_COLOR)}: ", "white") + colored("⏳ In progress", PHILOSOPHICAL_COLOR))
        print(colored(f"  └─ {colored('Mathematical', MATHEMATICAL_COLOR)}: ", "white") + colored("⏳ In progress", MATHEMATICAL_COLOR))
    
    print(colored("─" * terminal_width, "white"))
    
    # Run all tasks and collect results
    results = await asyncio.gather(*all_tasks)
    
    # Organize results by question and perspective
    organized_results = {}
    for i, result in enumerate(results):
        q_idx = task_info[i]["question_index"]
        perspective = task_info[i]["perspective"]
        
        if q_idx not in organized_results:
            organized_results[q_idx] = {
                "question": questions_result["questions"][q_idx],
                "scientific": None,
                "philosophical": None,
                "mathematical": None
            }
        
        organized_results[q_idx][perspective] = result
    
    # Convert to list and sort by question index
    all_results = [organized_results[idx] for idx in sorted(organized_results.keys())]
    
    # Process and display results for each question
    print(colored("\n🏁 ALL RESEARCH COMPLETE! DISPLAYING RESULTS:", "green", attrs=["bold"]))
    
    for i, result in enumerate(all_results):
        question = result["question"]
        
        print(colored(f"\n📝 RESULTS FOR QUESTION {i+1}:", QUESTION_COLOR, attrs=["bold"]))
        print(colored(question, QUESTION_COLOR))
        print(colored("─" * terminal_width, QUESTION_COLOR))
        
        # Extract responses
        scientific_response = result["scientific"]["response"]
        philosophical_response = result["philosophical"]["response"]
        mathematical_response = result["mathematical"]["response"]
        
        # Print responses side by side
        print_side_by_side(scientific_response, philosophical_response, mathematical_response)
        
        # Add to research data
        research_data["research_results"].append({
            "question": question,
            "question_number": i+1,
            "scientific": {
                "response": scientific_response
            },
            "philosophical": {
                "response": philosophical_response
            },
            "mathematical": {
                "response": mathematical_response
            }
        })
    
    # Save the complete research data
    save_research_to_json(research_data, session_id)
    
    return research_data

def safe_input(prompt):
    """Safe input function that handles UTF-8 encoding properly."""
    try:
        return input(prompt)
    except UnicodeDecodeError:
        # If default encoding fails, try with utf-8
        return input(prompt.encode('utf-8').decode(locale.getpreferredencoding()))

async def main():
    """Main function to run the application."""
    setup_environment()
    
    # Generate a unique session ID
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Print welcome message
    terminal_width = get_terminal_width()
    print(colored("=" * terminal_width, "yellow"))
    print(colored("MULTI-PERSPECTIVE RESEARCH ASSISTANT".center(terminal_width), "yellow", attrs=["bold"]))
    print(colored(f"Session ID: {session_id}".center(terminal_width), "yellow"))
    print(colored("Type 'exit' to quit the application".center(terminal_width), "yellow"))
    print(colored("=" * terminal_width, "yellow"))
    
    while True:
        # Get user input using safe_input
        topic = safe_input(colored("\nEnter a research topic (or 'exit' to quit): ", "yellow"))
        if topic.lower() == 'exit':
            print(colored("Exiting application...", "yellow"))
            break
        
        if not topic.strip():
            print(colored("Please enter a valid topic", "yellow"))
            continue
        
        # Conduct research
        await conduct_research(topic, session_id)
        
        print(colored("\nResearch complete! You can enter another topic or type 'exit' to quit.", "yellow"))

if __name__ == "__main__":
    asyncio.run(main()) 