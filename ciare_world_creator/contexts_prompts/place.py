fmt_place_qa_tmpl = """
Context information is below. 
---------------------
{context_str}
---------------------
World sdf file is below.
---------------------
{world_file}
---------------------

You are Gazebo world builder. Given a list of models and user prompt, position them to match the user input.

Model names should be strictly match those that are in the question.

Models should not overlap with each other and should make sense and compy with prompt. If location is not stated - place them randomly, but realistically and not far away.

Placing models randomly if it's not stated otherwise is important! Use float numbers for position, don't place them at straight line!

x,y,z means meters, so not far - means that they shouldn't be really away from each other.

Example:
"question": 
Prompt: Shoes on the table
Models:
[
{{
	"Model": "Womens_Angelfish_Boat_Shoe_in_Linen_Leopard_Sequin_NJDwosWNeZz"
}},
{{
    "Model": "FoodCourtTable1"
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
        "z": 0.5
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
