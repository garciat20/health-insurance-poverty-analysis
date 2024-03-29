"""
Helper to get the FIPS code/state names for US states
"""

import re

def parse_fips_file():
    """
    TODO: review code to see if works
    """
    keep_processing = False
    stop_processing = "county-level"

    state_code_andnames = {}

    with open("data/fips.txt") as f:
        for line in f:
            # elimniate all whitespace in a row
            columns = re.split('\s+', line.strip())

            # if multiple columns, combine the state names that have a space like "North Carolina"
            complete_state_name = ""

            # this is where i want to start iterating in the file
            if columns[0] == "-----------":
                keep_processing = True
                continue
            
            # lets stop here
            elif columns[0] == stop_processing:
                break

            # lets process the data
            if keep_processing:
                if len(columns) > 2:
                    for i in range(1, len(columns)):
                        # combine the state names that have spaces
                        complete_state_name += columns[i] + " "
                    # strip any leading whitespace
                    complete_state_name = complete_state_name.strip()

                    # key is going to be the fips code and the value is going to be the state name
                    state_code_andnames[columns[0]] = complete_state_name

                elif len(columns) == 2:
                    # key is going to be the fips code and the value is going to be the state name
                    state_code_andnames[columns[0]] = columns[1]

    return state_code_andnames

def get_state_names_by_fips_order():
    data = parse_fips_file()
    state_names = []
    for name in data.values():
        state_names.append(name)
    return state_names

def get_fips_in_seq_order():
    data = parse_fips_file()
    fips_in_order = []
    for fips in data.keys():
        fips_in_order.append(fips)

    return fips_in_order

def main():

    # print(get_state_names_by_fips_order())
    print(get_fips_in_seq_order())

if __name__ == "__main__":
    main()