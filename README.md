# wals-language-change-python
Python scripts for studying distribution of WALS features in family trees

# Usage
Download a [WALS](wals.info) feature in tab-separated format (i.e., as a txt file).

Then run "python wals-family-tree-search.py FILE"

# Output
Three lists:
1) A list of all transitions and number of supporting links sorted by initial state
2) A list of all transitions and number of supporting links sorted by final state
3) A list of all transitions and the exact links that support them

Also generates a state diagram, which shows the probability of moving from one value to any of the other values.
