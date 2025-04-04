# Rule Based Automata
* New implementation of the rule based engine

## Differences
* This implementation will use a graph to represent the entire database
* This will allow matching against the entire database at the same time (with significantly better complexity)
* This implementation will also need to prevent circular rules



## Implementation
* Need to know the types of input variables for each rule
* Parse Given Databases
    1. Accept databases as args
    2. Open each database
    3. Add each clause one-by-one
        * Make sure to prevent circular rules
        * For each clause smaller than its replacement, see if it matches with any tokens of the replacement
            * If there is a match, ignore this clause
    4. Accept list of tokens as input to optimize
* Optimization
    1. Given a list of tokens as input,
    2. Starting at each token of the input,
    3. Follow down the tree as far as possible, consuming as many tokens as possible
    4. Once out of matches or reaching the end of the input string, see if there is a replacement at the current node
        * While there is no replacement at the current node, go back up the graph by 1 node
        * If you reach the head of the tree and there is no replacement, continue to the next starting point
        * If there is ever a replacement, replace the matched tokens with the replacement and move the starting index to after the replacement's end
    5. If there were any replacements made in the list, rerun through the list again (back to step 2)

## New Syntax
```
. - Match any token
* - Repeat this token 0 or more times
$ - variable access (when replacement is made, replace with whatever is contained in this variable)
# - internal variable (when replacement is made, renumber to prevent conflicts)
```
