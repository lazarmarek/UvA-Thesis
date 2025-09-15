from IPython.display import display, clear_output
from PIL import Image
import json
import pandas as pd

def generate_interactive_queries(image_paths: list, contexts: list) -> list:
    """
    A helper function to interactively display the images and their contexts,
    allowing the user to input custom queries for each image.
    """
    queries = []
    total = len(image_paths)
    print(f"--- Starting Interactive Query Generation for {total} images ---")
    print("Type 'quit' or 'exit' to stop early.")
    print("-" * 40)

    for i, path in enumerate(image_paths):
        clear_output(wait=True)
        print(f"Image {i+1}/{total}: {path}")
        try:
            display(Image.open(path))
            print(f"{contexts[i]}\n")

            query = input("Enter your query: ")
            
            if query.lower() in ['quit', 'exit']:
                break
            
            queries.append({'image_path': path, 'query': query})
        except Exception as e:
            print(f"\n[ERROR] Could not process image: {e}")
            if input("Press Enter to continue, or type 's' to stop: ").lower() == 's':
                break

    clear_output(wait=True)
    print(f"--- Query generation complete! Generated {len(queries)} queries. ---")
    return queries

if __name__ == "__main__":

    # Example usage
    df = pd.read_csv('./data/tbp_articles/img-context-df.csv')

    # Separate image paths and contexts into lists
    img_paths = df['image_path_1'].tolist()
    contexts = df['image_context_1'].tolist()

    # Display images & contexts and write your own queries
    queries = generate_interactive_queries(img_paths, contexts)

    # Save queries to a JSON file
    output_filename = "queries_filename.json"

    with open(output_filename, 'w') as f:
        # json.dump writes the Python list of dictionaries directly to the file.
        # indent=4 makes the file nicely formatted and human-readable.
        json.dump(queries, f, indent=4)

    print(f"Successfully saved {len(queries)} queries to {output_filename}")