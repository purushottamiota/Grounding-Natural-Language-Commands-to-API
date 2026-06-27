import json
import os

def check_dataset_intersection():
    # Define paths
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    train_path = os.path.join(project_root, "dataset.jsonl")
    eval_path = os.path.join(project_root, "backend", "tests", "eval_data.json")

    print(f"Reading training set from: {train_path}")
    print(f"Reading evaluation set from: {eval_path}\n")

    # 1. Load Training Prompts
    train_prompts = set()
    prefix = "translate English to Calendar API: "
    
    try:
        with open(train_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    raw_prompt = item.get("input_text", "")
                    # Strip prefix to get the raw NL command
                    if raw_prompt.startswith(prefix):
                        raw_prompt = raw_prompt[len(prefix):]
                    train_prompts.add(raw_prompt.strip().lower())
    except FileNotFoundError:
        print(f"Error: Training file not found at {train_path}")
        return

    # 2. Load Evaluation Prompts
    eval_prompts = set()
    try:
        with open(eval_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
            for item in eval_data:
                command = item.get("command", "")
                eval_prompts.add(command.strip().lower())
    except FileNotFoundError:
        print(f"Error: Evaluation file not found at {eval_path}")
        return

    # 3. Calculate Intersection
    overlap = train_prompts.intersection(eval_prompts)

    print("--- Intersection Report ---")
    print(f"Unique Train Prompts: {len(train_prompts)}")
    print(f"Unique Eval Commands: {len(eval_prompts)}")
    print(f"Overlap Count:        {len(overlap)}")

    if overlap:
        print("\n[WARNING] Overlapping items found:")
        for idx, item in enumerate(sorted(overlap), 1):
            print(f"{idx}. '{item}'")
    else:
        print("\n[SUCCESS] Verification Successful: Zero overlap detected between datasets!")

if __name__ == "__main__":
    check_dataset_intersection()
