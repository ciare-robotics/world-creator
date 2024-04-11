fmt_scale_qa_tmpl = """
Models for scaling: {models_for_scaling}
---

Please provide a realistic scaling factor for a list of 3D models based on their names and current sizes,
with the objective of placing these models into user prompt context. \n

Use the model name and its dimensions (width, depth, height in meters) to determine an appropriate scale factor. \n
The scale factor should adjust the model's size to realistically fit within user prompt context, maintaining correct  proportional relationships among the models.

Try to reason internall about each scale factor, and provide a scale factor that makes sense in the context of the prompt. \n
It's very important to provide a scale factor that makes sense in the context of the prompt. \n

Example:
Models:
[
{{
	"Model": "Syringe",
    "Size":[1598.2947998 200. 1617.05322266]
}},
{{
    "Model": "Old hospital bed (PBR|GR)",
    "Size":[133.21003923 130.34797506 210.01590606]
}},
{{
    "Model": "Pills",
    "Size":[0.09257923 0.15060198 0.09353124]
}},
{{
    "Model": "Chair",
    "Size":[3.51076342 4.01976532 3.58686519]
}},
{{
    "Model": "Table",
    "Size":[0.056 0.0322 0.06]
}}
]


"answer": 
[
{{
	"Model": "Syringe",
    "Scale": 0.0001
}},
{{
    "Model": "Old hospital bed (PBR|GR)",
    "Scale": 0.01
}},
{{
    "Model": "Pills",
    "Scale": 1.0
}},
{{
    "Model": "Chair",
    "Scale": 0.1
}},
{{
    "Table": "Chair",
    "Scale": 10.0
}}
]

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`", for every model that in prompt:

```json
[
{{
	"Model": string  // Describes the world name from database. Model name should be exact the same as one of the world in the context.
    "Scale": float // float numbes representing scale of model
}}
]
```

If output has a multiple list elements it should formatted as json list.

"""
