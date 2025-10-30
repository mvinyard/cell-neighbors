
import ABCParse
import anndata
import pandas as pd
import numpy as np


class NeighborAttributeMap(ABCParse.ABCParse):
    """
    A class for mapping neighbor attributes in an AnnData object.

    Attributes:
        _adata (anndata.AnnData): An AnnData object containing data.
        _obs_key (str): The key for accessing observation attributes.
        _mapped_nn (np.ndarray): An array containing mapped neighbor indices.

    Methods:
        __call__(mapped_nn: np.ndarray, obs_key: str, *args, **kwargs): Calls the instance and returns the query DataFrame.
    """
    def __init__(self, adata: anndata.AnnData, *args, **kwargs):
        """Initializes the NeighborAttributeMap instance.

        Args:
            adata (anndata.AnnData): An AnnData object containing data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.__parse__(locals())

    @property
    def nn(self) -> np.ndarray:
        """Property to access flattened mapped neighbor indices.

        Returns:
            np.ndarray: Flattened array of mapped neighbor indices.
        """
        return self._mapped_nn.flatten()

    @property
    def n_neighbors(self) -> int:
        """
        Property to access the number of neighbors.

        Returns:
            int: Number of neighbors.
        """
        return self._mapped_nn.shape[-1]

    @property
    def _nn_adata(self) -> anndata.AnnData:
        """Property to access the AnnData object with mapped neighbor indices.

        Returns:
            anndata.AnnData: AnnData object containing mapped neighbor data.
        """
        return self._adata[self.nn]

    @property
    def query_df(self) -> pd.DataFrame:
        """Property to generate the query DataFrame.

        Returns:
            pd.DataFrame: DataFrame with neighbor observation attributes.
        """
        return pd.DataFrame(
            self._nn_adata.obs[self._obs_key].to_numpy().reshape(-1, self.n_neighbors)
        ).T

    def __call__(self, mapped_nn: np.ndarray, obs_key, *args, **kwargs):
        """Calls the instance and returns the query DataFrame.

        Args:
            mapped_nn (np.ndarray): An array containing mapped neighbor indices.
            obs_key (str): The key for accessing observation attributes.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            pd.DataFrame: DataFrame with neighbor observation attributes.
        """
        self.__update__(locals())
        return self.query_df
    
    
def map_neighbor_attributes(adata, mapped_nn, obs_key) -> pd.DataFrame:
    """Map neighbor attributes in the provided AnnData object.

    Args:
        adata (anndata.AnnData): An AnnData object containing data.
        mapped_nn (np.ndarray): An array containing mapped neighbor indices.
        obs_key (str): The key for accessing observation attributes.

    Returns:
        pd.DataFrame: DataFrame with neighbor observation attributes.
    """
    neighbor_attrs = NeighborAttributeMap(adata=adata)
    return neighbor_attrs(mapped_nn=mapped_nn, obs_key=obs_key)
