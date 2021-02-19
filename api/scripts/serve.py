
# Launch FastAPI on given port
# Call get_pattern() on a given endpoint


import os
import pickle
import sys
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI

sys.path.append("/home/code")
from logflow.logsparser.Journal import Journal, LogTooShortError

# Get the log parsing function
script_path = os.path.dirname(os.path.realpath(__file__))
parsing_function_path = os.path.join(script_path, "..")
sys.path.append(parsing_function_path)
from log_parsing_function import parser_function

app = FastAPI()


@app.get("/logflow")
def get_pattern(log: str) -> Dict[str, str]:
    """
    Load the trained model and find the pattern associated with the provided log.

    Args:
        log (str): The log to be parsed.

    Returns:
        Dict[str, str]: Its pattern ID and template.
    """
    # Load latest pattern
    patterns_dir = "/home/output"
    patterns = [os.path.join(patterns_dir, basename)
                for basename in os.listdir(patterns_dir)]
    latest_model = max(patterns, key=os.path.getctime)
    with open(latest_model, "rb") as handler:
        patterns = pickle.load(handler)

    # Transform the log
    model = Journal(
        parser_message=parser_function,
        path=None,
        associated_pattern=True,
        dict_patterns=patterns,
        output="logpai")
    model.run()
    try:
        log_pattern = model.associate_pattern(log)
    except LogTooShortError as exception:
        log_pattern = {"error": "log too short"}

    return log_pattern


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
