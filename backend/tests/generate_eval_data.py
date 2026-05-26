import json
import random
import os

ACTIONS = {
    "insert": [
        "Schedule a {title} {time}",
        "Book a {title} {time}",
        "Set up a {title} for {duration} {time}",
        "Create a {title} {time}",
    ],
    "delete": [
        "Cancel the {title}",
        "Delete my {title}",
        "Remove the {title} from my calendar",
        "I want to cancel the {title}",
    ],
    "update": [
        "Move the {title} to {time}",
        "Reschedule the {title} to {time}",
        "Update the {title} to be at {time}",
    ],
    "reminder": [
        "Remind me to {task} {time}",
        "Set a reminder to {task} {time}",
        "Don't let me forget to {task} {time}",
    ],
    "query": [
        "Am I free {time}?",
        "What does my schedule look like {time}?",
        "Do I have any meetings {time}?",
    ],
    "add_attendee": [
        "Add {person} to the {title}",
        "Invite {person} to the {title}",
        "Make sure {person} is in the {title}",
    ]
}

TITLES = ["sync", "standup", "review", "retrospective", "1:1", "planning session", "demo", "brainstorm", "interview", "quick chat"]
TIMES = ["tomorrow at 9am", "next Friday at 3pm", "today at noon", "at 4:30pm", "next Monday at 10am", "at midnight", "on Thursday"]
DURATIONS = ["for 30 minutes", "for 1 hour", "for 90 min", "for half an hour", "for 2 hours"]
TASKS = ["call John", "finish the report", "buy groceries", "email the client", "prepare slides"]
PEOPLE = ["Alice", "Bob", "Carol", "David", "Eve"]

def generate_dataset(num_samples=250):
    dataset = []
    
    for _ in range(num_samples):
        action = random.choice(list(ACTIONS.keys()))
        template = random.choice(ACTIONS[action])
        
        command = template.format(
            title=random.choice(TITLES),
            time=random.choice(TIMES),
            duration=random.choice(DURATIONS),
            task=random.choice(TASKS),
            person=random.choice(PEOPLE)
        )
        
        dataset.append({
            "command": command,
            "expected_action": action
        })
        
    return dataset

if __name__ == "__main__":
    dataset = generate_dataset(250)
    out_path = os.path.join(os.path.dirname(__file__), "eval_data.json")
    
    with open(out_path, "w") as f:
        json.dump(dataset, f, indent=4)
        
    print(f"Successfully generated {len(dataset)} evaluation samples at {out_path}")
