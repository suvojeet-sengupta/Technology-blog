import os
import google.generativeai as genai
import json
from datetime import datetime
import re
import random

# --- Configuration ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")

genai.configure(api_key=API_KEY)

# --- MODEL UPDATED AS PER USER'S REQUEST ---
# Using the model name you provided.
# Note: If you face a "model not found" error, you can switch to 'gemini-1.5-pro-latest'.
text_model = genai.GenerativeModel('gemini-2.5-pro') # Reverted to Pro as a stable, powerful choice. If you specifically want 2.5, you can change it back.

# --- Helper Functions (No changes) ---
def slugify(text):
    """Converts a string to a URL-friendly slug."""
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def calculate_read_time(text):
    """Calculates the estimated reading time in minutes."""
    word_count = len(text.split())
    read_time_min = word_count / 200
    return max(1, round(read_time_min)) # Return at least 1 minute

import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate a new blog post for The Thinking Editor.")
    parser.add_argument("--topic", type=str, help="The blog topic to write about.")
    parser.add_argument("--category", type=str, help="The category for the blog topic.")
    args = parser.parse_args()

    print("🚀 The Thinking Editor AI Blog Generator Activated...")

    if args.topic and args.category:
        # --- Manual Mode: Get topic and category from arguments ---
        print("1. Running in Manual Mode with provided arguments.")
        blog_topic = args.topic
        category = args.category
        print(f"   - Manual Topic: {blog_topic}")
        print(f"   - Manual Category: {category}")
    else:
        # --- Automated Mode: Let Gemini decide the topic ---
        print("1. Holding editorial meeting with Gemini to decide today's topic...")
        try:
            # This new, smarter prompt asks Gemini to think like an editor.
            editorial_prompt = """
            You are the Editor-in-Chief for a top Indian tech and science blog. Your job is to decide today's article.
            You have two choices:
            1.  **A Trending Topic:** Pick a subject that is currently hot and making news in fields like AI, Space-Tech, Quantum Computing, Climate Tech, Biotech, or the Internet.
            2.  **An Evergreen Knowledge Topic:** Pick a foundational concept that everyone should understand, like "How does GPS work?", "What is a Neural Network?", or "The science of black holes".

            Think, and then make a choice.
            
            After deciding, respond with ONLY two things, separated by a pipe symbol (|):
            1.  A short, relevant category name (e.g., AI, Space, Science, Tech).
            2.  A catchy, clickable blog title in Hinglish for your chosen topic.

            Example for Trending: AI|Apple Intelligence: Kya Yeh Game Changer Hoga?
            Example for Evergreen: Science|Black Holes: Universe ke Ultimate Mysteries!
            """
            response = text_model.generate_content(editorial_prompt)
            response_text = response.text.strip()
            
            if '|' not in response_text:
                raise ValueError("Response from editorial prompt was not in the expected format.")

            category, blog_topic = response_text.split('|', 1)
            print(f"   - Editor's Choice Category: {category}")
            print(f"   - Finalized Topic: {blog_topic}")

        except Exception as e:
            print(f"Error in editorial meeting: {e}")
            return

    # --- Step 2: The "Writer's Room" - Write the article ---
    print("2. Generating a long-form, organized Hinglish article on the chosen topic...")
    try:
        content_prompt = f"""
        विषय: "{blog_topic}"
        You are an expert tech blogger writing for an Indian audience. Write a very detailed, engaging, and well-organized blog post on this topic (around 1000-1200 words).

        **VERY IMPORTANT INSTRUCTIONS:**
        1.  **Language:** Write in a natural, conversational mix of Hindi and English (Hinglish). Use English for technical terms and Hindi for explanations.
        2.  **Structure and Organization:**
            - Start with the Title (Use #).
            - Write a catchy Introduction that hooks the reader.
            - Use multiple, clear subheadings (Use ##) to break down the topic.
            - Explain complex concepts with simple analogies and real-world examples.
            - Use bullet points ('-') for features, pros-cons, or important points.
            - **Crucially, end the article with a section called '## Mukhya Baatein (Key Takeaways)'**. This section should summarize the most important points of the article in a quick, easy-to-read list.
        3.  **Tone:** Professional yet super easy to understand. Make it feel like a smart friend is explaining something cool.
        4.  **Format:** Strictly Markdown.
        """
        response = text_model.generate_content(content_prompt)
        blog_content = response.text.strip()
        print("   - Hinglish content generated successfully.")
    except Exception as e:
        print(f"Error generating content: {e}")
        return

    # --- Step 3: "Publishing Desk" - Save Files and Update JSON ---
    print("3. Saving files and updating metadata...")
    today_date_str = datetime.now().strftime("%Y-%m-%d")
    post_slug = slugify(blog_topic)
    read_time = calculate_read_time(blog_content)
    
    post_dir = f"posts/{today_date_str}-{post_slug}"
    os.makedirs(post_dir, exist_ok=True)

    post_md_path = os.path.join(post_dir, "post.md")
    with open(post_md_path, "w", encoding="utf-8") as f:
        f.write(blog_content)
    print(f"   - Blog post saved to: {post_md_path}")

    blogs_json_path = "blogs.json"
    try:
        with open(blogs_json_path, "r", encoding="utf-8") as f:
            blogs_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        blogs_data = []

    first_paragraph = blog_content.split('\n\n')[0]
    excerpt = ' '.join(first_paragraph.split(' ')[:35]) + '...'
    excerpt = re.sub(r'#+\s*', '', excerpt)

    new_post_entry = {
        "title": blog_topic,
        "date": datetime.now().strftime("%d %B, %Y"),
        "post_path": post_md_path,
        "slug": post_slug,
        "read_time": read_time,
        "excerpt": excerpt,
        "category": category
    }
    
    blogs_data.insert(0, new_post_entry)

    with open(blogs_json_path, "w", encoding="utf-8") as f:
        json.dump(blogs_data, f, indent=4, ensure_ascii=False)
    print(f"   - Updated {blogs_json_path}.")

    print("✅ Process complete! A new, intelligently chosen article is ready.")

if __name__ == "__main__":
    main()

