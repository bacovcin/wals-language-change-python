import sys
from graphviz import Digraph

# Go through all command line arguments and apply process
for arg in sys.argv:
    # Try to run on all .txt files
    if arg.split('.')[-1] == 'txt':
        # Read in all the lines
        infile = open(arg)
        lines = infile.readlines()
        infile.close()

        # Extract the column names
        i = 0
        while True:
            try:
                if lines[i].split('\t')[0] == 'wals code':
                    break
                i += 1
            except:
                i += 1
        names = lines[i].rstrip().split('\t')

        # Find which columns store language name, value, genus and family
        ln_col = names.index('name')
        val_col = names.index('description')
        gen_col = names.index('genus')
        fam_col = names.index('family')

        # Create a dictionary of dictionaries with the follow key-value
        # pairs:
        # family -> dictionary of genuses
        # genus -> dictionary of languages
        # language -> value

        lgg = {}

        # Also track the number of languages with each value for deciding ties
        global_vals = {}

        for line in lines[i+1:]:
            s = line.rstrip().split('\t')
            try:
                global_vals[s[val_col]].append(s[ln_col])
            except KeyError:
                global_vals[s[val_col]] = [s[ln_col]]
            try:
                lgg[s[fam_col]][s[gen_col]][s[ln_col]] = s[val_col]
            except KeyError:
                try:
                    lgg[s[fam_col]][s[gen_col]] = {}
                    lgg[s[fam_col]][s[gen_col]][s[ln_col]] = s[val_col]
                except KeyError:
                    lgg[s[fam_col]] = {}
                    lgg[s[fam_col]][s[gen_col]] = {}
                    lgg[s[fam_col]][s[gen_col]][s[ln_col]] = s[val_col]

        # Collect list of changes in dictionary:
        # (start form, end form) -> list of tuples (start name, end name)
        output = {}
        for key1 in lgg:
            # Assign values to the genuses with tuples used in cases of ties
            geni = {}
            for key2 in lgg[key1]:
                tmp = {}
                for lang in lgg[key1][key2]:
                    try:
                        tmp[lgg[key1][key2][lang]].append(lang)
                    except KeyError:
                        tmp[lgg[key1][key2][lang]] = [lang]
                # Look for maximum value or ties
                best = []
                cur_best_len = 0
                for key in tmp:
                    if len(tmp[key]) > cur_best_len:
                        best = [key]
                    elif len(tmp[key]) == cur_best_len:
                        best.append(key)
                geni[key2] = best
            # Get proportion of values at family level
            tmp = {}
            for key2 in geni:
                for val in geni[key2]:
                    try:
                        tmp[val].append(key2)
                    except KeyError:
                        tmp[val] = [key2]

            tmp_keys = sorted(tmp.keys(),
                              key=lambda x: (-len(tmp[x]),
                                             -len(global_vals[x])))

            fam_val = tmp_keys[0]
            # For each genus, identify the correct value (resolving ties)
            # add the resulting transitions to "output"
            for key2 in geni:
                gen_val = geni[key2]
                if len(gen_val) > 1:
                    gen_val = sorted(gen_val, key=lambda x: tmp_keys.index(x))[0]
                else:
                    gen_val = gen_val[0]
                try:
                    output[(fam_val, gen_val)].append((key1 + ' (fam)',
                                                       key2 + ' (gen)'))
                except KeyError:
                    output[(fam_val, gen_val)] = [((key1 + ' (fam)',
                                                   key2 + ' (gen)'))]
                for lang in lgg[key1][key2]:
                    lan_val = lgg[key1][key2][lang]
                    try:
                        output[(gen_val, lan_val)].append((key2 + ' (gen)',
                                                           lang))
                    except KeyError:
                        output[(gen_val, lan_val)] = [((key2 + ' (gen)',
                                                       lang))]

        # Print out output
        outfile = open(arg.split('.')[0]+'-output.txt', 'w')
        outfile.write('Number of transitions (sorted by start)\n')
        skeys = sorted(output.keys(), key=lambda x: (x[0], -len(output[x])))
        for key in skeys:
            outfile.write(key[0]+' -> '+key[1]+': ' + str(len(output[key]))+'\n')
        outfile.write('\n+Number of transitions (sorted by end)\n')
        skeys = sorted(output.keys(), key=lambda x: (x[1], -len(output[x])))
        for key in skeys:
            outfile.write(key[0]+' -> '+key[1]+': ' + str(len(output[key]))+'\n')
        outfile.write('\n+Names of all transitions:\n')
        for key in skeys:
            outfile.write(key[0]+' -> '+key[1]+'\n')
            for val in output[key]:
                outfile.write('\t'+val[0] + ' -> ' + val[1] + '\n')

        # Generate a state diagram
        dot = Digraph(comment='Transition State Diagram')

        # Create new dictionary with following structure:
        # start state -> dictionary
        # end state -> number of examples
        graph_dict = {}
        for key in output:
            try:
                graph_dict[key[0]][key[1]] = float(len(output[key]))
            except KeyError:
                graph_dict[key[0]] = {}
                graph_dict[key[0]][key[1]] = float(len(output[key]))

        # Create nodes
        i = 0
        node_dict = {}
        for key in graph_dict:
            dot.node(str(i), key)
            node_dict[key] = str(i)
            i += 1

        # Create edges
        for key in graph_dict:
            total_num = sum([graph_dict[key][x] for x in graph_dict[key]])
            for key2 in graph_dict[key]:
                percent = int(100*(graph_dict[key][key2]/total_num))
                dot.edge(node_dict[key],
                         node_dict[key2],
                         label='%.2f' % percent,
                         constraint='false')

        # Save state diagram
        dot.render(arg.split('.')[0]+'-graph.gv')
