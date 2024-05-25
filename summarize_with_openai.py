import openai

MODEL_NAME="gpt-3.5-turbo"

def extract_topics_from_titles(api_key, news_articles, 
                               instructions=[
                                   "Please sort them according to their prominence and cluster them as closely as possible.",
                                   "Please be as concise as possible.", 
                                   "Please provie only the cluster titles not the actual news titles.",
                                   "Please keep the bullet point list in one level.",
                                   "Please use markdown."
                               ]):
    # Initialize OpenAI API
    openai.api_key = api_key

    # Extract titles
    titles = [article['title'] for article in news_articles]
    titles_content = "\n".join(titles)

    # Function to generate topics from titles
    def generate_topics(titles_content):
        messages = [
            {"role": "system", "content": "You are a helpful and knowledgeable assistant."},
            {"role": "user", "content": f"Extract important topics from the following news article titles. "
             + " ".join(instructions)
             + f"\n\n{titles_content}\n\nTopics:"}
        ]
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    # Generate topics from titles
    topics = generate_topics(titles_content)

    return topics


def summarize_articles(api_key, news_articles, n_paragraphs=5,
                       instructions=["If possible, use bullet points to make it easily readable.",
                                     "Please keep it to the points and ignore unnecessary details."
                                     "Please use markdown."]
                                     ):
    # Initialize OpenAI API
    openai.api_key = api_key

    # Combine titles and contents into a single string
    combined_content = "\n\n".join([f"{article['title']}: {article['content']}" for article in news_articles])

    # Function to generate a summary from combined content
    def generate_summary(combined_content):
        messages = [
            {"role": "system", "content": "You are a helpful and knowledgeable assistant."},
            {"role": "user", "content": f"Write a {n_paragraphs}-paragraph summary of the following news articles. "
             + " ".join(instructions)
             +f":\n\n{combined_content}\n\nSummary:"}
        ]
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()

    # Generate summary from the combined content
    summary = generate_summary(combined_content)

    return summary
