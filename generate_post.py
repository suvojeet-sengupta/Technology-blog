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
text_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- Helper Functions (No changes) ---
def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def calculate_read_time(text):
    word_count = len(text.split())
    read_time_min = word_count / 200
    return max(1, round(read_time_min))

def main():
    print("🚀 Editor-in-Chief AI Blog Generator Activated...")

    # --- Step 1: The "Trend Hunter" - Find a trending topic ---
    print("1. Asking Gemini for a trending Science/Tech topic...")
    try:
        # This prompt asks Gemini to act as an editor and find what's hot right now.
        trend_hunter_prompt = """
        Act as a tech journalist and editor for a popular Indian blog.
        What is one of the most exciting and currently trending topics in the world of science or technology?
        It could be a new breakthrough, a recent discovery, or a viral tech debate.
        Respond with ONLY two things, separated by a pipe symbol (|):
        1. A short category name (e.g., AI, Space, Biotech).
        2. A catchy, clickable blog title in Hinglish for that topic.

        Example: AI|AI Clones: Kya Aapka Digital Hamshakal Possible Hai?
        """
        response = text_model.generate_content(trend_hunter_prompt)
        response_text = response.text.strip()
        
        if '|' not in response_text:
            raise ValueError("Response from trend hunter prompt was not in the expected format.")

        category, blog_topic = response_text.split('|', 1)
        print(f"   - Trending Category: {category}")
        print(f"   - Generated Topic: {blog_topic}")

    except Exception as e:
        print(f"Error finding a trending topic: {e}")
        return

    # --- Step 2: The "Deep Dive" - Write the article ---
    print("2. Generating a long-form, organized Hinglish article on the trending topic...")
    try:
        content_prompt = f"""
        विषय: "{blog_topic}"
        You are an expert tech blogger writing for an Indian audience. Write a very detailed, engaging, and well-organized blog post on this topic (around 1000-1200 words).

        **VERY IMPORTANT INSTRUCTIONS:**
        1.  **Language:** Write in a natural, conversational mix of Hindi and English (Hinglish).
        2.  **Structure:**
            - Start with the Title (Use #).
            - Write a catchy Introduction.
            - Use multiple, clear subheadings (Use ##).
            - Explain complex concepts with simple analogies and real-world examples.
            - Use bullet points ('-') for features/pros-cons.
            - End with a '## Mukhya Baatein (Key Takeaways)' section summarizing the main points.
        3.  **Tone:** Professional yet super easy to understand.
        4.  **Format:** Strictly Markdown.
        """
        response = text_model.generate_content(content_prompt)
        blog_content = response.text.strip()
        print("   - Hinglish content generated successfully.")
    except Exception as e:
        print(f"Error generating content: {e}")
        return

    # --- Step 3: Save Files and Update JSON (No changes in logic) ---
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

    print("✅ Process complete! A new trending article is ready.")

if __name__ == "__main__":
    main()

