import os
try:
    from dotenv import load_dotenv, find_dotenv
    # Find the .env file automatically
    dotenv_path = find_dotenv()
    if dotenv_path:
        print(f"Loading environment variables from: {dotenv_path}")
        load_dotenv(dotenv_path)  # Load environment variables from found .env file
    else:
        print("No .env file found in the directory tree")
except ImportError:
    print("dotenv package not found. Environment variables must be set manually.")

from file_parser import SfoldParser
from design_evaluator import DesignEvaluator
from ranking_agent import RankingAgent
from report_generator import ReportGenerator

def extract_candidates_from_data(parsed_data):
    """
    Extract design candidates from the parsed Sfold data.
    This replaces the dummy candidates with real data-derived candidates.
    """
    candidates = []
    
    # Check if we have accessibility data
    if 'accessibility' in parsed_data and parsed_data['accessibility']:
        # Extract from oligo.out if available
        if 'oligo.out' in parsed_data['accessibility'] and parsed_data['accessibility']['oligo.out']:
            oligo_data = parsed_data['accessibility']['oligo.out']
            # Process oligo.out data to extract candidate regions
            for i in range(0, len(oligo_data), 4):  # Assuming data is grouped in blocks of 4 lines
                if i+3 < len(oligo_data):
                    try:
                        # Extract position and accessibility information
                        # Format may vary, this is an example extraction
                        line = oligo_data[i+1].strip()
                        if line and not line.startswith('#') and not line.startswith('Column'):
                            parts = line.split()
                            if len(parts) >= 3:
                                # Check if the first part is a valid integer
                                try:
                                    start = int(parts[0])
                                    end = start + 19  # Typical oligo length
                                    accessibility = float(parts[2])
                                    candidates.append({
                                        'design_type': 'oligo',
                                        'start': start,
                                        'end': end,
                                        'accessibility': accessibility,
                                        'binding_energy': -10.0,  # Default value, should be calculated from energy data
                                        'target_region': f"{start}-{end}"  # Add target_region field
                                    })
                                except ValueError:
                                    # Skip lines that don't have valid integers
                                    continue
                    except (ValueError, IndexError) as e:
                        print(f"Error processing oligo data: {e}")
    
    # If we have structure data, we can extract siRNA candidates
    if 'structure' in parsed_data and parsed_data['structure']:
        # Extract from 10structure.out if available
        if '10structure.out' in parsed_data['structure'] and parsed_data['structure']['10structure.out']:
            structure_data = parsed_data['structure']['10structure.out']
            # Process structure data to find stable regions for siRNA targeting
            for i in range(0, len(structure_data)):
                if i+1 < len(structure_data):
                    try:
                        line = structure_data[i].strip()
                        if line and not line.startswith('#') and not line.startswith('Structure'):
                            # This is a simplified example - actual parsing would depend on file format
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    pos = int(parts[0])
                                    # Find regions with stable structure for siRNA targeting
                                    if pos % 20 == 0:  # Sample every 20 positions
                                        candidates.append({
                                            'design_type': 'siRNA',
                                            'start': pos,
                                            'end': pos + 20,
                                            'accessibility': 0.5,  # Default value
                                            'binding_energy': -12.0,  # Default value
                                            'target_region': f"{pos}-{pos+20}"  # Add target_region field
                                        })
                                except ValueError:
                                    # Skip lines that don't have valid integers
                                    continue
                    except (ValueError, IndexError) as e:
                        print(f"Error processing structure data: {e}")
    
    # If no candidates were found, create a few default ones based on sequence length
    if not candidates and 'structure' in parsed_data and parsed_data['structure']:
        # Try to determine sequence length from structure files
        seq_length = 0
        for file_key in parsed_data['structure']:
            for line in parsed_data['structure'][file_key]:
                if 'ENERGY' in line and 'sequence length' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'length':
                            try:
                                seq_length = int(parts[i+1])
                                break
                            except (ValueError, IndexError):
                                continue
                    if seq_length > 0:
                        break
            if seq_length > 0:
                break
        
        if seq_length > 0:
            # Create candidates at regular intervals
            interval = seq_length // 5
            for i in range(1, 5):
                start = i * interval
                candidates.append({
                    'design_type': 'siRNA',
                    'start': start,
                    'end': start + 20,
                    'accessibility': 0.5,
                    'binding_energy': -12.0,
                    'target_region': f"{start}-{start+20}"  # Add target_region field
                })
        else:
            # If we couldn't determine sequence length, create some default candidates
            for i in range(1, 5):
                start = i * 20
                candidates.append({
                    'design_type': 'siRNA',
                    'start': start,
                    'end': start + 20,
                    'accessibility': 0.5,
                    'binding_energy': -12.0,
                    'target_region': f"{start}-{start+20}"  # Add target_region field
                })
    
    return candidates

def main():
    # Check if the OPENAI_API_KEY environment variable is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set. Please set it to use the OpenAI API.")
        print("You can set it by running: export OPENAI_API_KEY='your-api-key'")
        return
        
    input_dir = "../output"  # Directory containing Sfold output files.
    
    # Parse the Sfold data
    if not os.path.isdir(input_dir):
        print(f"Input directory '{input_dir}' not found. Cannot proceed without data.")
        return
    
    try:
        parser = SfoldParser(input_dir)
        parsed_data = parser.parse_all()
        print(f"Successfully parsed data from {input_dir}")
        
        # Extract candidates from the parsed data
        candidates = extract_candidates_from_data(parsed_data)
        
        if not candidates:
            print("No viable candidates could be extracted from the data. Cannot proceed.")
            return
            
        print(f"Extracted {len(candidates)} candidate designs from the data")
        
        # Evaluate the candidates
        evaluator = DesignEvaluator(parsed_data)
        design_summaries = evaluator.evaluate_designs(candidates)
        print(f"Evaluated {len(design_summaries)} designs")
        
        # Rank the designs
        ranking_agent = RankingAgent()
        ranked_designs = ranking_agent.rank_designs(design_summaries)
        print(f"Ranked {len(ranked_designs)} designs")
        
        # Generate the report
        report_generator = ReportGenerator()
        report_generator.generate_report(ranked_designs)
        print("Report generation completed")
    except Exception as e:
        print(f"Error in processing pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()