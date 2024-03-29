"""
Purpose of this file to anaylze parsed data from the US Census Bureau API and visualize trends
between poverty and people insured in the United States (more specifcally the states).
"""
import plotly.express as px
import pandas as pd
import numpy as np

from data.insurance_state_data import InsuranceStateData
from data.poverty_state_data import PovertyStateData
from data.states_fips_code_and_name import get_state_names_by_fips_order

INSURED_VS_POP_COLUMN = "uninsured_vs_state_pop"

PERCENT_OF_PPL_IN_POV_COLUMN = "SAEPOVRTALL_PT"
STATE_ABREV_COLUMN = "STABREV"

PROMPT = """
Which analysis would you like to see?
1. Percentage of Uninsured Population by State - 2020
2. Percentage of People in Poverty by State - 2020 
3. Trend between Poverty and Uninsured People by State - 2020 
Enter a number corresponding to the analysis you'd like to see: """

class PovertyInsuranceAnalysis:
    __slots__ = ["insurance_df", "poverty_df", "state_names"]
    def __init__(self):
        self.insurance_df = InsuranceStateData().get_insurance_dataframe() 
        self.poverty_df = PovertyStateData().get_poverty_dataframe() 
        self.state_names = get_state_names_by_fips_order()

    def analyze_insurance_state_data(self):
        """
        Creates a visualization of the percentage of uninsured people per state
        TODO: make numbers look prettier somehow when you hover over the state
        TODO: Polish visuals
        """
        
        # i did hover_data as such since I don't know how else to remove locations from being shown when hovering over a state
        # idk, i just used the dataframe for locations, i used the constant above but there were issues and I couldn't hide it
        # using the dataframe helped avoid this issue, why it happned? idk, it said UNHASHABLE Type and i tried to set the constant
        # to false in the hover_data dict
        fig = px.choropleth(
            # locations, using dataframe column 'state_name' it somehow understands that idk, color highlights the important part
            data_frame=self.insurance_df,
            locations="state_name",locationmode="USA-states", scope="usa",color=INSURED_VS_POP_COLUMN,
            color_continuous_scale="RdBu",
            title="Percentage of Uninsured Population by State - 2020",
            # when i hover i want to emphasize something/ make it bold (hover_name)
            # i want to display certain data when i hover over something (hover_data)
            hover_name=self.state_names, hover_data={'state_name': False,"uninsured_amt": True, "insured_amt": True, "population": True, INSURED_VS_POP_COLUMN: True},
            # rename columns to something more meaningful
            labels={"insured_amt": "Amount Of People Insured", "uninsured_amt": "Amount Of People Uninsured",
                    "population": "Number Of People Used For The Data",
                    INSURED_VS_POP_COLUMN: "Percentage Of State Uninsured",
                    })

        fig.show()

    def analyze_poverty_state_data(self):
        """
        Creates a visualization of the percentage of people in poverty per state
        TODO: make numbers look prettier somehow when you hover over the state
        TODO: Polish visuals
        """
        # df = self.poverty_state_data.parsed_data_per_state()
       
        fig = px.choropleth(
            data_frame=self.poverty_df,locations=STATE_ABREV_COLUMN,locationmode="USA-states",scope="usa",
            color=PERCENT_OF_PPL_IN_POV_COLUMN,
            color_continuous_scale="Viridis",
            hover_name=self.state_names,
            hover_data={STATE_ABREV_COLUMN: False},
            labels={PERCENT_OF_PPL_IN_POV_COLUMN: "Percentage Of State In Poverty"},
            title="Percentage of Poverty Population by State - 2020"
        )

        fig.show()

    def anaylze_poverty_and_uninsured_data(self):
        """
        TODO: Polish visuals
        TODO: To a time series analysis to see if this correlation has been existent for a while
        """

        # plug correlation number in graph somehow
        correlation = np.corrcoef(self.insurance_df[INSURED_VS_POP_COLUMN], self.poverty_df[PERCENT_OF_PPL_IN_POV_COLUMN])

        # indexing the correlation matrix to get the correlation coefficient
        correlation = correlation[0][1]

        # print(correlation)

        # lets combine the dataframes | both are sorted by states so it should be fine
        combined_cols = {INSURED_VS_POP_COLUMN: self.insurance_df[INSURED_VS_POP_COLUMN],
                         PERCENT_OF_PPL_IN_POV_COLUMN: self.poverty_df[PERCENT_OF_PPL_IN_POV_COLUMN],
                         STATE_ABREV_COLUMN: self.poverty_df[STATE_ABREV_COLUMN]}

        insurance_and_poverty_df = pd.DataFrame(combined_cols)

        # print(insurance_and_poverty_df)

        fig = px.scatter(data_frame=insurance_and_poverty_df, x=INSURED_VS_POP_COLUMN, 
                         y=PERCENT_OF_PPL_IN_POV_COLUMN,
                         trendline="ols",title="Correlation Between Poverty and Uninsured People by State - 2020",
                         labels={INSURED_VS_POP_COLUMN: "Percentage Of State Uninsured",
                                 PERCENT_OF_PPL_IN_POV_COLUMN: "Percentage Of State In Poverty"},
                                 trendline_color_override="black")
        
      
        # Add correlation coefficient as text outside the graph
        fig.add_annotation(x=1, y=1.05,  # Position outside the graph
                        xref='paper', yref='paper',
                        text=f'Correlation Coeeficient: {correlation:.2f}',
                        showarrow=False)

        fig.show()

def main():
    """
    Prompts user as to which visualization they would like to see.
    """
    user_selection = int(input(PROMPT))
    analysis = PovertyInsuranceAnalysis()

    # percentage of uninsured people per state
    if user_selection == 1:
        analysis.analyze_insurance_state_data()

    # percentage of people in poverty per state
    elif user_selection == 2:
        analysis.analyze_poverty_state_data()

    # combine results to draw a correlation
    elif user_selection == 3:
        analysis.anaylze_poverty_and_uninsured_data()

if __name__ == "__main__":
    main()
