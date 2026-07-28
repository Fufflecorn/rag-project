# workflow.py
# -----------
# This file improves retrieval quality using multi-step AI workflows.
#
# The retrieval quality problem:
# The quality of a RAG answer depends heavily on what gets retrieved.
# And what gets retrieved depends on how similar the query embedding is
# to the document embeddings. If the user's query is vague or uses
# different vocabulary than the documents, retrieval suffers.
#
# Two solutions:
#
# 1. Query rewriting: Use an LLM to rewrite the user's question into a
#    version that will produce a better embedding for semantic search.
#    "tell me about that database thing" → "How do relational databases
#    store and query structured data using SQL?"
#
# 2. Query decomposition: Some questions are actually multiple questions.
#    Split them up and retrieve separately, then combine the results.
#    This is called "multi-hop retrieval."

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL
from embeddings import embed_text
from vector_store import query_similar

_client = genai.Client(api_key=GEMINI_API_KEY)


def rewrite_query(original_query, conversation_context=""):
    """
    Use Gemini to rewrite the user's query for better semantic search.

    Args:
        original_query:      The user's original question.
        conversation_context: Recent conversation history (helps resolve
                              pronouns like "it" or "that").

    Returns:
        A rewritten query string, or the original if rewriting fails.
    """
    try:
        context_prompt = ""
        if conversation_context and conversation_context.strip():
            context_prompt = f"Recent Conversation History:\n{conversation_context}\n\n"

        prompt = f"""{context_prompt}User Question: "{original_query}"

Task: Rewrite the user question above to make it clear, specific, technical, and standalone so it works effectively for semantic search in a technical document database.
- If the question uses vague pronouns or references like "it", "that", "what else", or "more", resolve those references using the conversation history if available.
- Do NOT answer the question.
- Output ONLY the rewritten search query and nothing else."""

        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1),
        )

        rewritten = response.text.strip()

        # Validate response length and non-emptiness
        if rewritten and len(rewritten) <= 500:
            return rewritten
        return original_query

    except Exception:
        # Fallback to original query on any failure
        return original_query


def decompose_query(query):
    """
    Break a complex multi-part question into simpler sub-questions.

    Args:
        query: A question that may contain multiple distinct topics.

    Returns:
        A list of sub-question strings (up to 3), or [query] if it's
        already simple or if decomposition fails.
    """
    try:
        prompt = f"""User Question: "{query}"

Task: If the question above covers multiple distinct topics or asks multiple things, split it into 2 to 3 distinct, simple sub-questions (one per line). If the question is simple and focused on a single topic, return the question as-is on a single line.

Do not include any numbering, bullet points, introductory text, or extra explanation. Output only the sub-questions."""

        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1),
        )

        raw_lines = response.text.strip().split("\n")
        
        # Clean up lines, strip bullet points or numbers if model added them anyway
        sub_queries = []
        for line in raw_lines:
            cleaned = line.strip()
            # Remove leading numbers or symbols like "1. ", "- ", "* "
            while cleaned and (cleaned[0].isdigit() or cleaned[0] in [".", "-", "*", " "]):
                cleaned = cleaned.lstrip("0123456789.-* ")
            if len(cleaned) > 5:  # filter out empty or trivial strings
                sub_queries.append(cleaned)

        # Return at most 3 sub-questions, or fallback to [query]
        if sub_queries:
            return sub_queries[:3]
        return [query]

    except Exception:
        # Fallback to original query wrapped in a list
        return [query]


def multi_hop_retrieve(query, n_per_hop=2):
    """
    Retrieve documents for each sub-question and combine the results.

    Steps:
      1. Decompose the query into sub-questions
      2. Embed and search for each sub-question independently
      3. Combine results, removing duplicates

    Args:
        query:     The original complex query.
        n_per_hop: Documents to retrieve per sub-question.

    Returns:
        A deduplicated list of relevant document strings.
    """
    sub_queries = decompose_query(query)

    all_documents = []
    seen_documents = set()

    for sub_query in sub_queries:
        embedding = embed_text(sub_query)
        results = query_similar(embedding, n_per_hop)

        for doc in results["documents"][0]:
            if doc not in seen_documents:
                seen_documents.add(doc)
                all_documents.append(doc)

    return all_documents
