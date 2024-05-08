
# Literally to change the moves.txt file. 
# Should not be run really but it's here for reference.

def change_word():
    def replace_word(file_path, old_word, new_word):
        try:
            # Read the contents of the file
            with open(file_path, 'r') as file:
                content = file.read()

            # Replace all occurrences of the old word with the new word
            content = content.replace(old_word, new_word)

            # Write the modified content back to the file
            with open(file_path, 'w') as file:
                file.write(content)

            print(f"All instances of '{old_word}' have been replaced with '{new_word}' in the file.")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except IOError:
            print(f"An error occurred while processing the file: {file_path}")

    # Example usage
    file_path = './moves.txt'
    old_word = 'Summarize in 400 characters or less:'
    new_word = 'Summarize in 80 words or less:'

    replace_word(file_path, old_word, new_word)

change_word()