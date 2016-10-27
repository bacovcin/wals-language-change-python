import sys

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
        for line in lines[i+1:]:
            s = line.rstrip().split('\t')
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
            geni = []
            for key2 in lgg[key1]:
                tmp = {}
                for lang in lgg[key1][key2]:
                    try:
                        tmp[lgg[key1][key2][lang]].append(lang)
                    except KeyError:
                        tmp[lgg[key1][key2][lang]] = [lang]
                # Get maximum value item
                tmp_keys = sorted(tmp.keys(),
                                  key=lambda x: len(tmp[x]),
                                  reverse=True)
                gen_val = tmp_keys[0]
                # Assign all genus to language changes
                for key in tmp_keys:
                    for lang in tmp[key]:
                        try:
                            output[(gen_val, key)].append((key2 + ' (gen)',
                                                           lang))
                        except KeyError:
                            output[(gen_val, key)] = [(key2 + ' (gen)', lang)]
                geni.append((key2, gen_val))
            tmp = {}
            for genus in geni:
                try:
                    tmp[genus[1]].append(genus[0])
                except KeyError:
                    tmp[genus[1]] = [genus[0]]
            # Get maximum value item
            tmp_keys = sorted(tmp.keys(),
                              key=lambda x: len(tmp[x]),
                              reverse=True)
            fam_val = tmp_keys[0]
            # Assign all genus to language changes
            for key in tmp_keys:
                for genus in tmp[key]:
                    try:
                        output[(fam_val, key)].append((key1+' (fam)',
                                                       genus+' (gen)'))
                    except KeyError:
                        output[(fam_val, key)] = [(key1+' (fam)',
                                                   genus + ' (gen)')]
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
