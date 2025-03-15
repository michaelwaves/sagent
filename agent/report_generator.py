import json
import os
from openai import OpenAI

class ReportGenerator:
    def __init__(self, output_file='recommendation_report.md', openai_api_key=None, prompts_file="prompts.json"):
        self.output_file = output_file
        
        # Load prompts from JSON file
        try:
            with open(prompts_file, 'r') as f:
                self.prompts = json.load(f)["report_generator"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load prompts from {prompts_file}: {e}")
            self.prompts = {
                "system_message": "You are an expert in RNA therapeutics and report writing.",
                "prompt_template": "You are a domain expert in RNA therapeutics tasked with summarizing the evaluation of design candidates for RNA targeting.\n\nBelow is a JSON list of ranked design summaries. Each summary contains details such as design type, target region, accessibility, binding energy, and a composite score.\n\nPlease produce a final recommendation report for the researcher that includes:\n- An executive summary of the analysis.\n- A clear final recommendation based on the ranking.\n- Brief summaries for each design candidate.\n- Any additional insights or suggestions for further validation.\n\nOutput your report in clear plain text with sections for the executive summary, candidate details, and final recommendation.\n\nRanked Design Summaries:\n{ranked_designs}"
            }
            
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OpenAI API key not provided. Set it via parameter or the OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=openai_api_key)

    def generate_report(self, ranked_designs):
        # Format the prompt template with ranked designs
        prompt = self.prompts["prompt_template"].format(
            ranked_designs=json.dumps(ranked_designs, indent=2)
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.prompts["system_message"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                n=1
            )
            report = response.choices[0].message.content.strip()
        except Exception as e:
            print("Error during LLM report generation:", e)
            # Fallback: use a simple text concatenation method
            report_lines = []
            report_lines.append("RNA Targeting Recommendation Report")
            report_lines.append("=" * 40)
            report_lines.append("\nRanked Design Candidates:")
            for idx, design in enumerate(ranked_designs, start=1):
                line = f"Rank {idx}: {design.get('design_type', 'Unknown')} targeting {design.get('target_region', 'Unknown')} - Score: {design.get('composite_score', design.get('score', 0)):.2f}"
                report_lines.append(line)
                # Safely access accessibility and binding_energy with get() to avoid KeyError
                accessibility = design.get('accessibility', 'N/A')
                binding_energy = design.get('binding_energy', 'N/A')
                details = f"    Accessibility: {accessibility}, Binding Energy: {binding_energy}"
                report_lines.append(details)
            report_lines.append("\nFinal Recommendation:")
            if ranked_designs:
                best = ranked_designs[0]
                report_lines.append(f"Recommend {best.get('design_type', 'Unknown')} targeting {best.get('target_region', 'Unknown')} with composite score {best.get('composite_score', best.get('score', 0)):.2f}.")
            else:
                report_lines.append("No viable design candidates were identified.")
            report = "\n".join(report_lines)
        
        with open(self.output_file, 'w') as f:
            f.write(report)
        print(f"Report generated: {self.output_file}")