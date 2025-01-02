from flask import Flask, request, jsonify, render_template
import os
from src.openrouter import OpenRouterLLM
from src.bing_search import BingSearch

app = Flask(__name__, template_folder='templates')

# Initialize OpenRouterLLM with question answering system prompt
qa_llm = OpenRouterLLM("You are a straight to the point assistant who always answer the question ONLY based on the provided snippet. Provide a very short answer to the user question ONLY based on the provided snippet. IMPORTANT: ONLY WHEN THE SNIPPET IS EXPLICITLY RELEVANT TO THE QUESTION; if not output NOT_RELEVANT tag and nothing else")

# Initialize Search Engines
bing_search = BingSearch()
from src.google_search import GoogleSearch
google_search = GoogleSearch()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    engine_filter = data.get('engineFilter', 'bing')
    site_filter = data.get('siteFilter', '')
    time_filter = data.get('timeFilter', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        if engine_filter == 'google':
            search_results = google_search.search(query, site_filter, time_filter)
        else:
            search_results = bing_search.search(query, site_filter, time_filter)
        return jsonify(search_results)
    except Exception as e:
        error_detail = {
            'error': str(e),
            'status_code': getattr(e, 'status_code', None),
            'response_text': getattr(e, 'response_text', None)
        }
        print(f"API Error: {error_detail}")
        return jsonify(error_detail), 500

def generate_answers(results, query):
    """Generate answers for multiple results using OpenRouter LLM"""
    if not results or not isinstance(results, list):
        return None
    
    
    prompts = [
        f"#### Name: {result['name']}\n#### Snippet: {result['snippet']}\n\n#### User question: {query}"
        for result in results
    ]
    
    try:
        batch_results = qa_llm.generate_batch(prompts)
        if not batch_results:
            return None
            
        total_cost = sum(result['total_cost'] for result in batch_results)
        answers = [result['content'] for result in batch_results]
        
        return {
            'answers': answers,
            'total_cost': total_cost
        }
    except Exception as e:
        print(f"Error in generate_answers: {str(e)}")
        return None

@app.route('/api/answers', methods=['POST'])
def get_answers():
    data = request.json
    results = data.get('results')
    query = data.get('query')
    
    
    generated_results = generate_answers(results, query)
    
    
    if not generated_results:
        return jsonify({'error': 'Failed to generate answers'}), 500
        
    return jsonify(generated_results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
