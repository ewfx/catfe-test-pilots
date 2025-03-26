import json
import re
import google.generativeai as genai
import os
from google.generativeai import GenerativeModel
from dotenv import load_dotenv
from utils import clean_extract_queries, run_queries

load_dotenv()

GENAI_API_KEY = os.getenv("GEMINI_API_KEY")  # 🔹 Replace with your key
genai.configure(api_key=GENAI_API_KEY)
model = GenerativeModel("gemini-1.5-flash")

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

generated_folder = "tests\generated_tests\Bank-Of-Bharat-BOB"


feature_files_content = ""
for filename in os.listdir(generated_folder):
    if filename.endswith(".feature"):  # Only process feature files
        with open(os.path.join(generated_folder, filename), "r", encoding="utf-8") as file:
            feature_files_content += f"\n### {filename} ###\n"  # Add filename for clarity
            feature_files_content += file.read() + "\n\n"

def generate_graph_queries(full_code):
    """ 
    Uses Gemini model to generate queries for creating dependency graph in neo4j database 
    """
    system_prompt = """
    You are a *Neo4j Query Generator* that parses code and outputs dependency graph queries. Follow these rules:
    1. *Only generate Neo4j Cypher queries*. No explanations, comments, or extra text.
    2. *One query per line*. No wrapping or multi-line strings.
    3. *Nodes to extract*:
    - API: Properties - endpoint, method, parameters, response
    - Entity: Properties - name, fields
    - Exception: Properties - name, message
    - Repository: Properties - name, entity
    - Service: Properties - name, functions
    - Request (from DTO): Properties - name, fields
    - Response (from DTO): Properties - name, fields
    4. *Relationships*:
    - API -[:CALLS]-> Service
    - API -[:THROWS]-> Exception
    - Service -[:USES]-> Repository
    - Repository -[:HAS]-> Entity
    - Service -[:THROWS]-> Exception
    - Service -[:ASKS]-> Request (new)
    - Service -[:GIVES]-> Response (new)
    5. *Strictly derive relationships from code*. No assumptions.

    """

    cypher_query = model.generate_content(f"{system_prompt}\nHere is the full Java code:\n{full_code}")
    cypher_query = clean_extract_queries(cypher_query.text)

    return cypher_query

def generate_modified_bdd(changes):
    system_prompt = """
    You are an AI expert in Behavior-Driven Development (BDD) and software testing. 
    Your task is to analyze the provided code changes and existing BDD feature files, 
    then update or generate new Gherkin-style BDD scenarios to ensure test coverage.    
    This is a summary of code modifications, including added, removed, or updated logic: 
    """
    modified_bdds = model.generate_content(f"{system_prompt}\n {changes}:\n these are the existing bdd test{feature_files_content}")
    return modified_bdds.text

def generate_dependency_graph(full_code):
    cypher_queries = generate_graph_queries(full_code)
    run_queries(URI,USERNAME,PASSWORD,cypher_queries)
    print("DEPENDENCY GRAPH GENERATED!!")

# ✅ STEP 3: Generate API Details using Gemini
def generate_api_details(full_code):
    """
    Uses Gemini model to extract API details from Java code.
    
    Args:
        full_code (str): Java code content.
    
    Returns:
        dict: Extracted API data.
    """
    system_prompt = """
    You are an AI expert in analyzing code of financial applications. Extract API details from the given codebase and return structured JSON output.

    Return JSON in this format:
    {
      "apis": [
        {
          "endpoint": "/transfer",
          "method": "POST",
          "parameters": [...],
          "responses": {...},
          "dependencies": [...],
          "description": "...",
          "businessRules": "..."
        }
      ]
    }
    """
    
    response = model.generate_content(f"{system_prompt}\nHere is the full Java code:\n{full_code}")

    try:
        response_json = re.sub(r'```json|```', '', response.text).strip()
        api_dict = json.loads(response_json)
        formatted_json = json.dumps(api_dict, indent=4)
        return formatted_json , api_dict
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON response. Returned as string.")
        return response

# ✅ STEP 4: Save API Details to JSON
def save_api_details(api_data, output_path):
    """
    Saves API details to a JSON file.
    
    Args:
        api_data (dict): API details from AI.
        output_path (str): Path to save JSON.
    """
    with open(output_path, "w") as f:
        json.dump(api_data, f, indent=4)
    print(f"✅ API details saved to {output_path}")

# ✅ STEP 5: Generate BDD Scenarios
def generate_bdd_scenarios(api_data):
    """
    Uses stored API details to generate BDD scenarios.
    
    Args:
        api_data (dict): Extracted API details.
    
    Returns:
        str: Generated BDD scenarios.
    """
    system_prompt = """
    You are an AI expert in Behavior-Driven Development (BDD). Based on the provided API details, generate Gherkin-style BDD scenarios.

    Example:
    Feature: Transfer Money
      Scenario: Successful Transfer
        Given a user with sufficient balance
        When they request a transfer of 100 USD
        Then the transfer should be successful
    """

    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{system_prompt}\nAPI Data:\n{api_data}")

    return response.text

def generate_step_definitions(feature_file):

    system_prompt =     """
    You are an expert in BDD automation testing using Cucumber with Java.
Task: Given the following Gherkin feature file, generate step definitions in a single StepDefinitions.java file.
Guidelines:

All step definitions should be implemented inside StepDefinitions.java.

Use dependency injection with Cucumber's @Before, @After, and @Given, @When, @Then annotations.

Call appropriate request methods from the Requests.java class for each step.

Ensure placeholders in Gherkin scenarios are mapped to method parameters correctly.

The step definitions should log appropriate messages for debugging.

Return responses appropriately for validation in assertion steps.
  
    Args:
        Gherkin feature file content.
    
    Returns:
        str: Generated Step Definitions file content.
    """

    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{system_prompt}\nFeature File:\n{feature_file}")

    return response.text

def generate_requests_file(step_definitions):

    system_prompt =     """
   System Role: You are an expert in writing Java-based API automation using REST Assured.
Task: Based on the step definitions from StepDefinitions.java, create a WalletRequests.java file that handles all API requests.
Guidelines:

Implement each API call in separate methods inside WalletRequests.java.

Use REST Assured for sending requests and handling responses.

Ensure reusability by keeping request parameters configurable.

Provide meaningful method names that align with their purpose.
  
    Args:
        StepDefinitions.java file content.
    
    Returns:
        str: Generated Requests.java file content.
    """

    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{system_prompt}\nStepDefinitions.java:\n{step_definitions}")

    return response.text
