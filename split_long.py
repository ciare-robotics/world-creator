import json

def split_list(data, chunk_size):
    return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

def main():
    with open('output_models_name.json', 'r') as f:
        long_list = json.load(f)
    print(len(json.dumps(long_list)))
    max_message_size = 4096  # Maximum message size for OpenAI Chat API
    prompt_size = len(json.dumps(long_list))  # Calculate the size of the original list

    chunk_size = prompt_size // max_message_size  # Calculate the appropriate chunk size

    chunks = split_list(long_list, chunk_size)
    num_chunks = len(chunks)

    for i, chunk in enumerate(chunks):
        message = json.dumps(chunk)
        print(f"Processing Chunk {i+1}/{num_chunks}: {message}\n")  # Print or use the chunk as needed

    print("All chunks received. Starting chat GPT...")  # Indicate that all chunks have been received

if __name__ == '__main__':
    main()