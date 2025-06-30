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

# --- NEW: Expanded Topic Categories ---
TOPIC_CATEGORIES = [
    "Artificial Intelligence breakthroughs",
    "Quantum Computing explained simply",
    "The future of Space Exploration and new missions",
    "Latest advancements in Biotechnology and CRISPR",
    "Deep Dive into Neuroscience and Brain-Computer Interfaces",
    "The science behind Black Holes and Wormholes",
    "Next-generation Renewable Energy sources",
    "The impact of 5G and the future of 6G",
    "Cybersecurity threats and how to stay safe",
    "The evolution of Electric Vehicles and battery tech",
    "Augmented Reality (AR) vs. Virtual Reality (VR)",
    "The role of Nanotechnology in medicine"
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
    print("🚀 God Mode AI Blog Post Generator Activated...")

    # --- 1. Generate a Diverse and Deep Topic ---
    print("1. Selecting a deep topic from expanded categories...")
    chosen_category = random.choice(TOPIC_CATEGORIES)
    print(f"   - Category: {chosen_category}")
    
    try:
        topic_prompt = f"From the category '{chosen_category}', suggest one specific, intriguing, and in-depth blog topic in Hindi. The title should be catchy and make people want to click. Only provide the topic title, nothing else."
        response = text_model.generate_content(topic_prompt)
        blog_topic = response.text.strip().replace('"', '')
        print(f"   - Topic: {blog_topic}")
    except Exception as e:
        print(f"Error generating topic: {e}")
        return

    # --- 2. Generate a Long, Detailed Blog Post ---
    print("2. Generating a long-form, detailed article (1000+ words)...")
    try:
        content_prompt = f"""
        विषय: "{blog_topic}"

        इस विषय पर एक बहुत ही विस्तृत, गहन, और आकर्षक ब्लॉग पोस्ट हिंदी में लिखो (लगभग 1000-1200 शब्दों में)।
        - एक दमदार शीर्षक (title) से शुरू करो। (Use # for the main title)
        - एक आकर्षक परिचय (introduction) दो जो पाठक को बांध ले।
        - विषय को गहराई से समझाने के लिए कई सबहेडिंग (subheadings) का प्रयोग करो। (Use ## for subheadings)
        - जटिल कॉन्सेप्ट्स को सरल भाषा में, उदाहरणों के साथ समझाओ।
        - जहाँ संभव हो, डेटा या आँकड़े शामिल करो।
        - अंत में एक शक्तिशाली निष्कर्ष (conclusion) लिखो जो पाठक को सोचने पर मजबूर कर दे।
        - भाषा प्रोफेशनल लेकिन सरल होनी चाहिए।
        - Format: Markdown.
        """
        response = text_model.generate_content(content_prompt)
        blog_content = response.text.strip()
        print("   - Long-form content generated successfully.")
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
        "category": chosen_category.split(' ')[0] # Add a simple category tag
    }
    
    blogs_data.insert(0, new_post_entry)

    with open(blogs_json_path, "w", encoding="utf-8") as f:
        json.dump(blogs_data, f, indent=4, ensure_ascii=False)
    print(f"   - Updated {blogs_json_path} with category, read time, and excerpt.")

    print("✅ Process completed successfully! A new masterpiece is ready.")

if __name__ == "__main__":
    main()
