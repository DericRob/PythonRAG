from query_data import query_rag
from langchain_ollama import Ollama  # Corrected import

EVAL_PROMPT = """
Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Answer with 'true' or 'false') Does the actual response match the expected response? 
"""


def test_monopoly_rules():
    """Test if the RAG system can answer a question about Monopoly rules."""
    assert query_and_validate(
        question="How much total money does a player start with in Monopoly? (Answer with the number only)",
        expected_response="$1500",
    )


def test_ticket_to_ride_rules():
    """Test if the RAG system can answer a question about Ticket to Ride rules."""
    assert query_and_validate(
        question="How many points does the longest continuous train get in Ticket to Ride? (Answer with the number only)",
        expected_response="10 points",
    )


def query_and_validate(question: str, expected_response: str):
    """
    Query the RAG system and validate the response.
    
    Args:
        question: The question to ask
        expected_response: The expected response
        
    Returns:
        True if the response matches expectations, False otherwise
    """
    # Query the RAG system
    response_text, _ = query_rag(question)
    
    # Create a prompt to evaluate the response
    prompt = EVAL_PROMPT.format(
        expected_response=expected_response, actual_response=response_text
    )

    # Use Llama 3.2 to evaluate the response
    model = Ollama(model="llama3.2:3b")
    evaluation_results_str = model.invoke(prompt)
    evaluation_results_str_cleaned = evaluation_results_str.strip().lower()

    print("\n--- EVALUATION ---")
    print(prompt)

    if "true" in evaluation_results_str_cleaned:
        # Print response in Green if it is correct
        print("\033[92m" + f"Result: {evaluation_results_str_cleaned}" + "\033[0m")
        return True
    elif "false" in evaluation_results_str_cleaned:
        # Print response in Red if it is incorrect
        print("\033[91m" + f"Result: {evaluation_results_str_cleaned}" + "\033[0m")
        return False
    else:
        raise ValueError(
            f"Invalid evaluation result. Cannot determine if 'true' or 'false': {evaluation_results_str_cleaned}"
        )