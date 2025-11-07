import pandas as pd
from pandas_datareader import wb

class WorldBankDataset:
    """
    Handles downloading and preparing data from the World Bank API.
    """

    def __init__(self, country, indicator):
        """
        Initializes the WorldBankDataset class.

        Parameters
        ----------
        country : str
            Country code (e.g., 'WLD' for World Bank data).
        indicator : str
            Indicator code (e.g., 'EN.ATM.CO2E.PC' for CO2 emissions per capita).

        Returns
        -------
        WorldBankDataset
            An instance of the WorldBankDataset class.

        Notes
        -----
        Country and indicator codes can be found on the World Bank API documentation.
        """
        self.country = country
        self.indicator = indicator

    def load_data(self):
        
        """
        Downloads and prepares data from the World Bank API.

        Returns a pandas DataFrame with the following columns:
        - date (int): year of observation
        - value (float): value of the indicator for the given year

        If the API call fails or no data is available, returns an empty DataFrame.
        """
        
        try:
            data = wb.download(
                indicator=self.indicator,
                country=self.country,
                start=1960,
                end=2025
            )
            if data.empty:
                return pd.DataFrame()  # gracefully return empty

            data = data.reset_index()
            if self.indicator not in data.columns:
                return pd.DataFrame()

            data = data.rename(columns={'year': 'date', self.indicator: 'value'})
            data['date'] = pd.to_numeric(data['date'], errors='coerce')
            data = data.dropna(subset=['value'])
            return data

        except Exception:
            return pd.DataFrame()