import json
import os
from openai import OpenAI

class RankingAgent:
    def __init__(self, weight_therapeutic=0.4, weight_research=0.2, weight_understanding=0.2, weight_versatility=0.2, openai_api_key=None, prompts_file="prompts.json"):
        self.weights = {
            'therapeutic': weight_therapeutic,
            'research': weight_research,
            'understanding': weight_understanding,
            'versatility': weight_versatility
        }
        
        # Load prompts from JSON file
        try:
            with open(prompts_file, 'r') as f:
                self.prompts = json.load(f)["ranking_agent"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load prompts from {prompts_file}: {e}")
            self.prompts = {
                "system_message": "You are an expert in RNA therapeutics evaluation and ranking.",
                "prompt_template": "You are a domain expert in RNA therapeutics ranking design candidates.\n\nBelow is a JSON list of candidate design summaries. Each summary contains fields such as 'design_type', 'target_region', 'score' (from prior evaluation), and other metrics.\n\nPlease rank these designs in descending order of their therapeutic potential and overall suitability. Use the following weighting criteria in your evaluation:\n- Therapeutic potential weight: {therapeutic}\n- Research activity weight: {research}\n- Fundamental understanding weight: {understanding}\n- Versatility weight: {versatility}\n\nFor each design, provide a \"composite_score\" that reflects your ranking decision, and output a JSON list of the design summaries sorted by descending composite_score.\n\nOutput only valid JSON.\n\nDesign Summaries:\n{design_summaries}"
            }
            
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OpenAI API key not provided. Set it via parameter or the OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=openai_api_key)

    def rank_designs(self, design_summaries):
        # Format the prompt template with weights and design summaries
        prompt = self.prompts["prompt_template"].format(
            therapeutic=self.weights['therapeutic'],
            research=self.weights['research'],
            understanding=self.weights['understanding'],
            versatility=self.weights['versatility'],
            design_summaries=json.dumps(design_summaries, indent=2)
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.prompts["system_message"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300,
                n=1
            )
            reply = response.choices[0].message.content.strip()
            ranked_designs = json.loads(reply)
        except Exception as e:
            print("Error during LLM ranking evaluation:", e)
            # Fallback: use the evaluator's score to compute a composite score
            for summary in design_summaries:
                summary['composite_score'] = summary.get('score', 0) * sum(self.weights.values())
            ranked_designs = sorted(design_summaries, key=lambda x: x['composite_score'], reverse=True)
        return ranked_designs