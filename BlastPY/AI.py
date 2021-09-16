import random
import json
import copy
import math
from typing import Union
import time
from .ProgressBar import progressbar


class BlastAI:
    def __init__(self, save: Union[str, None] = None):
        self.save = save
        self.predict = lambda values: self._predict(values, self.nodes, len(
            self.questions[0][1]) if len(self.questions) > 0 and len(self.questions[0]) > 1 else 1)

        if self.save:
            try:
                saves = open(self.save, "rb")
                data = json.loads(saves.read())
                self.nodes: list = data["nodes"]
                self.oldnodes: list = data["oldnodes"]
                self.results: float = data["results"]
                self.questions: list = data["questions"]
                self.gen: int = data["gen"]
                saves.close()
                del saves
                del data
            except:
                self.nodes = []
                self.oldnodes = []
                self.results = None
                self.questions = []
                self.gen = 0
        else:
            self.nodes = []
            self.oldnodes = []
            self.results = None
            self.questions = []
            self.gen = 0

    def _nodesToCode(self, nodes, inputlength, outputlength):
        output = []
        output.append("# INPUTS")

        output.append('INPUTS = ['+(", ".join([('\n    'if i %
                                                10 == 0 else '')+"0" for i in range(inputlength)]))+" # CHANGE ME!\n]")
        output.append("")
        output.append("# OUTPUTS")
        output.append('OUTPUTS = ['+(", ".join([('\n    'if i %
                                                 10 == 0 else '')+"0" for i in range(outputlength)]))+" # DONT CHANGE ME!\n]")
        output.append("")
        output.append("# ALGORITHM")

        usemathlib = False

        def addlines(nodes, indents):
            nonlocal usemathlib
            output = []
            for node in nodes:
                if node["type"] == "add":
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} += {node["second"] if type(node["second"])==float else f"""INPUTS[{node["second"]}]"""}')
                elif node["type"] == "subtract":
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} -= {node["second"] if type(node["second"])==float else f"""INPUTS[{node["second"]}]"""}')
                elif node["type"] == "multiply":
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]""" if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} *= {node["second"] if type(node["second"])==float else f"""INPUTS[{node["second"]}]"""}')
                elif node["type"] == "divide" and "second" in node:
                    if node["second"] != 0:
                        totab = False
                        if type(node["second"]) == str:
                            output.append(
                                f'{"    "*indents}if INPUTS[{node["second"]}] != 0:')
                            totab = True
                        output.append(
                            f'{"    "*indents}{"    "if totab else ""}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} /= {node["second"] if type(node["second"])==float else f"""INPUTS[{node["second"]}]"""}')
                elif node["type"] == "power":
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} **= {node["second"] if type(node["second"])==float else f"""INPUTS[{node["second"]}]"""}')
                elif node["type"] == "floor":
                    usemathlib = True
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} = math.floor({f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""}.real)')
                elif node["type"] == "ceil":
                    usemathlib = True
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} = math.ceil({f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""}.real)')
                elif node["type"] == "round":
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} = round({f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""}.real)')
                elif node["type"] == "zeromin":
                    output.append(
                        f'{"    "*indents}{f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""} = max([0, {f"""OUTPUTS[{node["first"][6:]}]"""if node["first"].startswith("output") else f"""INPUTS[{node["first"]}]"""}.real])')
                elif node["type"] == "statement":
                    isoutput = addlines(node["is"], indents+1)
                    elseoutput = addlines(node["else"], indents+1)
                    if len(isoutput) != 0:
                        output.append(
                            f'{"    "*indents}if {f"""OUTPUTS[{node["condition"]["first"][6:]}]"""if node["condition"]["first"].startswith("output") else f"""INPUTS[{node["condition"]["first"]}]"""} {node["condition"]["type"]} {node["condition"]["second"] if type(node["condition"]["second"])==float else f"""INPUTS[{node["condition"]["second"]}]"""}:')
                        output.extend(isoutput)
                    if len(elseoutput) != 0:
                        if len(isoutput) == 0:
                            output.append(
                                f'{"    "*indents}if not {f"""OUTPUTS[{node["condition"]["first"][6:]}]"""if node["condition"]["first"].startswith("output") else f"""INPUTS[{node["condition"]["first"]}]"""} {node["condition"]["type"]} {node["condition"]["second"] if type(node["condition"]["second"])==float else f"""INPUTS[{node["condition"]["second"]}]"""}:')
                        else:
                            output.append(f'{"    "*indents}else:')
                        output.extend(elseoutput)
            return output
        output.extend(addlines(nodes, 0))
        if usemathlib:
            output.insert(0, "")
            output.insert(0, "import math")
            output.insert(0, "# IMPORTS")

        output.append("")
        output.append("# DONE!")

        output.append("print(\"OUTPUTS:\", OUTPUTS)")

        output.insert(0, "")
        output.insert(0, "# GENERATED BY BlastAI")
        return output

    def toPythonCode(self):
        return "\n".join(self._nodesToCode(self.nodes, len(self.questions[0][0]), len(self.questions[0][1]) if len(self.questions) > 0 and len(self.questions[0]) > 1 else 1))

    def completelyRandom(self):
        return (1./random.random())-1

    def complextofloat(self, x: Union[complex, int, float]):
        if isinstance(x, complex):
            return x.real
        return x

    def _predict(self, values: list, nodes: list, outputlength: int) -> float:
        try:
            vals = {}
            for i in range(outputlength):
                vals[f"output{i}"] = 0
            for i in range(len(values)):
                vals[str(i)] = values[i]

            def predict(nodes):
                nonlocal vals
                for node in nodes:
                    if node["type"] == "add":
                        vals[node["first"]] += node["second"] if isinstance(
                            node["second"], float) else vals[node["second"]]
                    elif node["type"] == "subtract":
                        vals[node["first"]] -= node["second"] if isinstance(
                            node["second"], float) else vals[node["second"]]
                    elif node["type"] == "multiply":
                        vals[node["first"]] *= node["second"] if isinstance(
                            node["second"], float) else vals[node["second"]]
                    elif node["type"] == "divide":
                        number = (node["second"] if type(node["second"])
                                  == float else vals[node["second"]])
                        if number != 0:
                            vals[node["first"]] /= node["second"] if type(
                                node["second"]) == float else vals[node["second"]]
                    elif node["type"] == "power":
                        vals[node["first"]] **= node["second"]
                    elif node["type"] == "floor":
                        vals[node["first"]] = math.floor(
                            vals[node["first"]].real)
                    elif node["type"] == "ceil":
                        vals[node["first"]] = math.ceil(
                            vals[node["first"]].real)
                    elif node["type"] == "round":
                        vals[node["first"]] = round(vals[node["first"]].real)
                    elif node["type"] == "zeromin":
                        vals[node["first"]] = max(
                            [0, vals[node["first"]].real])
                    elif node["type"] == "statement":
                        if (node["condition"]["type"] == "==" and vals[node["condition"]["first"]] == (node["condition"]["second"] if isinstance(node["condition"]["second"], float) else vals[node["condition"]["second"]])) or (node["condition"]["type"] == "!=" and vals[node["condition"]["first"]] != (node["condition"]["second"] if isinstance(node["condition"]["second"], float) else vals[node["condition"]["second"]])) or (node["condition"]["type"] == ">" and vals[node["condition"]["first"]] > (node["condition"]["second"] if isinstance(node["condition"]["second"], float) else vals[node["condition"]["second"]])) or (node["condition"]["type"] == "<" and vals[node["condition"]["first"]] < (node["condition"]["second"] if isinstance(node["condition"]["second"], float) else vals[node["condition"]["second"]])) or (node["condition"]["type"] == ">=" and vals[node["condition"]["first"]] >= (node["condition"]["second"] if isinstance(node["condition"]["second"], float) else vals[node["condition"]["second"]])) or (node["condition"]["type"] == "<=" and vals[node["condition"]["first"]] <= (node["condition"]["second"] if isinstance(node["condition"]["second"], float) else vals[node["condition"]["second"]])):
                            predict(node["is"])
                        else:
                            predict(node["else"])
            predict(nodes)
            return [vals[f"output{i}"] for i in range(outputlength)]
        except Exception:
            return None

    def _moreEfficent(self, nodes):
        lastoutput = 0
        for i in range(len(nodes)):
            if nodes[i]["type"] == "statement" or nodes[i]["first"].startswith("output"):
                lastoutput = i
        nodes = nodes[0:lastoutput+1]
        return nodes

    def _generateNode(self, nodes, oldnodes, firstchoices, secondchoices, numberofoutputs):
        editednodes = copy.deepcopy(
            oldnodes) if random.random() <= 0.5 else copy.deepcopy(nodes)

        def adding(editednodes, addlimit):
            if len(editednodes) > 0:
                delete = 0
                for node in editednodes:
                    if 0.25 >= random.random():
                        if 0.5 >= random.random():
                            delete += 1
                            editednodes.remove(node)
                        elif node["type"] != "statement":
                            if 0.5 >= random.random():
                                node["type"] = random.choice(
                                    ["add", "subtract", "multiply", "divide", "power", "floor", "ceil", "round", "zeromin"])
                            if 0.5 >= random.random():
                                node["first"] = random.choice(firstchoices)
                            if (node["type"] not in ["floor", "ceil", "round", "zeromin"] and "second" not in node) or (node["type"] not in ["floor", "ceil", "round", "zeromin"] and 0.5 >= random.random()):
                                secondchoicescopy = copy.copy(
                                    secondchoices)
                                secondchoicescopy.append(
                                    self.completelyRandom())
                                node["second"] = random.choice(
                                    secondchoicescopy)
                        else:
                            if 0.5 >= random.random():
                                node["is"] = adding(node["is"], 2)
                            if 0.5 >= random.random():
                                node["else"] = adding(node["else"], 2)
            for i in range(random.randint(0, (addlimit))):
                types = random.choice(
                    ["add", "subtract", "multiply", "divide", "power", "floor", "ceil", "round", "zeromin", "statement"])
                secondchoicescopy = copy.copy(secondchoices)
                secondchoicescopy.append(self.completelyRandom())
                if types != "statement":
                    if types not in ["floor", "ceil", "round", "zeromin"]:
                        editednodes.append({"type": types, "first": random.choice(
                            firstchoices), "second": random.choice(secondchoicescopy)})
                    else:
                        editednodes.append(
                            {"type": types, "first": random.choice(firstchoices)})
                else:
                    condition = {"first": random.choice(
                        firstchoices), "type": random.choice(
                        ["==", "!=", ">", "<", ">=", "<="]), "second": random.choice(secondchoicescopy)}
                    editednodes.append({"type": "statement",
                                        "condition": condition, "is": adding([], 2), "else": adding([], 2)})
            return editednodes
        editednodes = self._moreEfficent(
            adding(editednodes, max([0, len(editednodes)-numberofoutputs])+10))
        return editednodes

    def appendQuestions(self, questions: list):
        self.questions.extend(questions)

    def exam(self, nodescount: int, testquestions: list = [], nodes=None, numberlimit=None, appendNewQuestionsToOldQuestions=True):
        if appendNewQuestionsToOldQuestions:
            self.appendQuestions(testquestions)
            questions = self.questions
        else:
            questions = testquestions
        questionslength = len(questions)
        firstchoices = []
        secondchoices = []
        for i in range(len(
                questions[0][0])):
            firstchoices.append(f"output{i}")
        numberofoutputs = len(questions[0][1]) if questionslength > 0 and len(
            questions[0]) > 1 else 1
        for i in range(numberofoutputs):
            firstchoices.append(str(i))
            secondchoices.append(str(i))
        result = None
        worstofbest = None
        best = None
        skip = 0
        for node in progressbar(range(nodescount), "testing node trees: "):
            try:
                nodes = self._generateNode(
                    self.nodes, self.oldnodes, firstchoices, secondchoices, numberofoutputs)
                finalresult = 0
                breaks = False
                worst = 0
                for i in range(questionslength):
                    question = questions[i]
                    questionsresults = 0
                    starttime = time.perf_counter()
                    predictions = self._predict(question[0], nodes, len(
                        questions[0][1]) if questionslength > 0 and len(questions[0]) > 1 else 1)
                    timed = time.perf_counter() - starttime
                    if predictions:
                        predictionslen = len(predictions)
                        for j in range(predictionslen):
                            howclose = abs(
                                question[1][j].real - predictions[j].real)
                            howclose += timed
                            if numberlimit and numberlimit < howclose:
                                howclose = numberlimit
                            questionsresults += howclose
                            if worst < howclose:
                                worst = howclose
                            if worstofbest and worstofbest < howclose:
                                skip += 1
                                breaks = True
                                break
                        if breaks:
                            break
                        finalresult += questionsresults
                    else:
                        breaks = True
                        break
                finalresult /= questionslength
                if not breaks:
                    if not result or result > finalresult:
                        worstofbest = worst
                        result = finalresult
                        best = nodes
            except Exception:
                pass
        added = False
        if not self.results or self.results > result:
            added = True
            self.results = result
            self.oldnodes = self.nodes
            self.nodes = best
            self.gen += 1
        if self.save:
            try:
                saves = open(self.save, "w")
                saves.write(json.dumps(
                    {"results": self.results, "nodes": self.nodes, "oldnodes": self.oldnodes, "questions": self.questions, "gen": self.gen}))
                saves.close()
                del saves
            except Exception as e:
                print("SAVE ERROR:", str(e))
        return (result, added)
