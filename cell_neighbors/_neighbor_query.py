
# -- import packages: ---------------------------------------------------------
import ABCParse
import anndata
import pandas as pd
import numpy as np


# -- import local dependencies: -----------------------------------------------
from ._graph_query import query_graph
from ._neighbor_attribute_map import map_neighbor_attributes
from ._neighbor_attribute_counter import NeighborAttributeCounter

# -- set up logger: -----------------------------------------------------------
import py_pkg_logging
import logging

logger = logging.getLogger(__name__)


# -- set typing: --------------------------------------------------------------
from typing import Optional


# -- operational class: -------------------------------------------------------
class NeighborQuery(ABCParse.ABCParse):
    """
    Higher-level class that operates below the kNN class but above all other
    related classes. It is used for querying nearest neighbors and processing
    attributes related to these neighbors.

    Attributes:
        idx (annoy.AnnoyIndex): Annoy index for nearest neighbor queries.
        
        adata (anndata.AnnData): Annotated data matrix.
        
        n_dim (int): Number of dimensions.
    """
    @py_pkg_logging.log_function_call(logger)
    def __init__(self, idx, adata: anndata.AnnData, n_dim: int, *args, **kwargs):
        """Initializes the NeighborQuery object with the provided Annoy index,
        annotated data, and dimensions.

        Args:
            idx (annoy.AnnoyIndex): Annoy index for nearest neighbor queries.
            
            adata (anndata.AnnData): Annotated single-cell data matrix.
            
            n_dim (int): Number of dimensions.
            
        Returns:
            None
        """
        self.__parse__(locals())

    @property
    def _IS_MULTI_QUERY(self) -> bool:
        """Determines if the current query is a multi-query based on the shape
        of the query.

        Returns:
            (bool): True if it's a multi-query, False otherwise.
        """
        return len(self.query_shape) > 2 and self.query_shape[-1] == self._n_dim

    @property
    def mapped_nn(self) -> np.ndarray:
        """
        Queries the graph and returns the mapped nearest neighbors.

        Returns:
            (np.ndarray): The mapped nearest neighbors.
        """
        return query_graph(self._idx, self._X_query)

    @property
    def attr_df(self) -> pd.DataFrame:
        """
        Maps attributes to the nearest neighbors. Raises an exception if 'obs_key' is not set.

        Returns:
            (pd.DataFrame): Attributes mapped to nearest neighbors.
        
        Raises:
            Exception: If 'obs_key' is not passed during `NeighborQuery.__call__`.
        """
        if not hasattr(self, "_obs_key"):
            raise Exception(
                "To map attributes to neighbors, pass `obs_key` during `NeighborQuery.__call__`"
            )
        return map_neighbor_attributes(self._adata, self.mapped_nn, self._obs_key)

    @property
    def attribute_counter(self):
        """Provides an instance of NeighborAttributeCounter for the current
        attributes DataFrame.

        Returns:
            (NeighborAttributeCounter): The counter object for neighbor attributes.
        """
        if not hasattr(self, "_attribute_counter"):
            self._attribute_counter = NeighborAttributeCounter(self.attr_df)
        return self._attribute_counter

    @property
    def count_df(self):
        """Provides a DataFrame with counts of neighbor attributes.

        Returns:
            DataFrame: Count of neighbor attributes.
        """
        return self.attribute_counter.count_df

    @property
    def labels(self):
        """Provides labels for the attributes. If it's a multi-query, the
        labels are reshaped accordingly.

        Returns:
            (pd.DataFrame): Labels for the attributes.
        """
        if self._IS_MULTI_QUERY:
            return pd.DataFrame(
                self.attribute_counter.labels.values.reshape(-1, self._X_query.shape[0])
            )
        return self.attribute_counter.labels
    
    @py_pkg_logging.log_function_call(logger)
    def _sub_call(self):
        """Internal method to handle sub-calls based on the presenceof 'obs_key' and
        'label_only' flags.

        Returns:
            Various: Depending on the flags, it returns labels, count DataFrame, or
            mapped nearest neighbors.
        """
        if self._obs_key and self._label_only:
            return self.labels
        if self._obs_key:
            return self.count_df
        return self.mapped_nn
    
    @py_pkg_logging.log_function_call(logger)
    def __call__(
        self, X_query, obs_key: Optional[str] = None, label_only=True, *args, **kwargs
    ):
        """
        Calls the NeighborQuery with the given query matrix and optional observation
        key and label flag. Updates the internal state based on the query and processes
        the query accordingly.

        Args:
            X_query (np.ndarray): Query matrix for nearest neighbor search.
            obs_key (Optional[str]): Key to observation attributes in the annotated data
            matrix. Default is None. label_only (bool): Flag to indicate whether only labels
            should be returned. Default is True.

        Returns:
            Various: Depending on the query and flags, it returns labels, count DataFrame, or
            mapped nearest neighbors.
        """
        self.__update__(locals())
        
        if hasattr(self, "_attribute_counter"):
            del self._attribute_counter

        self._obs_key = obs_key
        self.query_shape = self._X_query.shape

        if self._IS_MULTI_QUERY:
            self._X_query = self._X_query.reshape(-1, self._n_dim)
            print(f"Multi-query, new shape: {self._X_query.shape}")
            if self._obs_key and self._label_only:
                return pd.DataFrame(
                    self._sub_call().values.reshape(-1, self.query_shape[0])
                )
            if not self._obs_key:
                return self._sub_call().reshape(
                    self.query_shape[0], self.query_shape[1], -1
                )

        return self._sub_call()
