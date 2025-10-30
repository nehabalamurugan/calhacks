# we will take conversations from the supabase db that have not already been embedded into text and embed them 
# into chunks and store them in an elastic ai vector db
# when we ask questions using a serverless endpoint from supabase db we will search the vector db for the most relevant chunks 
# and return the answer which should contain the metadata of the person id and the conversation id

from elasticsearch import Elasticsearch, helpers
client = Elasticsearch(
    "https://my-elasticsearch-project-eecd91.es.us-west-2.aws.elastic.cloud:443",
    api_key="aFI1c0hwb0JoNG5DMGl6Vm5aekg6RlVkdHRjOW44amRoWEtjRlZ5MzVsUQ==",
)
index_name = "conversation-chunks"
docs = [
    {
        "chunks": "Yellowstone National Park is one of the largest national parks in the United States. It ranges from the Wyoming to Montana and Idaho, and contains an area of 2,219,791 acress across three different states. Its most famous for hosting the geyser Old Faithful and is centered on the Yellowstone Caldera, the largest super volcano on the American continent. Yellowstone is host to hundreds of species of animal, many of which are endangered or threatened. Most notably, it contains free-ranging herds of bison and elk, alongside bears, cougars and wolves. The national park receives over 4.5 million visitors annually and is a UNESCO World Heritage Site.",
        "conversation_id": "sample-keyword-conversation_id",
        "created_at": None,
        "person_id": "sample-keyword-person_id",
        "semantic_text": "Yellowstone National Park is one of the largest national parks in the United States. It ranges from the Wyoming to Montana and Idaho, and contains an area of 2,219,791 acress across three different states. Its most famous for hosting the geyser Old Faithful and is centered on the Yellowstone Caldera, the largest super volcano on the American continent. Yellowstone is host to hundreds of species of animal, many of which are endangered or threatened. Most notably, it contains free-ranging herds of bison and elk, alongside bears, cougars and wolves. The national park receives over 4.5 million visitors annually and is a UNESCO World Heritage Site."
    },
    {
        "chunks": "Yosemite National Park is a United States National Park, covering over 750,000 acres of land in California. A UNESCO World Heritage Site, the park is best known for its granite cliffs, waterfalls and giant sequoia trees. Yosemite hosts over four million visitors in most years, with a peak of five million visitors in 2016. The park is home to a diverse range of wildlife, including mule deer, black bears, and the endangered Sierra Nevada bighorn sheep. The park has 1,200 square miles of wilderness, and is a popular destination for rock climbers, with over 3,000 feet of vertical granite to climb. Its most famous and cliff is the El Capitan, a 3,000 feet monolith along its tallest face.",
        "conversation_id": "sample-keyword-conversation_id",
        "created_at": None,
        "person_id": "sample-keyword-person_id",
        "semantic_text": "Yosemite National Park is a United States National Park, covering over 750,000 acres of land in California. A UNESCO World Heritage Site, the park is best known for its granite cliffs, waterfalls and giant sequoia trees. Yosemite hosts over four million visitors in most years, with a peak of five million visitors in 2016. The park is home to a diverse range of wildlife, including mule deer, black bears, and the endangered Sierra Nevada bighorn sheep. The park has 1,200 square miles of wilderness, and is a popular destination for rock climbers, with over 3,000 feet of vertical granite to climb. Its most famous and cliff is the El Capitan, a 3,000 feet monolith along its tallest face."
    },
    {
        "chunks": "Rocky Mountain National Park  is one of the most popular national parks in the United States. It receives over 4.5 million visitors annually, and is known for its mountainous terrain, including Longs Peak, which is the highest peak in the park. The park is home to a variety of wildlife, including elk, mule deer, moose, and bighorn sheep. The park is also home to a variety of ecosystems, including montane, subalpine, and alpine tundra. The park is a popular destination for hiking, camping, and wildlife viewing, and is a UNESCO World Heritage Site.",
        "conversation_id": "sample-keyword-conversation_id",
        "created_at": None,
        "person_id": "sample-keyword-person_id",
        "semantic_text": "Rocky Mountain National Park  is one of the most popular national parks in the United States. It receives over 4.5 million visitors annually, and is known for its mountainous terrain, including Longs Peak, which is the highest peak in the park. The park is home to a variety of wildlife, including elk, mule deer, moose, and bighorn sheep. The park is also home to a variety of ecosystems, including montane, subalpine, and alpine tundra. The park is a popular destination for hiking, camping, and wildlife viewing, and is a UNESCO World Heritage Site."
    }
]
# Test connection first
try:
    print("Testing Elasticsearch connection...")
    info = client.info()
    print(f"Connected to Elasticsearch: {info['version']['number']}")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Check if index exists
try:
    if client.indices.exists(index=index_name):
        print(f"Index '{index_name}' exists")
    else:
        print(f"Index '{index_name}' does not exist - creating it...")
        # Create index with basic mapping
        client.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "chunks": {"type": "text"},
                        "conversation_id": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "person_id": {"type": "keyword"},
                        "semantic_text": {"type": "text"}
                    }
                }
            }
        )
        print(f"Index '{index_name}' created successfully")
except Exception as e:
    print(f"Index operation failed: {e}")
    exit(1)

# Timeout to allow machine learning model loading and semantic ingestion to complete
ingestion_timeout=300
try:
    bulk_response = helpers.bulk(
        client.options(request_timeout=ingestion_timeout),
        docs,
        index=index_name
    )
    print(f"Bulk indexing successful: {bulk_response}")
except Exception as e:
    print(f"Bulk indexing failed: {e}")
    # Try to get more detailed error info
    try:
        bulk_response = helpers.bulk(
            client.options(request_timeout=ingestion_timeout),
            docs,
            index=index_name,
            raise_on_error=False
        )
        print(f"Bulk response with errors: {bulk_response}")
    except Exception as e2:
        print(f"Even detailed error handling failed: {e2}")