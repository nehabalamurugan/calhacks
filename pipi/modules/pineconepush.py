from pinecone import Pinecone

import os
import dotenv

dotenv.load_dotenv("/home/babapi/calhacks/.env")
api_key: str = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

assistant = pc.assistant.Assistant(
    assistant_name="calhacks",
)


def upload_transcript(path_to_transcript, person_id, conversation_id, created_at_unix_ts):
    response = assistant.upload_file(
        file_path=path_to_transcript,
        timeout=None,
        metadata={
            "person_id": person_id,
            "conversation_id": conversation_id,
            "created_at": created_at_unix_ts,
        },
    )
    return response


