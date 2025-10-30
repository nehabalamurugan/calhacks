from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import dotenv
from get_pinecone_response import query_assistant

# Load environment variables
dotenv.load_dotenv("../.env")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication


@app.route("/")
def index():
    """Serve the main page"""
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def search():
    """
    Handle search queries with optional metadata filters

    Expected JSON payload:
    {
        "query": "user search query",
        "person_id": "optional person ID",
        "conversation_id": "optional conversation ID",
        "start_time": "optional start timestamp",
        "end_time": "optional end timestamp"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate required fields
        if not data or "query" not in data:
            return jsonify({"success": False, "error": "Query is required"}), 400

        user_query = data["query"]

        # Extract optional filter parameters
        person_id = data.get("person_id")
        conversation_id = data.get("conversation_id")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        # Validate time parameters if provided
        if start_time and not isinstance(start_time, (int, float)):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "start_time must be a timestamp (number)",
                    }
                ),
                400,
            )

        if end_time and not isinstance(end_time, (int, float)):
            return (
                jsonify(
                    {"success": False, "error": "end_time must be a timestamp (number)"}
                ),
                400,
            )

        # Query the assistant with filters
        response_content = query_assistant(
            user_query=user_query,
            person_id=person_id,
            conversation_id=conversation_id,
            start_time=start_time,
            end_time=end_time,
        )
        
        # The response from query_assistant is a string, not a dict
        # For now, just return the message content
        return jsonify(
            {
                "success": True,
                "message": response_content if isinstance(response_content, str) else str(response_content),
                "results": [],
                "query": user_query,
                "filters_applied": {
                    "person_id": person_id,
                    "conversation_id": conversation_id,
                    "start_time": start_time,
                    "end_time": end_time,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"Search failed: {str(e)}"}), 500


@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    """
    Retrieve all conversations sorted by date (newest first)

    Optional query parameters:
    - limit: Number of conversations to return (default: 50)
    - offset: Number of conversations to skip (default: 0)
    """
    try:
        # Get query parameters
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        # Validate parameters
        if limit < 1 or limit > 100:
            return (
                jsonify({"success": False, "error": "Limit must be between 1 and 100"}),
                400,
            )

        if offset < 0:
            return (
                jsonify({"success": False, "error": "Offset must be non-negative"}),
                400,
            )

        # Query conversations from Supabase using direct HTTP requests
        import requests
        
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        # Use direct HTTP requests to Supabase REST API
        api_url = f"{url}/rest/v1/conversations"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        # Query with joins
        params = {
            "select": "id,created_at,turns,person_id,people(name,affiliation)",
            "limit": limit,
            "offset": offset,
            "order": "created_at.desc"
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        conversations_result = response.json()

        if conversations_result is None:
            conversations_result = []

        # Format the response
        formatted_conversations = []
        for conv in conversations_result:
            # Extract person name and affiliation
            person_info = conv.get("people", {})
            person_name = (
                person_info.get("name", "Unknown") if person_info else "Unknown"
            )
            person_affiliation = (
                person_info.get("affiliation", "") if person_info else ""
            )

            # Format turns for display (show first few exchanges)
            turns = conv.get("turns", [])
            preview_turns = turns[:4] if turns else []  # Show first 4 exchanges

            # Format turns with proper speaker labels
            formatted_turns = []
            for turn in turns:
                speaker = turn.get("speaker", "Unknown")
                content = turn.get("text", "")

                # Determine speaker label and styling
                if "ina" in speaker.lower():
                    speaker_label = "Ina"
                    speaker_type = "person"
                elif "speaker_b" in speaker.lower():
                    speaker_label = ""  # No label for other person
                    speaker_type = "other"
                else:
                    speaker_label = speaker  # Show actual name
                    speaker_type = "person"

                formatted_turns.append(
                    {
                        "content": content,
                        "speaker_label": speaker_label,
                        "speaker_type": speaker_type,
                    }
                )

            formatted_conversations.append(
                {
                    "id": conv["id"],
                    "created_at": conv["created_at"],
                    "person_id": conv["person_id"],
                    "person_name": person_name,
                    "person_affiliation": person_affiliation,
                    "turns_preview": formatted_turns,
                    "total_turns": len(turns),
                    "has_more_turns": len(turns) > 4,
                }
            )

        return jsonify(
            {
                "success": True,
                "conversations": formatted_conversations,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "count": len(formatted_conversations),
                },
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Failed to retrieve conversations: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/people", methods=["GET"])
def get_people():
    """Retrieve all people from Supabase"""
    try:
        import requests
        
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        # Use direct HTTP requests to Supabase REST API
        api_url = f"{url}/rest/v1/people"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "select": "id,name,affiliation"
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        people_result = response.json()
        
        if people_result is None:
            people_result = []
        
        # Format the response
        formatted_people = []
        for person in people_result:
            formatted_people.append({
                "id": person["id"],
                "name": person["name"],
                "company": person.get("affiliation", "Unknown")
            })
        
        return jsonify({
            "success": True,
            "people": formatted_people
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve people: {str(e)}"
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "CalHacks Search Backend"})


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=5001)
