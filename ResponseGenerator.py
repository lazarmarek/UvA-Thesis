from openai import OpenAI
import os
import base64
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class ResponseGenerator:
    """
    A class to generate responses using OpenAI's API based on a provided image and context.
    """
    def __init__(self, api_key, model, dev_message, base_prompt):
        self.api_key = api_key
        self.model = model
        self.dev_message = dev_message
        self.base_prompt = base_prompt
        self.responses = []  # Store responses

        # Create responses directory
        self.responses_dir = Path("responses")
        self.responses_dir.mkdir(exist_ok=True)

    def generate(self, image, context=None, item_id=None):
        # Prepare the prompt with the base prompt and any additional context
        # If context is provided, include it in the prompt
        context_prompt = ""
        if context:
            context_prompt = (
                f"Additional textual context from the document where this image appears:\n\n{context}\n\n"
                "Use this context to ground your interpretation and enhance the accuracy of your explanation. "
            )
        
        prompt = self.base_prompt + context_prompt

        # Initialize the OpenAI client with the provided API key
        client = OpenAI()

        # Create a response using the OpenAI client
        response = client.responses.create(
            model=self.model,
            reasoning={"effort": "high"},
            instructions=self.dev_message,
            input=[

                { "role": "user","content": [
                        { "type": "input_text", "text": prompt },
                        { "type": "input_image", "image_url": f"data:image/jpeg;base64,{image}" }
                    ]
                }
            ]
        )

        # Save full response to JSON
        self.save_response_json(response, item_id, context is not None)

        # Store response
        self.responses.append({
            'item_id': item_id,
            'has_context': context is not None,
            'output_text': response.output_text
        })
        
        return response

    def save_response_json(self, response, item_id, has_context):
        """Save the full response to a JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        context_suffix = "with_context" if has_context else "without_context"
        filename = f"response_{item_id}_{context_suffix}_{timestamp}.json"
        filepath = self.responses_dir / filename
        
        # Extract the actual text from the nested structure
        output_text = ""
        if response.output and len(response.output) > 0:
            for output_item in response.output:
                if hasattr(output_item, 'content') and output_item.content:
                    for content_item in output_item.content:
                        if hasattr(content_item, 'text'):
                            output_text = content_item.text
                            break
        
        # Convert response to dict
        response_dict = {
            "timestamp": timestamp,
            "item_id": item_id,
            "has_context": has_context,
            "response_id": response.id,
            "created_at": response.created_at,
            "model": response.model,
            "output_text": output_text,
            "status": response.status,
            "usage": {
                "input_tokens": response.usage.input_tokens if response.usage else 0,
                "output_tokens": response.usage.output_tokens if response.usage else 0,
                "reasoning_tokens": response.usage.output_tokens_details.reasoning_tokens if response.usage and response.usage.output_tokens_details else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            "temperature": response.temperature,
            "prompt_used": self.prompt,
            "dev_message": self.dev_message
        }
        
        # Save to JSON with nice formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Full response saved to: {filepath}")
        return filepath
    
    def save_to_csv(self, filename="evaluation_data.csv"):
        """Create CSV with with_context and without_context columns"""
        data = {}
        
        # Group by item_id
        for resp in self.responses:
            item_id = resp['item_id']
            if item_id not in data:
                data[item_id] = {'item_id': item_id}
            
            if resp['has_context']:
                data[item_id]['with_context'] = resp['output_text']
            else:
                data[item_id]['without_context'] = resp['output_text']
        
        # Convert to DataFrame and save
        df = pd.DataFrame(list(data.values()))
        df.to_csv(filename, index=False)
        print(f"Saved to {filename}")

if __name__ == "__main__":
    # Example usage
    # Load the developer message & base prompt
    with open("dev_message.txt", "r") as f:
        dev_message = f.read()
    base_prompt = "Generate a clear, insightful, and informative interpretation of what the provided image reveals. "

    api_key = os.getenv("OPENAI_API_KEY")

    generator = ResponseGenerator(
        api_key=api_key,
        model="o4-mini",
        dev_message=dev_message,
        base_prompt=base_prompt
    )

    # Generate responses for dataset
    dataset = pd.read_csv("test_df.csv")
    for idx, row in dataset.iterrows():
        with open(row['image_path_1'], 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        generator.generate(image_data, context=row['image_context_1'], item_id=row['article_name'])  # with context
        generator.generate(image_data, context=None, item_id=row['article_name'])  # without context
    
    generator.save_to_csv("test.csv")
