import json
import os

def clean_and_format_django_fixture(input_filepath, output_filepath=None):
    """
    Reads a Django JSON fixture, removes problematic entries (like contenttypes),
    and writes the filtered data to a new (or the same) file, pretty-printed.

    Args:
        input_filepath (str): The path to the unformatted JSON fixture file.
        output_filepath (str, optional): The path where the cleaned and formatted
                                         JSON will be saved. If None, it will
                                         overwrite the input file.
    """
    if output_filepath is None:
        output_filepath = input_filepath

    # List of models to exclude from the fixture
    # These are usually managed by Django itself and cause conflicts if loaded
    models_to_exclude = [
        "contenttypes.contenttype",
        "auth.permission",
        "admin.logentry",
        "sessions.session",
        # Add any other models you want to exclude here, e.g.,
        # "auth.user" if you manage users separately or don't want them in fixtures
    ]

    print(f"Reading data from: {input_filepath}")
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {input_filepath}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {input_filepath}: {e}")
        print("The file might be corrupted or not valid JSON.")
        return

    # Filter out entries based on the 'model' field
    filtered_data = [
        item for item in data
        if "model" in item and item["model"].lower() not in models_to_exclude
    ]

    print(f"Filtered out {len(data) - len(filtered_data)} entries.")
    print(f"Writing cleaned and formatted data to: {output_filepath}")

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            # Use indent=2 for pretty-printing (2 spaces indentation)
            json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        print("File cleaned and formatted successfully!")
    except IOError as e:
        print(f"Error writing file to {output_filepath}: {e}")

# --- How to use this script ---
# 1. Save the code above into a Python file (e.g., clean_fixture.py)
#    in your Django project's root directory.

# 2. Update the input_json_path variable to point to your localandserver.json file.
#    Based on your previous messages, it seems to be:
#    '/Users/bahaaismail/Documents/GitHub/django_sample/localandserver.json'

# 3. Run the script from your terminal:
#    python clean_fixture.py

# Example usage:
if __name__ == "__main__":
    # IMPORTANT: Replace this with the actual path to your localandserver.json file
    input_json_path = '/Users/bahaaismail/Documents/GitHub/django_sample/localandserver.json'

    # You can choose to overwrite the original file (set output_json_path = None)
    # or save to a new file (e.g., 'localandserver_cleaned.json')
    output_json_path = input_json_path # Overwrite the original file
    # output_json_path = '/Users/bahaaismail/Documents/GitHub/django_sample/localandserver_cleaned.json' # Save to a new file

    clean_and_format_django_fixture(input_json_path, output_json_path)

