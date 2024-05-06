import json

# Define the input and output file paths
input_file_path = 'output.jsonl'
output_file_path = 'formatted_finetuning_output.jsonl'

# Initialize a list to hold the formatted entries
formatted_data = []

# Read the .jsonl file
with open(input_file_path, 'r') as file:
    lines = file.readlines()

# Process each line, assuming each prompt has a system, user, and assistant message in sequence
for i in range(0, len(lines), 3):
    system_line = json.loads(lines[i])
    user_line = json.loads(lines[i+1])
    assistant_line = json.loads(lines[i+2])
    
    # Ensure correct roles and sequence
    if system_line['role'] == 'system' and user_line['role'] == 'user' and assistant_line['role'] == 'assistant':
        # Format as per the provided structure
        formatted_entry = {
            "messages": [
                {"role": "system", "content": system_line['content']},
                {"role": "user", "content": user_line['content']},
                {"role": "assistant", "content": assistant_line['content']}
            ]
        }
        formatted_data.append(formatted_entry)

# Write the formatted data to a new JSONL file
with open(output_file_path, 'w') as outfile:
    for item in formatted_data:
        outfile.write(json.dumps(item) + '\n')

print("Data formatted and written to", output_file_path)
