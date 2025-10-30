from pinecone_plugins.assistant.models.chat import Message
from pinecone import Pinecone

import os
import dotenv

# Load environment variables from the correct path
dotenv.load_dotenv("../.env")
api_key: str = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

assistant = pc.assistant.Assistant(
    assistant_name="calhacks",
)

def query_assistant(
    user_query, person_id=None, conversation_id=None, start_time=None, end_time=None
):
    """
    user_query is the only required parameter.
    person_id, conversation_id, start_time, and end_time are optional parameters.
    if person_id is provided, the assistant will only search for conversations with that person.
    if conversation_id is provided, the assistant will only search for that conversation.
    if start_time is provided, the assistant will only search for conversations after that time.
    if end_time is provided, the assistant will only search for conversations before that time.
    if no parameters are provided, the assistant will search for all conversations.
    """
    msg = Message(role="user", content=user_query)
    # Build metadata filter only if at least one parameter is provided
    filter_conditions = []

    if person_id:
        filter_conditions.append({"person_id": person_id})

    if conversation_id:
        filter_conditions.append({"conversation_id": conversation_id})

    if start_time or end_time:
        created_at_filter = {}
        if start_time:
            created_at_filter["$gte"] = start_time
        if end_time:
            created_at_filter["$lte"] = end_time
        filter_conditions.append({"created_at": created_at_filter})

    # Only pass filter if we have conditions
    if filter_conditions:
        if len(filter_conditions) == 1:
            metadata_filter = filter_conditions[0]
        else:
            metadata_filter = {"$and": filter_conditions}
        response = assistant.chat(messages=[msg], filter=metadata_filter)
    else:
        response = assistant.chat(messages=[msg])
    return response["message"]["content"]

if __name__ == "__main__":
    response = query_assistant("Which school is Jennifer from?")
    print(response)