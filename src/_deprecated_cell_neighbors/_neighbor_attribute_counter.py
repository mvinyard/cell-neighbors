
# -- import packages: ---
import ABCParse
import pandas as pd


# -- set typing: ----
from typing import Generator, Tuple

class NeighborAttributeCounter(ABCParse.ABCParse):
    """
    A class for counting neighbor attributes in a pd.DataFrame.

    Attributes:
        _attr_df (pd.DataFrame): The DataFrame containing attribute data.

    Methods:
        count(df): Counts the occurrences of each attribute value in the DataFrame.
        count_df (property): Property to access the DataFrame with attribute counts.
        labels (property): Property to retrieve the labels of the most frequent attributes.
    """
    
    def __init__(self, attr_df: pd.DataFrame, *args, **kwargs):
        """
        Initializes the NeighborAttributeCounter instance.

        Args:
            attr_df (pd.DataFrame): The DataFrame containing attribute data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.__parse__(locals())

    def count(self, df: pd.DataFrame) -> Generator:
        """
        Counts the occurrences of each attribute value in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame for which attribute counts are to be calculated.

        Yields:
            dict: A dictionary containing attribute values as keys and their counts as values.
        """
        for col in df:
            yield df[col].value_counts().to_dict()

    @property
    def count_df(self):
        """Property to access the DataFrame with attribute counts.

        Returns:
            count_df (pd.DataFrame): DataFrame containing counts of attribute values.
        """
        if not hasattr(self, "_count_df"):
            self._count_df = pd.DataFrame(list(self.count(self._attr_df))).fillna(0)
        return self._count_df

    @property
    def labels(self) -> pd.Series:
        """Property to retrieve the labels of the most frequent attributes.

        Returns:
            labels (pd.Series): Series containing labels of the most frequent attributes.
        """
        return self.count_df.idxmax(1)
        
        
def count_neighbor_attributes(attr_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Count neighbor attributes in the provided DataFrame.

    Args:
        attr_df (pd.DataFrame): The DataFrame containing attribute data.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: DataFrame with attribute counts.
            - pd.Series: Series containing labels of the most frequent attributes.
    """
    attr_counter = NeighborAttributeCounter(attr_df=attr_df)
    return attr_counter.count_df, attr_counter.labels