import requests
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class OpenRouterLLM:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        
        # Load model configuration from settings
        settings_path = Path("app/settings/llms.json")
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            self.model = settings['model']['name']
            self.pricing = settings['model']['pricing']
        
        # Load API key from json file
        api_key_path = Path("app/settings/api-keys.json")
        with open(api_key_path, 'r') as f:
            keys = json.load(f)
            self.api_key = keys.get('openrouter')
            
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in api-keys.json")
    
    def calculate_cost(self, prompt_tokens, completion_tokens):
        """
        Calculate the cost of the API call based on token usage
        
        Args:
            prompt_tokens (int): Number of tokens in the prompt
            completion_tokens (int): Number of tokens in the completion
        
        Returns:
            dict: Dictionary containing cost breakdown
        """
        input_cost = (prompt_tokens / 1_000_000) * self.pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * self.pricing["output"]
            
        return {
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost
        }
    
    def generate(self, prompt, temperature=0.7):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Calculate costs
            usage = result['usage']
            cost_info = self.calculate_cost(
                prompt_tokens=usage.get('prompt_tokens', 0),
                completion_tokens=usage.get('completion_tokens', 0)
            )
            
            return {
                "content": result['choices'][0]['message']['content'],
                "total_cost": cost_info['total_cost']
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call failed: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Error parsing API response: {str(e)}")
    
    def generate_batch(self, prompts, temperature=0.7, max_workers=None):
        """
        Generate responses for multiple prompts in parallel while preserving order
        
        Args:
            prompts (list): List of prompts to process
            temperature (float): Temperature for generation
            max_workers (int, optional): Maximum number of threads to use
            
        Returns:
            list: List of dictionaries containing generated content and costs, in same order as input prompts
        """
        results = [None] * len(prompts)  # Pre-allocate results list
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks and store futures in order
            futures = [
                executor.submit(self.generate, prompt, temperature)
                for prompt in prompts
            ]
            
            # Process results in order
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    results[i] = result
                except Exception as e:
                    # Add failed prompt to result with error message
                    results[i] = {
                        "content": f"Error processing prompt: {str(e)}",
                        "total_cost": 0.0,
                        "error": True,
                        "original_prompt": prompts[i]
                    }
        
        return results
