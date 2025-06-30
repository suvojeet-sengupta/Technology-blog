import os
import google.generativeai as genai
import json
from datetime import datetime
import re

# --- Configuration ---
# API key ko GitHub Secrets se lena hai
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")

genai.configure(api_key=API_KEY)

# Model
text_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- Helper Function ---
def slugify(text):
    """Converts a string to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[\s\W_]+', '-', text)
    return text.strip('-')

def main():
    print("🤖 AI Blog Post Generator Started (Text-Only Mode)...")

    # --- 1. Generate Blog Topic ---
    print("1. Generating a new tech topic...")
    try:
        topic_prompt = "Suggest one interesting and relevant technology blog topic in Hindi. The topic should be suitable for both beginners and advanced readers. Only provide the topic title, nothing else."
        response = text_model.generate_content(topic_prompt)
        blog_topic = response.text.strip()
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
        - एक आकर्षक शीर्षक (title) से शुरू करो।
        - एक परिचय (introduction) दो।
        - मुख्य सामग्री को समझाने के लिए कम से कम 3-4 सबहेडिंग (subheadings) का प्रयोग करो।
        - अंत में एक निष्कर्ष (conclusion) लिखो।
        - भाषा सरल और आकर्षक होनी चाहिए।
        - Format: Markdown. Use # for title, ## for subheadings.
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
    
    # Create directory for the new post
    post_dir = f"posts/{today_date_str}-{post_slug}"
    os.makedirs(post_dir, exist_ok=True)

    # Save markdown content
    post_md_path = os.path.join(post_dir, "post.md")
    with open(post_md_path, "w", encoding="utf-8") as f:
        f.write(blog_content)
    print(f"   - Blog post saved to: {post_md_path}")

    # Update blogs.json
    blogs_json_path = "blogs.json"
    try:
        with open(blogs_json_path, "r", encoding="utf-8") as f:
            blogs_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        blogs_data = []

    new_post_entry = {
        "title": blog_topic,
        "date": datetime.now().strftime("%d %B, %Y"),
        "post_path": post_md_path,
        "slug": post_slug
    }
    
    # Add the new post to the beginning of the list
    blogs_data.insert(0, new_post_entry)

    with open(blogs_json_path, "w", encoding="utf-8") as f:
        json.dump(blogs_data, f, indent=4, ensure_ascii=False)
    print(f"   - Updated {blogs_json_path}")

    print("✅ Process completed successfully!")

if __name__ == "__main__":
    main()

