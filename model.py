from transformers import RagTokenizer, RagTokenForGeneration
import json
from rapidfuzz import process

# Initialize the tokenizer and model
tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq")

# Load the local knowledge base
with open("cooking_knowledge.json", "r") as f:
    knowledge_base = json.load(f)

def get_answer(question):
    # Use fuzzy matching to search the knowledge base
    matches = process.extract(question, [entry["question"] for entry in knowledge_base], limit=1)
    if matches and matches[0][1] > 70:  # Adjust the score threshold as needed
        matched_question = matches[0][0]
        for entry in knowledge_base:
            if entry["question"] == matched_question:
                answer = entry["answer"]
                # Add context-sensitive responses based on topic
                if entry["topic"] == "substitution":
                    answer += " Let me know if you'd like more information on substitutions!"
                elif entry["topic"] == "recipe":
                    answer += " Enjoy cooking, and let me know if you need more recipes!"
                elif entry["topic"] == "cooking_technique":
                    answer += " Try it out and let me know how it goes!"
                return answer

    # Generate an answer using RAG if no match is found
    inputs = tokenizer(question, return_tensors="pt")
    generated = model.generate(**inputs)
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
