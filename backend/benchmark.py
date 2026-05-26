import time
import json
import os
from app.models.nlp_model import nlp_pipeline
from app.services.parser import postprocess

def run_benchmark():
    eval_file = os.path.join(os.path.dirname(__file__), "tests", "eval_data.json")
    
    try:
        with open(eval_file, "r") as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"Evaluation dataset not found at {eval_file}")
        return

    print(f"Loaded {len(dataset)} evaluation samples.")
    print("Loading model for benchmarking...")
    
    try:
        nlp_pipeline.load_model()
    except Exception as e:
        print(f"Failed to load model (Are the LoRA weights in model_artifacts?): {e}")
        return

    print("Starting benchmark run...\n")
    
    total_time = 0
    success_count = 0
    accuracy_count = 0
    
    for item in dataset:
        command = item["command"]
        expected_action = item["expected_action"]
        
        start_time = time.time()
        try:
            raw_output = nlp_pipeline.generate(command)
            latency = time.time() - start_time
            total_time += latency
            
            # Simulate the parsing logic in the API
            parsed = json.loads(raw_output)
            parsed = postprocess(parsed, command)
            
            success_count += 1
            
            if parsed.get("action") == expected_action:
                accuracy_count += 1
                
        except Exception as e:
            latency = time.time() - start_time
            total_time += latency
            print(f"[FAIL] Command: '{command}' | Error: {str(e)}")

    print("\n--- Benchmark Results ---")
    print(f"Total Samples: {len(dataset)}")
    
    avg_latency = total_time / len(dataset)
    throughput = len(dataset) / total_time if total_time > 0 else 0
    success_rate = (success_count / len(dataset)) * 100
    accuracy = (accuracy_count / len(dataset)) * 100
    
    print(f"Average Latency: {avg_latency:.4f} seconds/request")
    print(f"Throughput:      {throughput:.2f} requests/second")
    print(f"Parse Success:   {success_rate:.1f}% (Generated valid JSON)")
    print(f"Action Accuracy: {accuracy:.1f}% (Generated correct action)")

if __name__ == "__main__":
    run_benchmark()
