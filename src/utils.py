import json
import os

def dump_ticket_ids_to_disk(ticketIds: list):
    with open("data/ticket_ids.json", "w") as f:
        json.dump(ticketIds, f)

def get_ticket_ids_from_disk() -> list:
    if not os.path.exists("data/ticket_ids.json"):
        return []
    
    with open("data/ticket_ids.json", "r") as f:
        data = []
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

        return data