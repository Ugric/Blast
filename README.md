# BlastPY
a machine learning framework by W̷̛͒i̶̓͗l̷͗̌ľ̶͘

# Example
```
from BlastPY.AI import BlastAI

# create AI or load from file
ai = BlastAI("FIRSTAI.dat")

if len(ai.questions) == 0:  # check if no questions have been added

    # add questions
    # [list-of-input-to-AI, list-of-wanted-outputs-from-AI]
    ai.appendQuestions([[[0], [0]],
                        [[1], [1]],
                        [[2], [2]],
                        [[3], [6]],
                        [[4], [8]],
                        [[5], [10]],
                        [[6], [30]],
                        [[7], [44]],
                        [[8], [51]],
                        [[9], [56]],
                        [[10], [56]]
                        ])

while True:

    # the AI generation
    print(ai.gen)

    # examen the AI
    print(ai.exam(1000))

    # compile the AI to python code
    open("compiled.py", "w").write(ai.toPythonCode())
```

# Licence
This project is licensed under the terms of the MIT license.