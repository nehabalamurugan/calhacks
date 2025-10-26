import os
import json
from datetime import datetime, timezone
import dotenv
from supabase import create_client, Client
from deepface import DeepFace
import numpy as np

# Load environment variables
dotenv.load_dotenv("/home/babapi/calhacks/.env")
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(url, key)


def create_face_embedding(image_path):
    """
    Create face embedding using DeepFace represent
    Returns: List of 512 float values (embedding vector)
    """
    try:
        print(f"Creating embedding for {image_path}...")
        embedding_objs = DeepFace.represent(
            img_path=image_path,
            model_name="Facenet512",  # This model produces 512-dim embeddings
            max_faces=1,
            enforce_detection=False,
        )

        # Get the first face embedding (512 dimensions)
        embedding = embedding_objs[0]["embedding"]
        # unit norm the embedding
        embedding = embedding / np.linalg.norm(embedding)

        # Convert numpy array to Python list for JSON serialization
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        print(f"Embedding type: {type(embedding)}")
        print(f"Embedding length: {len(embedding)}")
        return embedding

    except Exception as e:
        print(f"Error creating embedding: {e}")
        return None


def create_fake_conversation_turns():
    """
    Create fake conversation turns for testing
    Returns: List of turn objects in format [{"speaker": "content"}, ...]
    """
    turns = [
        {"person": "Hello, how are you doing today?"},
        {"system": "I'm doing great, thank you for asking! How can I help you today?"},
        {"person": "I was wondering about the weather forecast for this weekend."},
        {
            "system": "I'd be happy to help with that! Let me check the latest weather data for you."
        },
        {"person": "That would be really helpful, thank you!"},
        {"system": "You're welcome! I'll get that information for you right away."},
    ]
    return turns


def process_conversation_with_supabase(embedding, turns):
    """
    Process conversation by calling Supabase functions
    This simulates what the serverless function would do
    """
    try:
        print("Processing conversation with Supabase...")

        # 1. Search for similar people
        print("Searching for similar people...")
        similar_people_result = supabase.rpc(
            "find_similar_people",
            {"input_embedding": embedding, "similarity_threshold": 0.3},
        ).execute()

        print(f"Similar people search result: {similar_people_result.data}")

        person_id = None

        if similar_people_result.data and len(similar_people_result.data) > 0:
            # Person found - update their embedding
            person_id = similar_people_result.data[0]["person_id"]
            print(f"Found existing person: {person_id}")

            # Update running average embedding
            print("Updating person embedding...")
            update_result = supabase.rpc(
                "update_person_embedding",
                {"person_uuid": person_id, "new_embedding": embedding},
            ).execute()

            print(f"Update result: {update_result.data}")

        else:
            # No person found - create new person
            print("No similar person found, creating new person...")
            new_person_result = (
                supabase.table("people")
                .insert(
                    {
                        "embedding": embedding,
                        "times_interacted": 1,
                        "name": "Test User",
                        "notes": "Created from test script",
                    }
                )
                .execute()
            )

            person_id = new_person_result.data[0]["id"]
            print(f"Created new person: {person_id}")

        # 2. Insert conversation
        print("Inserting conversation...")
        conversation_result = (
            supabase.table("conversations")
            .insert(
                {
                    "person_id": person_id,
                    "turns": turns,
                    "embedding": embedding,
                }
            )
            .execute()
        )
        isoformattime = conversation_result.data[0]["created_at"]
        dt = datetime.fromisoformat(isoformattime)
        timestamp_unix = dt.timestamp()
        print(f"Conversation inserted: {conversation_result.data[0]['id']}")
        return {
            "success": True,
            "person_id": person_id,
            "conversation_id": conversation_result.data[0]["id"],
            "created_at":timestamp_unix,
        }

    except Exception as e:
        print(f"Error processing conversation: {e}")
        return {"success": False, "error": str(e)}


def main():
    """
    Main function to test the complete pipeline
    """
    print("=== CalHacks 2025 - Supabase + DeepFace Test ===")

    # 1. Create face embedding from pic1.jpg
    image_path = "images/pic5.jpg"
    embedding = create_face_embedding(image_path)

    if embedding is None:
        print("Failed to create embedding. Exiting.")
        return

    # 2. Create fake conversation turns
    turns = create_fake_conversation_turns()
    print(f"Created {len(turns)} conversation turns")

    # 3. Process conversation with Supabase
    result = process_conversation_with_supabase(embedding, turns)

    if result["success"]:
        print(f"\n✅ SUCCESS!")
        print(f"Person ID: {result['person_id']}")
        print(f"Conversation ID: {result['conversation_id']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")

    # 4. Test querying the data
    print("\n=== Testing Data Retrieval ===")
    try:
        # Get all people
        people_result = supabase.table("people").select("*").execute()
        print(f"Total people in database: {len(people_result.data)}")

        # Get all conversations
        conversations_result = supabase.table("conversations").select("*").execute()
        print(f"Total conversations in database: {len(conversations_result.data)}")

        # Get conversations for the person we just created/updated
        if result["success"]:
            person_conversations = (
                supabase.table("conversations")
                .select("*")
                .eq("person_id", result["person_id"])
                .execute()
            )
            print(
                f"Conversations for person {result['person_id']}: {len(person_conversations.data)}"
            )

    except Exception as e:
        print(f"Error querying data: {e}")


if __name__ == "__main__":
    main()

