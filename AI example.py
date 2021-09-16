from BlastPY.AI import BlastAI


ai = BlastAI("FIRSTAI.dat")

if len(ai.questions) == 0:
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
    print(ai.gen)
    print(ai.exam(1000))
    open("compiled.py", "w").write(ai.toPythonCode())
