import json
import os
from openai import OpenAI

class DesignEvaluator:
    def __init__(self, parsed_data, openai_api_key=None, prompts_file="prompts.json"):
        self.parsed_data = parsed_data
        # Load prompts from JSON file
        try:
            with open(prompts_file, 'r') as f:
                self.prompts = json.load(f)["design_evaluator"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load prompts from {prompts_file}: {e}")
            self.prompts = {
                "system_message": "You are an expert in RNA therapeutics evaluation.",
                "prompt_template": "You are a domain expert in RNA therapeutics.\nEvaluate the following candidate design for therapeutic potential.\n\nCandidate details:\n- Design Type: {design_type}\n- Target Region: {start} - {end}\n- Accessibility: {accessibility}\n- Binding Energy: {binding_energy} kcal/mol\n\nProvide your evaluation as a valid JSON object with the following keys:\n- \"design_type\": string (the design type)\n- \"target_region\": string (e.g., \"100-120\")\n- \"evaluation\": string (\"Pass\" or \"Fail\" based on overall assessment)\n- \"score\": number (a composite score where a higher value indicates better potential)\n- \"notes\": string (a concise explanation of the evaluation)\n- \"accessibility\": number (copy from input)\n- \"binding_energy\": number (copy from input)\n\nOutput only valid JSON."
            }
            
        # Use provided API key or check environment variable OPENAI_API_KEY
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OpenAI API key not provided. Set it via parameter or the OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=openai_api_key)

    def evaluate_candidate_with_llm(self, candidate):
        # Format the prompt template with candidate details
        prompt = self.prompts["prompt_template"].format(
            design_type=candidate.get('design_type'),
            start=candidate.get('start'),
            end=candidate.get('end'),
            accessibility=candidate.get('accessibility'),
            binding_energy=candidate.get('binding_energy')
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.prompts["system_message"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=150,
                n=1
            )
            reply = response.choices[0].message.content.strip()
            # Attempt to parse the JSON output from the LLM
            summary = json.loads(reply)
            
            # Ensure accessibility and binding_energy are included
            if 'accessibility' not in summary:
                summary['accessibility'] = candidate.get('accessibility')
            if 'binding_energy' not in summary:
                summary['binding_energy'] = candidate.get('binding_energy')
                
        except Exception as e:
            print("Error during LLM evaluation:", e)
            summary = {
                "design_type": candidate.get('design_type'),
                "target_region": f"{candidate.get('start')}-{candidate.get('end')}",
                "evaluation": "Error",
                "score": 0,
                "notes": "LLM evaluation failed.",
                "accessibility": candidate.get('accessibility'),
                "binding_energy": candidate.get('binding_energy')
            }
        return summary

    def evaluate_designs(self, candidates):
        summaries = []
        for candidate in candidates:
            summary = self.evaluate_candidate_with_llm(candidate)
            summaries.append(summary)
        return summaries