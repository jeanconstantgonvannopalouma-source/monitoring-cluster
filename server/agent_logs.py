import json

def get_logs():
    logs = []
    try:
        with open("logs.jsonl", "r") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
    except FileNotFoundError:
        pass

    return logs
