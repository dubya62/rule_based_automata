
import math


# TODO: add state for special syntax
class Clause:
    """
    A single clause of information to be added to the graph
    """
    def __init__(self):
        self.content:list[str] = []
        self.replacement:Clause = None
        self.metric:float = 0.0

        # variable mappings
        # example: [None, 1, None, 2]
        self.internal_variables = [None] * len(self.content)
        self.variables = [None] * len(self.content)

    def handle_mappings(self):
        self.internal_variables = [None] * len(self.content)
        self.variables = [None] * len(self.content)

        i = 0
        n = len(self.content)
        while i < n:
            m = len(self.content[i]) - 1
            while m > 0:
                if self.content[i][m] == "$":
                    self.variables[i] = int(self.content[i][m+1:])
                    self.content[i] = self.content[:m]
                elif self.content[i][m] == "#":
                    self.internal_variables[i] = int(self.content[i][m+1:])
                    self.content[i] = self.content[:m]
                m -= 1
            i += 1


class Node:
    """
    A single node for the graph.
    Allows following the graph to match strings
    """
    def __init__(self, replacement=None):
        self.children = {}
        self.replacement = replacement


class Graph:
    """
    Can be executed on an input list to optimize
    """
    def __init__(self):
        self.head = Node()

    def add_clause(self, clause:Clause):
        """
        Add a clause object to the graph while handling circular rules
        """
        print("Adding clause...")
        # TODO: check if this creates a circular rule

        # add required nodes
        # TODO: account for special syntax
        current_node = self.head
        for i, x in enumerate(clause.content):
            print(f"--- : {x} ")
            if x in current_node.children:
                print("Already exists")
                current_node = current_node.children[x]
            else:
                print("Creating new node")
                new_node = Node()
                if i == len(clause.content)-1:
                    print(f"Gave node a replacement of {clause.replacement}")
                    new_node.replacement = clause.replacement

                current_node.children[x] = new_node
                current_node = new_node


    def execute(self, tokens:list[str]):
        """
        Execute the current graph on a list of strings
        """
        # TODO: recursively match against nodes for the forward pass
        # TODO: check if replacement is available for backward pass
        return None



class Parser:
    """
    Parses a database file to create a graph
    Requires knowing the metric and direction to optimize with
    """
    def __init__(self, database_filenames:list[str], direction:int, metric:int):
        self.database_filenames = database_filenames
        self.direction = direction
        self.metric = metric

        file_data = self.parse_files()
        self.graph = self.parse_file_data(file_data)


    def parse_files(self):
        file_data = ""
        for filename in self.database_filenames:
            try:
                with open(filename, 'r') as f:
                    file_data += f.read()
                    file_data += "\n"
            except:
                print(f"Unable to open {filename}")
                exit(1)
        return file_data


    def parse_file_data(self, file_data):
        result = Graph()

        # read through the file data, parsing into clauses
        current_rule:list[Clause] = []
        clause_data = []

        all_clauses = []

        quotes = 0
        backslashes = 0

        # TODO: Special syntax

        i = 0
        n = len(file_data)
        while i < n:
            if file_data[i] == '"':
                if backslashes % 2 == 0:
                    quotes ^= 1

                    if quotes == 0:
                        # we just reached the end of a clause. 
                        # get the metrics for this clause
                        the_metric = None
                        if i + 1 < n and file_data[i+1] == "~":
                            # get content until =
                            i += 1
                            start = i + 1
                            while i < n and file_data[i] not in ["=", ";"]:
                                i += 1
                            content = file_data[start:i]
                            content = content.split(":")

                            try:
                                the_metric = float(content[self.metric])
                            except:
                                if self.direction > 0:
                                    the_metric = -math.inf
                                else:
                                    the_metric = math.inf
                            i -= 1

                        print(the_metric)

                        # add it to the current rule
                        new_clause = Clause()
                        new_clause.content = [x for x in "".join(clause_data).split(" ") if len(x) > 0]
                        new_clause.metric = the_metric
                        current_rule.append(new_clause)
                        clause_data = []
                    else:
                        i += 1
                        continue
            elif file_data[i] == "\\":
                backslashes += 1
            elif file_data[i] == ";":
                if quotes == 0:
                    # we just reached the end of a rule. handle all clauses of this rule
                    if len(current_rule) > 0:
                        best = current_rule[0]
                        for clause in current_rule:
                            if self.direction > 0:
                                if clause.metric > best.metric:
                                    best = clause
                            else:
                                if clause.metric < best.metric:
                                    best = clause

                        for clause in current_rule:
                            if clause != best:
                                clause.replacement = best
                            else:
                                clause.replacement = None
                        all_clauses += current_rule

                    current_rule = []
            if file_data[i] != "\\":
                backslashes = 0

            if quotes == 1:
                if file_data[i] == "\\" and backslashes % 2 == 1:
                    i += 1
                    continue

                clause_data += file_data[i]


            i += 1

        print(all_clauses)
        for clause in all_clauses:
            print(clause.content)

        print("Adding all clauses")
        for clause in all_clauses:
            clause.handle_mappings()
            result.add_clause(clause)

        return result


if __name__ == "__main__":
    parser = Parser(["test.rbe"], -1, 0)



