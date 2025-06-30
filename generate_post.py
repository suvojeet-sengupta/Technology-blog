import os
import google.generativeai as genai
import json
from datetime import datetime
import re

# --- Configuration ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")

genai.configure(api_key=API_KEY)
text_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- Helper Functions ---
def slugify(text):
    """Converts a string to a URL-friendly slug."""
    # This regex handles Hindi characters better
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def calculate_read_time(text):
    """Calculates the estimated reading time in minutes."""
    word_count = len(text.split())
    # Average reading speed is ~200 words per minute
    read_time_min = word_count / 200
    return max(1, round(read_time_min)) # Return at least 1 minute

def main():
    print("🤖 Pro AI Blog Post Generator Started...")

    # --- 1. Generate Blog Topic ---
    print("1. Generating a new tech topic...")
    try:
        topic_prompt = "Suggest one interesting and relevant technology blog topic in Hindi. The topic should be suitable for both beginners and advanced readers. Only provide the topic title, nothing else."
        response = text_model.generate_content(topic_prompt)
        blog_topic = response.text.strip().replace('"', '')
        print(f"   - Topic: {blog_topic}")
    except Exception as e:
        print(f"Error generating topic: {e}")
        return

    # --- 2. Generate Blog Post Content ---
    print("2. Generating blog content...")
    try:
        content_prompt = f"""
        विषय: "{blog_topic}"

        इस विषय पर एक विस्तृत, आकर्षक और आसानी से समझ में आने वाला ब्लॉग पोस्ट हिंदी में लिखो।
        - एक आकर्षक शीर्षक (title) से शुरू करो। (Use # for the main title)
        - एक परिचय (introduction) दो।
        - मुख्य सामग्री को समझाने के लिए कम से कम 3-4 सबहेडिंग (subheadings) का प्रयोग करो। (Use ## for subheadings)
        - अंत में एक निष्कर्ष (conclusion) लिखो।
        - भाषा सरल और आकर्षक होनी चाहिए।
        - Format: Markdown.
        """
        response = text_model.generate_content(content_prompt)
        blog_content = response.text.strip()
        print("   - Content generated successfully.")
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

    # Extract a short excerpt for the homepage card
    first_paragraph = blog_content.split('\n\n')[0]
    excerpt = ' '.join(first_paragraph.split(' ')[:30]) + '...'
    excerpt = re.sub(r'#+\s*', '', excerpt) # Remove markdown hashes from excerpt

    new_post_entry = {
        "title": blog_topic,
        "date": datetime.now().strftime("%d %B, %Y"),
        "post_path": post_md_path,
        "slug": post_slug,
        "read_time": read_time,
        "excerpt": excerpt
    }
    
    blogs_data.insert(0, new_post_entry)

    with open(blogs_json_path, "w", encoding="utf-8") as f:
        json.dump(blogs_data, f, indent=4, ensure_ascii=False)
    print(f"   - Updated {blogs_json_path} with read time and excerpt.")

    print("✅ Process completed successfully!")

if __name__ == "__main__":
    main()

