import json

import numpy as np


def parse_output_to_json(output):
    if "```json\n" in output:
        json_start = output.find("```json\n") + len("```json\n")
        json_end = output.find("\n```", json_start)
        json_str = output[json_start:json_end].strip()
    else:
        json_str = output.strip()

    try:
        parsed_json = json.loads(json_str)
    except json.decoder.JSONDecodeError as e:
        raise RuntimeError(f"Error parsing output {json_str}. Error - {e}")

    return parsed_json


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
