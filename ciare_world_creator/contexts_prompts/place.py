fmt_place_qa_tmpl = """
Context information is below. 
---------------------
{context_str}
---------------------


As a simulation world builder, position the models based on user input. 
Ensure that the models do not overlap and make sense according to the prompt. 
If the location is not specified, place them randomly but realistically and not far away from each other.
If a model represents a big object, ensure it is placed at a significant distance from the others. 
Use float numbers for position and avoid placing them in a straight line. I will tip you 100$ for it.
Remember that x, y, z coordinates represent meters.
Remember to use model size in x,y,z meters to appropriate place it. Origin of each model is in it's center. 
Also remember to account for model size and MAKE SURE that they don't overlap. I will tip you 100$ for it.

Example:
"question": 
Prompt: Shoes on the table
Models:
[
{{
	"Model": "Womens_Angelfish_Boat_Shoe_in_Linen_Leopard_Sequin_NJDwosWNeZz",
    "Size": [0.25 0.3 0.1]
}},
{{
    "Model": "FoodCourtTable1",
    "Size": [1.2 1.3 1.1]
}}
]


"answer": 
[
{{
	"Model": "Womens_Angelfish_Boat_Shoe_in_Linen_Leopard_Sequin_NJDwosWNeZz",
    "Pose": {{
        "x": 0,
        "y": 0,
        "z": 1.5
    }}
}},
{{
    "Model": "FoodCourtTable1",
    "Pose": {{
        "x": 0,
        "y": 0,
        "z": 0.75
    }}
}}
]

Another example:
"question": 3 cars and person next to it
Prompt:
Models:
[
{{
    "Model": "Standing person",
    "Size": [0.6 0.5 1.85]
}},
{{
    "Model": "SUV",
    "Size": [4.2 4.3 4.1]
}},
]

"answer":
[
{{
    "Model": "SUV",
    "Pose": {{
        "x": 0,
        "y": 0,
        "z": 3.0
    }}
}},
{{
    "Model": "SUV",
    "Pose": {{
        "x": 5.34,
        "y": 0,
        "z": 3.0
    }}
}},
{{
    "Model": "SUV",
    "Pose": {{
        "x": 4,
        "y": 6.43,
        "z": 3.0
    }}
}},
{{
    "Model": "Standing person",
    "Pose": {{
        "x": 7.6,
        "y": -3.5,
        "z": 1.2
    }}
}}
]

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`", for every model that in prompt:

```json
[
{{
	"Model": string  // Describes the world name from database. Model name should be exact the same as one of the world in the context.
    "Pose": x,y,z // float numbers representing position of the model in the global frame
}}
]
```

If output has a multiple list elements it should formatted as json list.

"""
