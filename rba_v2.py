
import math
import tokens as tokens_def


class Clause:
    """
    A single clause of information to be added to the graph
    """
    def __init__(self):
        self.content:list[str] = []
        self.replacement:Clause = None
        self.metric:float = 0.0
        self.internal_variables = []

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

    def add_clause(self, clause:Clause, circular=False):
        """
        Add a clause object to the graph while handling circular rules
        """
        print(f"Adding clause...: {clause.content} -> {clause.replacement}")
        
        # add a new variable to function args: whether or not this is checking for circular rule: circular=False on first pass
        if not circular and clause.replacement is not None: 
            print(f"Checking circular: {clause.content} --- {clause.replacement.content}")
            new_graph = Graph() # create a new graph 
            
            # create a copy of the original clause
            new_clause = Clause()
            new_clause.content = clause.content[:]
            new_clause.replacement = Clause()
            new_graph.add_clause(new_clause, circular=True)
            replacement_made = new_graph.execute(clause.replacement.content, replace=False)
            print("Replacement made:")
            print(replacement_made)
            
            # if the execution ever made a replacement, stop execution
            if replacement_made == True:
                print(f"[Circular Check] Detected circular rule for clause: {clause.content}")
                print(f"[Circular Check] Not adding clause to graph: {clause.content}")
                # do not add to graph 
                return
            
            print("No Circular rule detected for this clause")
        

        # add required nodes
        current_node = self.head
        for i, x in enumerate(clause.content):
            #print(f"--- : {x} ")
            if x in current_node.children:
                #print("Already exists")
                current_node = current_node.children[x]
            else:
                #print("Creating new node")
                new_node = Node()
                if i == len(clause.content)-1:
                    print(f"Gave node a replacement of {clause.replacement}")
                    new_node.replacement = clause.replacement

                current_node.children[x] = new_node
                current_node = new_node


    # optimize the graph 
    def execute(self, tokens:list[str], replace=True, varnum=0):
        """
        Execute the current graph on a list of strings
        Replaces matched token sequences with the replacement string 
        """
        
        # 2. starting at each token of the input 
        while True:
            modified = False # check if any replacements were made 
            i = 0 # starting index for the current token 
            
            while i < len(tokens): # loop through the tokens 
                print(f"Starting at token index {i}: {tokens[i]}")
            
                # 3. follow down the tree as far as possible, consuming as many tokens as possible 
                def match_forward(node, token_index, path):
                    print(f"Attempting match")
                    if token_index >= len(tokens):
                        print("Ran out of input tokens")
                        return path
                    if tokens[token_index] in node.children:
                        print(f"Token {tokens[token_index]} matched in {node.children}")
                        next_node = node.children[tokens[token_index]]
                        path.append(next_node)
                        return match_forward(next_node, token_index + 1, path)
                    if "#" in node.children:
                        print(f"Token {tokens[token_index]} matched in {node.children} with #")
                        next_node = node.children["#"]
                        path.append(next_node)
                        return match_forward(next_node, token_index + 1, path)
                    print(f"No matching node in graph {tokens[token_index]}, {node.children}")
                    return path
                
                print("Attempting Match")
                # start matching/tracking path from head node 
                path = [self.head]
                path = match_forward(self.head, i, path)
            
                def match_backward(path):
                    # check if there is a replacement at the current node if not, go back up the graph by 1 node
                    for node in reversed(path):
                        if node.replacement:
                            return node
                    return None 
            
                matched_node = match_backward(path) 
            
                if matched_node: 
                    # determine the start and end of the matched tokens 
                    j = i + len(path) - 1
                    print(f"Replacement found: {matched_node.replacement.content}")
                    
                    replacement = [x for x in matched_node.replacement.content]
                    print("Replacement variables")
                    print(matched_node.replacement.internal_variables)
                    varmap = {}
                    for x in range(len(replacement)):
                        the_var = matched_node.replacement.internal_variables[x]
                        print(f"varmap = {varmap}")
                        print(f"var[{x}] = {the_var}")
                        if the_var == -1:
                            continue

                        if the_var not in varmap:
                            varmap[the_var] = varnum
                            varnum += 1

                        the_type = replacement[x].type if hasattr(replacement[x], "type") else []
                        print(f"Replacement type ({replacement[x]}) ({type(replacement[x])}): {the_type}")
                        replacement[x].token = f"#{varmap[the_var]}"
                        # replacement[x] = tokens_def.VariableToken(tokens_def.Token("#" + str(varmap[the_var]), "", 0), "", 0, tokens_def.Token("vartoken", "", 0), tokens_def.TypeToken(tokens_def.Token("#TYPE", "", 0), "", 0, the_type))

                    tokens = tokens[:i] + replacement + tokens[j:]
                    print(f"Tokens after replacement: {tokens}")
                    
                    # move the starting index to after the replacement's end 
                    i = i + len(replacement)
                    modified = True 
                    if not replace:
                        return True, varnum
                    
                else: 
                    print("No replacement found, moving to next token")
                    i += 1
                
            # 5. if there were any replacements made in the list, rerun through the list again (back to step 2)
            if not modified:
                print("No modifications made in this pass, exiting")
                break

        if not replace:
            return False, varnum
            
        return tokens_def.Tokens(tokens), varnum



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

        # handle type awareness
        for clause in all_clauses:
            for i in range(len(clause.content)):
                if "#" in clause.content[i]:
                    if "(" in clause.content[i]:
                        typeval = ""
                        paren_index = clause.content[i].index("(")
                        type_toks = clause.content[i][paren_index+1:]
                        clause.content[i] = clause.content[i][:paren_index]
                        for tok in type_toks:
                            typeval += tok
                    else:
                        typeval = ""
                    new_token = tokens_def.VariableToken(clause.content[i], "", 0, "vartoken", tokens_def.TypeToken(tokens_def.Token("#TYPE", "", 0), "", 0, [tokens_def.Token(f"{typeval}", "", 0)]))
                else:
                    new_token = tokens_def.Token(clause.content[i], "", 0)
                print("Made type aware token")
                clause.content[i] = new_token


        # handle internal variables
        for clause in all_clauses:
            for i in range(len(clause.content)):
                if "#" in clause.content[i]:
                    clause.internal_variables.append(int(clause.content[i][1:]))
                    clause.content[i].token = "#"
                else:
                    clause.internal_variables.append(-1)


        print(all_clauses)
        for clause in all_clauses:
            print(clause.content)

        print("Adding all clauses")
        for clause in all_clauses:
            result.add_clause(clause)

        return result


if __name__ == "__main__":
    parser = Parser(["c.rbe"], -1, 2)
    # test the graph 
    print("\nTesting graph...")
    tokens = ["a", "b", "c", "d", "e", "chill", "guy"]
    print("Tokens before execution: ", tokens) 
    result, varnum = parser.graph.execute(tokens)
    print("Tokens after execution: ", result)
    
    # test the circular rule 
    print("\nChecking for circular rule...")
    circular_rule = Clause()
    circular_rule.content = ["a", "b", "c"]
    circular_rule.replacement = circular_rule 
    parser.graph.add_clause(circular_rule)
    print("Tokens after adding circular rule: ", result)

