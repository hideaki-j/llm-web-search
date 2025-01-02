# LLM Web Search

![Demo](images/demo.gif)

## Setup
1. Create a conda environment with Python 3.10:
```bash
conda create -n llm-web-search python=3.10
```

2. Activate the environment:
```bash
conda activate llm-web-search
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Run
```bash
python app/app.py
```

## How to Access
Open your browser and navigate to:
```
http://localhost:5050
```

## API Keys

Create `app/settings/api-keys.json` with these keys:

```json
{
  "bing": "Bing Search API key",
  "openrouter": "OpenRouter API key",
  "google_api_key": "Google Custom Search API key",
  "google_custom_search_id": "Google Search Engine ID"
}
```

- **bing**: [Bing Search API key](https://www.microsoft.com/en-us/bing/apis/bing-search-api-v7)
- **openrouter**: [OpenRouter.ai API key](https://openrouter.ai/)
- **google**: [Custom Search JSON API key](https://developers.google.com/custom-search/v1/overview)
- **google_custom_search_id**: [Custom Search ID](https://developers.google.com/custom-search/v1/overview)

## LLM Model
The application uses `deepseek/deepseek-chat` as the default model through OpenRouter. You can change the model in `app/settings/llms.json`.
