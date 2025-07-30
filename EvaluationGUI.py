import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from PIL import Image, ImageTk
import os
import random
from pathlib import Path

class EvaluationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Context Evaluation Study")
        self.root.geometry("1400x900")
        
        # Data storage
        self.dataset = None
        self.current_index = 0
        self.results = []
        self.text_assignments = {}  # Track which text is which for each item
        
        # GUI setup
        self.setup_gui()
        
    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Load data button
        load_btn = ttk.Button(main_frame, text="Load Dataset", command=self.load_dataset)
        load_btn.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # Progress info
        self.progress_label = ttk.Label(main_frame, text="No dataset loaded")
        self.progress_label.grid(row=0, column=1, columnspan=2, pady=(0, 10))
        
        # Image display (left side)
        image_frame = ttk.LabelFrame(main_frame, text="Image", padding="10")
        image_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.image_label = ttk.Label(image_frame, text="No image loaded")
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # Text comparison frame (right side)
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text A frame (blinded)
        text_a_frame = ttk.LabelFrame(text_frame, text="Text A", padding="10")
        text_a_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        text_a_frame.columnconfigure(0, weight=1)
        text_a_frame.rowconfigure(0, weight=1)
        
        self.text_a = tk.Text(text_a_frame, wrap=tk.WORD, font=("Arial", 10))
        text_a_scroll = ttk.Scrollbar(text_a_frame, orient=tk.VERTICAL, command=self.text_a.yview)
        self.text_a.configure(yscrollcommand=text_a_scroll.set)
        self.text_a.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_a_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Text B frame (blinded)
        text_b_frame = ttk.LabelFrame(text_frame, text="Text B", padding="10")
        text_b_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        text_b_frame.columnconfigure(0, weight=1)
        text_b_frame.rowconfigure(0, weight=1)
        
        self.text_b = tk.Text(text_b_frame, wrap=tk.WORD, font=("Arial", 10))
        text_b_scroll = ttk.Scrollbar(text_b_frame, orient=tk.VERTICAL, command=self.text_b.yview)
        self.text_b.configure(yscrollcommand=text_b_scroll.set)
        self.text_b.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_b_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Evaluation frame
        eval_frame = ttk.LabelFrame(main_frame, text="Evaluation", padding="10")
        eval_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        eval_frame.columnconfigure(1, weight=1)
        eval_frame.columnconfigure(3, weight=1)
        
        # Likert scales
        self.setup_likert_scales(eval_frame)
        
        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        self.prev_btn = ttk.Button(nav_frame, text="Previous", command=self.previous_item, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_btn = ttk.Button(nav_frame, text="Next", command=self.next_item, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_btn = ttk.Button(nav_frame, text="Save Results", command=self.save_results, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT)
        
    def setup_likert_scales(self, parent):
        # Text A evaluation
        ttk.Label(parent, text="Text A Quality:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.text_a_vars = {}
        questions_a = [
            ("Accuracy", "How accurate is the description?"),
            ("Clarity", "How clear and understandable is the text?"),
            ("Relevance", "How relevant is the content to the image?"),
            ("Completeness", "How complete is the description?")
        ]
        
        for i, (key, question) in enumerate(questions_a):
            ttk.Label(parent, text=question).grid(row=i+1, column=0, sticky=tk.W, padx=(20, 0))
            
            var = tk.IntVar()
            self.text_a_vars[key] = var
            
            scale_frame = ttk.Frame(parent)
            scale_frame.grid(row=i+1, column=1, sticky=(tk.W, tk.E), padx=(10, 20))
            
            for j in range(1, 8):
                ttk.Radiobutton(scale_frame, text=str(j), variable=var, value=j).pack(side=tk.LEFT, padx=5)
        
        # Text B evaluation
        ttk.Label(parent, text="Text B Quality:", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky=tk.W, pady=(0, 5))
        
        self.text_b_vars = {}
        questions_b = [
            ("Accuracy", "How accurate is the description?"),
            ("Clarity", "How clear and understandable is the text?"),
            ("Relevance", "How relevant is the content to the image?"),
            ("Completeness", "How complete is the description?")
        ]
        
        for i, (key, question) in enumerate(questions_b):
            ttk.Label(parent, text=question).grid(row=i+1, column=2, sticky=tk.W, padx=(20, 0))
            
            var = tk.IntVar()
            self.text_b_vars[key] = var
            
            scale_frame = ttk.Frame(parent)
            scale_frame.grid(row=i+1, column=3, sticky=(tk.W, tk.E), padx=(10, 0))
            
            for j in range(1, 8):
                ttk.Radiobutton(scale_frame, text=str(j), variable=var, value=j).pack(side=tk.LEFT, padx=5)
        
        # Overall comparison
        ttk.Label(parent, text="Overall Preference:", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=4, sticky=tk.W, pady=(20, 5))
        ttk.Label(parent, text="Which text provides a better description overall?").grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        
        self.preference_var = tk.StringVar()
        pref_frame = ttk.Frame(parent)
        pref_frame.grid(row=6, column=2, columnspan=2, sticky=tk.W, padx=(10, 0))
        
        ttk.Radiobutton(pref_frame, text="Text A", variable=self.preference_var, value="A").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(pref_frame, text="Text B", variable=self.preference_var, value="B").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(pref_frame, text="No preference", variable=self.preference_var, value="Equal").pack(side=tk.LEFT, padx=10)
    
    def load_dataset(self):
        file_path = filedialog.askopenfilename(
            title="Select dataset CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.dataset = pd.read_csv(file_path)
                self.current_index = 0
                self.results = []
                self.text_assignments = {}
                
                # Validate required columns - adjust these based on your actual column names
                required_cols = ['image_path_1']  # Remove text_a, text_b requirement for now
                missing_cols = [col for col in required_cols if col not in self.dataset.columns]
                
                if missing_cols:
                    messagebox.showerror("Error", f"Missing required columns: {missing_cols}")
                    return
                
                # Generate random assignments for each item
                self.generate_text_assignments()
                
                self.load_current_item()
                self.update_navigation()
                
                messagebox.showinfo("Success", f"Loaded {len(self.dataset)} items for evaluation")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load dataset: {str(e)}")
    
    def generate_text_assignments(self):
        """Generate random assignments of with/without context to Text A/B for each item"""
        for i in range(len(self.dataset)):
            # Randomly assign which text gets context (True = with context, False = without context)
            text_a_has_context = random.choice([True, False])
            self.text_assignments[i] = {
                'text_a_has_context': text_a_has_context,
                'text_b_has_context': not text_a_has_context  # Ensure one has context, one doesn't
            }
    
    def load_current_item(self):
        if self.dataset is None or self.current_index >= len(self.dataset):
            return
        
        row = self.dataset.iloc[self.current_index]
        
        # Update progress
        self.progress_label.config(text=f"Item {self.current_index + 1} of {len(self.dataset)}")
        
        # Load image
        self.load_image(row['image_path_1'])
        
        # Load texts based on random assignment
        self.text_a.delete(1.0, tk.END)
        self.text_b.delete(1.0, tk.END)
        
        assignment = self.text_assignments[self.current_index]
        
        # You'll need to adjust these column names based on your actual dataset
        # Assuming you have columns like 'without_context' and 'with_context'
        text_without_context = row.get('without_context', '')
        text_with_context = row.get('with_context', '')
        
        # Assign texts based on randomization
        if assignment['text_a_has_context']:
            self.text_a.insert(1.0, str(text_with_context))
            self.text_b.insert(1.0, str(text_without_context))
        else:
            self.text_a.insert(1.0, str(text_without_context))
            self.text_b.insert(1.0, str(text_with_context))
        
        # Clear previous ratings
        self.clear_ratings()
    
    def load_image(self, image_path):
        try:
            if pd.notna(image_path) and os.path.exists(image_path):
                # Load and resize image
                pil_image = Image.open(image_path)
                # Resize to fit display area (adjust as needed)
                pil_image.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(pil_image)
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
            else:
                self.image_label.configure(image="", text=f"Image not found:\n{image_path}")
        except Exception as e:
            self.image_label.configure(image="", text=f"Error loading image:\n{str(e)}")
    
    def clear_ratings(self):
        for var in self.text_a_vars.values():
            var.set(0)
        for var in self.text_b_vars.values():
            var.set(0)
        self.preference_var.set("")
    
    def save_current_ratings(self):
        if self.dataset is None:
            return False
        
        # Check if all ratings are provided
        all_ratings_complete = True
        for var in list(self.text_a_vars.values()) + list(self.text_b_vars.values()):
            if var.get() == 0:
                all_ratings_complete = False
                break
        
        if not all_ratings_complete or not self.preference_var.get():
            messagebox.showwarning("Incomplete", "Please provide all ratings before proceeding.")
            return False
        
        # Get the assignment for this item
        assignment = self.text_assignments[self.current_index]
        
        # Save ratings with proper mapping to with/without context
        result = {
            'item_index': self.current_index,
            'preference': self.preference_var.get(),
            'text_a_has_context': assignment['text_a_has_context'],
            'text_b_has_context': assignment['text_b_has_context']
        }
        
        # Map Text A/B ratings to with/without context ratings
        for key, var in self.text_a_vars.items():
            if assignment['text_a_has_context']:
                result[f'with_context_{key.lower()}'] = var.get()
            else:
                result[f'without_context_{key.lower()}'] = var.get()
        
        for key, var in self.text_b_vars.items():
            if assignment['text_b_has_context']:
                result[f'with_context_{key.lower()}'] = var.get()
            else:
                result[f'without_context_{key.lower()}'] = var.get()
        
        # Map preference to actual text type
        if self.preference_var.get() == "A":
            if assignment['text_a_has_context']:
                result['preference_actual'] = 'with_context'
            else:
                result['preference_actual'] = 'without_context'
        elif self.preference_var.get() == "B":
            if assignment['text_b_has_context']:
                result['preference_actual'] = 'with_context'
            else:
                result['preference_actual'] = 'without_context'
        else:
            result['preference_actual'] = 'equal'
        
        # Update or append result
        existing_result = next((i for i, r in enumerate(self.results) if r['item_index'] == self.current_index), None)
        if existing_result is not None:
            self.results[existing_result] = result
        else:
            self.results.append(result)
        
        return True
    
    def next_item(self):
        if self.save_current_ratings():
            if self.current_index < len(self.dataset) - 1:
                self.current_index += 1
                self.load_current_item()
                self.update_navigation()
            else:
                # Last item - show completion message
                messagebox.showinfo("Complete", "All items evaluated! You can now save your results.")

    def previous_item(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_item()
            
            # Load previous ratings if they exist
            existing_result = next((r for r in self.results if r['item_index'] == self.current_index), None)
            if existing_result:
                self.load_ratings_from_result(existing_result)
            
            self.update_navigation()
    
    def load_ratings_from_result(self, result):
        # Get assignment for current item
        assignment = self.text_assignments[self.current_index]
        
        # Clear current ratings
        self.clear_ratings()
        
        # Load Text A ratings (map back from with/without context)
        for key, var in self.text_a_vars.items():
            if assignment['text_a_has_context']:
                if f'with_context_{key.lower()}' in result:
                    var.set(result[f'with_context_{key.lower()}'])
            else:
                if f'without_context_{key.lower()}' in result:
                    var.set(result[f'without_context_{key.lower()}'])
        
        # Load Text B ratings
        for key, var in self.text_b_vars.items():
            if assignment['text_b_has_context']:
                if f'with_context_{key.lower()}' in result:
                    var.set(result[f'with_context_{key.lower()}'])
            else:
                if f'without_context_{key.lower()}' in result:
                    var.set(result[f'without_context_{key.lower()}'])
        
        # Load preference
        if 'preference' in result:
            self.preference_var.set(result['preference'])
    
    def update_navigation(self):
        if self.dataset is None:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            self.save_btn.config(state=tk.DISABLED)
            return
        
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        
        # Change button text for last item
        if self.current_index >= len(self.dataset) - 1:
            self.next_btn.config(text="Submit & Finish", state=tk.NORMAL)
        else:
            self.next_btn.config(text="Next", state=tk.NORMAL)
        
        self.save_btn.config(state=tk.NORMAL)
    
    def save_results(self):
        if not self.results:
            messagebox.showwarning("No Results", "No evaluation results to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save evaluation results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                results_df = pd.DataFrame(self.results)
                results_df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Results saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EvaluationGUI(root)
    root.mainloop()