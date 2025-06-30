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

# --- QUOTA FIX: Switched back to the Flash model ---
# It's much faster and has a more generous free tier, perfect for this project.
text_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- Expanded Topic Categories ---
TOPIC_CATEGORIES = [
    "Artificial Intelligence and its real-world impact",
    "Quantum Computing and the next tech revolution",
    "Space Exploration: Mars, Black Holes, and beyond",
    "Biotechnology, Gene Editing, and the future of health",
    "Neuroscience and Brain-Computer Interfaces (BCIs)",
    "The science of Climate Change and Renewable Energy solutions",
    "The future of the Internet: Web3, Metaverse, and Decentralization",
    "Cybersecurity in the age of AI and digital warfare",
    "The evolution of Robotics and Automation",
    "Nanotechnology and its mind-boggling applications"
]

# --- Helper Functions ---
def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def calculate_read_time(text):
    word_count = len(text.split())
    read_time_min = word_count / 200
    return max(1, round(read_time_min))

def main():
    print("🚀 Hinglish Pro AI Blog Generator Activated...")

    # --- 1. Generate a Diverse and Deep Topic ---
    print("1. Selecting a deep topic from expanded categories...")
    chosen_category = random.choice(TOPIC_CATEGORIES)
    print(f"   - Category: {chosen_category}")
    
    try:
        topic_prompt = f"From the category '{chosen_category}', suggest one specific, intriguing, and in-depth blog topic. The title should be a catchy mix of Hindi and English (Hinglish). For example: 'Quantum Computing: Future ka Super-Computer?'. Only provide the topic title, nothing else."
        response = text_model.generate_content(topic_prompt)
        blog_topic = response.text.strip().replace('"', '')
        print(f"   - Topic: {blog_topic}")
    except Exception as e:
        print(f"Error generating topic: {e}")
        return

    # --- 2. Generate a Long, Detailed, Organized Hinglish Blog Post ---
    print("2. Generating a long-form, organized Hinglish article...")
    try:
        content_prompt = f"""
        विषय: "{blog_topic}"

        You are an expert tech blogger who writes for an Indian audience. Write a very detailed, engaging, and well-organized blog post on this topic (around 1000-1200 words).

        **VERY IMPORTANT INSTRUCTIONS:**
        1.  **Language:** Write in a natural, conversational mix of Hindi and English (Hinglish). Use English for technical terms and Hindi for explanations. For example: "Quantum bits, yaani 'qubits', normal bits se bilkul alag hote hain."
        2.  **Structure and Organization:**
            - Start with a powerful Title (Use #).
            - Write a catchy Introduction that hooks the reader.
            - Use multiple, clear subheadings (Use ##) to break down the topic.
            - Explain complex concepts using simple analogies and real-world examples.
            - Use bullet points (using '-') or numbered lists to present information like pros/cons, steps, or features.
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

    # --- 3. Save Files and Update JSON ---
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
        "category": chosen_category.split(' ')[0]
    }
    
    blogs_data.insert(0, new_post_entry)

    with open(blogs_json_path, "w", encoding="utf-8") as f:
        json.dump(blogs_data, f, indent=4, ensure_ascii=False)
    print(f"   - Updated {blogs_json_path}.")

    print("✅ Process complete! New Hinglish article is live.")

if __name__ == "__main__":
    main()

