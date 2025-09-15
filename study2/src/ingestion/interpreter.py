import pandas as pd
from transformers import AutoProcessor, AutoModelForImageTextToText
from pathlib import Path
import torch
from typing import Optional
import os
import gc

class ImageInterpreter:
    """
    A class to generate responses using HuggingFace model based on a provided image and context.
    """
    def __init__(self, model_id: str, dev_message: str, base_prompt: str, api_key: Optional[str] = None):
        self.model_id = model_id
        self.dev_message = dev_message
        self.base_prompt = base_prompt
        self.api_key = api_key 
        self.responses = []
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32

        # --- HF Model Loading ---
        self.processor = AutoProcessor.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            token=self.api_key
        )
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            dtype=self.dtype,
            device_map="auto" if self.device == "cuda" else None,
            token=self.api_key,
        ).eval()

        if self.device == "cpu":
            self.model.to(self.device)

    def generate(self, image: str, context: Optional[str] = None, item_id: Optional[str] = None):
        """Generate response for a given image and optional context
        image: base64 encoded image string / url / local path
        context: optional textual context

        """

        # Prepare the prompt
        context_prompt = ""
        if context:
            context_prompt = (
                f"Additional textual context from the document where this image appears:\n\n{context}\n\n"
                "Use this context to ground your interpretation and enhance the accuracy of your explanation. "
            )
        
        prompt = self.base_prompt + context_prompt

        # Prepare messages for the Model

        messages = [
            { 
                "role": "system",
                    "content": [
                {"type": "text", "text": self.dev_message},
                ],
            },

            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "url": image},
                ],
            },
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(**inputs, max_new_tokens=256, temperature=0.6, do_sample=True)

        output_text = self.processor.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)

        self.responses.append({
            "item_id": item_id,
            "has_context": context is not None,
            "output_text": output_text
        })

        return output_text
    
    def clear_responses(self):
        """Clear stored responses to free memory"""
        self.responses = []

    def save_to_csv(self, filename="output.csv"):
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
    with open("config/dev_message.txt", "r") as f:
        dev_message = f.read()

    base_prompt = "Generate a clear, insightful, and informative interpretation of what the provided image reveals. "

    # Get the optional Hugging Face token from an environment variable
    hf_token = os.getenv("HUGGING_FACE_TOKEN")

    # Instantiate the generator, passing the optional token
    generator = ImageInterpreter(
        model_id="OpenGVLab/InternVL3_5-1B-HF",
        dev_message=dev_message,
        base_prompt=base_prompt,
        api_key=hf_token
    )

    # Load the full dataset
    full_dataset = pd.read_csv("data/processed/img-context-df.csv")

    # --- CONFIGURATION FOR A SINGLE RUN ---
    output_filename = "all_responses.csv"
    # Using a safe limit for context length to prevent memory spikes
    # If your hardware can handle more, set this to infinity
    MAX_CONTEXT_CHARS = 12000 

    print(f"--- Processing all {len(full_dataset)} rows. Output will be saved to {output_filename} ---")

    # Iterate over the entire dataset
    for idx, row in full_dataset.iterrows():
        try:
            image_path = row['image_path_1']
            context = row.get('image_context_1')
            item_id = row['article_name']

            # Truncate context if it's too long to prevent crashes
            if context and pd.notna(context) and len(context) > MAX_CONTEXT_CHARS:
                print(f"  [WARNING] Long context for {item_id}. Truncating from {len(context)} to {MAX_CONTEXT_CHARS} chars.")
                context = context[:MAX_CONTEXT_CHARS]
            
            print(f"  Processing item {idx+1}/{len(full_dataset)}: {item_id}")
            
            # Generate both with and without context
            generator.generate(image_path, context=context, item_id=item_id)
            generator.generate(image_path, context=None, item_id=item_id)

        except Exception as e:
            print(f"  [ERROR] Failed on item_id: {item_id}. Skipping.")
            print(f"  Error details: {e}")
            continue
    
    # Save all collected responses to a single file after the loop is complete
    print("\n--- All items processed. Saving results... ---")
    generator.save_to_csv(output_filename)

    print(f"--- Processing complete. All results saved to {output_filename} ---")