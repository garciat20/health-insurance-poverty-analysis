"""
Purpose of this file is to parse specific data about health insurance coverage per state from the US Census Bureau API. -2020
"""

import requests
import pandas as pd
from config.api_config import HEALTH_INSURANCE_URL, HEALTH_INSURANCE_PARAMAS

STATE_ABBREVIATION = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

UNINSURED_AMT_OF_PPL = "uninsured_amt"
INSURED_AMT_OF_PPL = "insured_amt"
POP_FROM_STATE = "population"

class InsuranceStateData:
    __slots__ = ["data"]

    def __init__(self):
        response = requests.get(HEALTH_INSURANCE_URL, params=HEALTH_INSURANCE_PARAMAS)
        self.data = response.json() # data returned from the API
        
    def parsed_data_per_state(self):
        """
        Returns a dictionary containing every state code as the key and the values are the population used in the data collected along with uninsured/ insured people
        """

        states_data = {} # store's data corresponding to a state's code

        # dummy values given, will be updated when going through data
        state_code = -1
        county_code = -1

        # data columns returned from the API: if more paramters are given, these columns will change
        state_col = 4
        county_col = 5
        insured_col = 0
        uninsured_col = 1

        # skip header
        for row in self.data[1:]:

            # firstly, we want to avoid dealing with null values so we'll skip that row
            if (self.is_valid_data(row[insured_col], row[uninsured_col]) == False):
                continue

            # if current statecode doesn't match previous one, that means we hit a new state because our data is organized in ascending order
            # the data returned from the API is all in strings, we have to convert to int
            curr_state_code = int(row[state_col])
            curr_county_code = int(row[county_col])
            if (curr_state_code != state_code):
                state_code = curr_state_code
                county_code = curr_state_code

                # create a nested dict for a state that contains many values! the state code will be the key
                states_data[state_code] = {INSURED_AMT_OF_PPL: 0, UNINSURED_AMT_OF_PPL: 0, POP_FROM_STATE: 0}

            # check the state code and county code of new row matches criteria to add up a state's population
            if (curr_state_code == state_code and curr_county_code != county_code):
                # county col shouldn't match county code so no duplicates in population addition

                # get nested dict from state code:
                pop_val_dict = states_data[state_code] # nested dict

                # add the population of the uninsured/ insured people of different counties of the same state
                insured_pop = int(row[insured_col])
                uninsured_pop = int(row[uninsured_col])

                # loop thru nested dict
                for key, val in pop_val_dict.items():
                    if key == UNINSURED_AMT_OF_PPL:
                        pop_val_dict[key] = val + uninsured_pop  #update uninsured pop accordingly
                    if key == INSURED_AMT_OF_PPL:
                        pop_val_dict[key] = val + insured_pop   #update insured pop accordingly
                    if key == POP_FROM_STATE:
                        pop_val_dict[key] = val + insured_pop + uninsured_pop

        return states_data

    
    def is_valid_data(self, insured_pop, uninsured_pop):
        """
        If there's a piece of data that is 'null' we will avoid that row.
        """
        if (insured_pop == None or uninsured_pop == None):
            return False
        return True
    
    def get_population_of_us(self):
        """
        Returns the population of the United States used in this data (in 2020)
        """
        total_population = 0
        states_data = self.parsed_data_per_state()
        for state_code, nested_dict in states_data.items():
            # pop the nested dictionary
            population_dict = nested_dict
            for key, value in population_dict.items():
                if key == POP_FROM_STATE:
                    total_population += value # if the key is population, get the value and update total pop
    
        return total_population
    
    def proportion_of_uninsured_to_state_pop(self):
        """
        Calculates the amount of uninsured people against the state population
        returns a dict with key of fip code and value that's a percentage (out of 100, 100 == all uninsured and vice versa)
        """
        state_data = self.parsed_data_per_state()
        nested_dict = state_data.values()

        'STORE PRECENTAGE IN NEW DICT BY CODE OR STATENAME THO? -- most likely list bc its all ordered lol'
        result = []
        # state_data contained the states in ascending order via their state fips code
        for state_proportion in nested_dict:
            uninsured_people = state_proportion[UNINSURED_AMT_OF_PPL] 
            pop_in_state = state_proportion[POP_FROM_STATE]
            "formula will be (uninsured/pop) * 100"
            percentage = (uninsured_people/pop_in_state) * 100
            result.append(percentage)
      
        return result
    
    def get_insurance_dataframe(self):
        """
        Format the data we gathered into a dataframe to utilize in our plotly visualizations
        """
         # using helper function to get fips codes per state and converting to list
        states_data = self.parsed_data_per_state()
        states_fips_code = [f'{fips:02}' for fips in states_data.keys()] # list of string of fips codes

        # lets get nested dict that contains amt_insured, amt_uninsured, pop_per_state
        pop_nested_dict = states_data.values()

        # everything is organized in order by FIPS code so it makes it easier, i can just enter the data raw

        proportional_uninsured_results = self.proportion_of_uninsured_to_state_pop()

        df = pd.DataFrame(pop_nested_dict)
        # add column to datafram
        df.insert(0, "fips", states_fips_code)
        df.insert(1, "state_name", STATE_ABBREVIATION)
        df.insert(2, "uninsured_vs_state_pop", proportional_uninsured_results)
        # columns are fips, state_name, uninsured..., insured_amt, uninsured_amt, population --> maybe missing one? somehow check later

        return df
        
def main():
    insurance_data = InsuranceStateData()
    print(insurance_data.parsed_data_per_state())
    # print("Total population:", insurance_data.get_population_of_us())
    # print(insurance_data.proportion_of_uninsured_to_state_pop())
    
if __name__ == "__main__":
    main()
