import ollama
import os

# Ensure the image exists
image_path = './hazard_test.jpg'
if not os.path.exists(image_path):
    print(f"Error: {image_path} not found!")
    exit()

print(f" Sending {image_path} to LLaVA for analysis...")

try:
    response = ollama.chat(model='llava', messages=[
      {
        'role': 'user',
        'content': 'Describe this image. Are there any safety hazards?',
        'images': [image_path]
      }
    ])
    print("\n--- AI REPORT ---")
    print(response['message']['content'])
except Exception as e:
    print(f"Error communicating with Ollama: {e}")