
# -- import packages: ---------------------------------------------------------
import ABCParse
import anndata
import adata_query
import annoy
import numpy as np


# -- set up logger: -----------------------------------------------------------
import py_pkg_logging
import logging

logger = logging.getLogger(__name__)


# -- set typing: --------------------------------------------------------------
from typing import Optional


# -- import local dependencies: -----------------------------------------------
from ._neighbor_query import NeighborQuery


# -- operational class: -------------------------------------------------------
class kNN(ABCParse.ABCParse):
    """Container for kNN graph using annoy.AnnoyIndex.

    Attributes:
        _knn_idx_built (bool): Indicates whether the kNN index has been built.

        adata (anndata.AnnData): An AnnData object containing data.

        _use_key (str): The key specifying the data to use for building the kNN graph.

        _n_trees (int): The number of trees to build the Annoy index.

        _distance_metric (str): The distance metric used for building the Annoy index.

    Methods:
        query(X_query: np.ndarray, obs_key: Optional[str] = None, label_only: bool = True):
            Query the kNN graph for neighbors of a given set of query points.
    """
    @py_pkg_logging.log_function_call(logger)
    def __init__(
        self,
        adata: anndata.AnnData,
        use_key: str = "X_pca",
        n_trees: int = 10,
        distance_metric: str = "euclidean",
        *args,
        **kwargs,
    ) -> None:
        """Initializes the kNN instance.
        

        Args:
            adata (anndata.AnnData): An AnnData object containing data.

            use_key (str): The key specifying the data to use for building the kNN graph.
            
            n_trees (int): The number of trees to build the Annoy index.
            
            distance_metric (str): The distance metric used for building the Annoy index.
            
            *args: Additional positional arguments.
            
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        self._knn_idx_built = False
        self.__parse__(locals(), public=["adata"])
        self._build_index()

    @property
    def X_use(self) -> np.ndarray:
        """Property to access the data used for building the kNN graph.

        Returns:
            np.ndarray: The data used for building the kNN graph.
        """
        if not hasattr(self, "_X_use"):
            self._X_use = adata_query.fetch(
                self.adata, key=self._use_key, groupby=None, torch=False
            )
        return self._X_use

    @property
    def _n_obs(self) -> int:
        """Property to access the number of observations.

        Returns:
            int: The number of observations.
        """
        return self.X_use.shape[0]

    @property
    def _n_dim(self) -> int:
        """Property to access the number of dimensions.

        Returns:
            int: The number of dimensions.
        """
        return self.X_use.shape[1]
    
    @py_pkg_logging.log_function_call(logger)
    def _build_index(self) -> annoy.AnnoyIndex:
        """Build the Annoy index for the kNN graph.

        Returns:
            annoy.AnnoyIndex: The Annoy index built for the kNN graph.
        """
        idx = annoy.AnnoyIndex(self._n_dim, self._distance_metric)
        [idx.add_item(i, self.X_use[i]) for i in range(self._n_obs)]
        idx.build(self._n_trees)
        self._idx = idx
        self._knn_idx_built = True

    @property
    def idx(self) -> annoy.AnnoyIndex:
        """Property to access the Annoy index.

        Returns:
            annoy.AnnoyIndex: The Annoy index for the kNN graph.
        """
        if not hasattr(self, "_idx"):
            self._build_index()
        return self._idx

    @property
    def _query_cls(self):
        """Property to access the NeighborQuery class.

        Returns:
            NeighborQuery: The NeighborQuery class for querying neighbors in the kNN graph.
        """
        if not hasattr(self, "_neighbor_query_cls"):
            self._neighbor_query_cls = NeighborQuery(self.idx, self.adata, self._n_dim)
        return self._neighbor_query_cls

    @py_pkg_logging.log_function_call(logger)
    def query(self, X_query: np.ndarray, obs_key: Optional[str] = None, label_only: bool = True):
        """Query the kNN graph for neighbors of a given set of query points.

        Args:

            X_query (np.ndarray): The query points for which neighbors are to be found.

            obs_key (Optional[str]): The key for accessing observation attributes. **Default**: ``None``.
            
            label_only (bool): Flag indicating whether to return only labels of the neighbors. **Default**: ``True``.

        Returns:
            (NeighborQuery): The NeighborQuery instance containing information about neighbors.
        """
        return self._query_cls(X_query, obs_key=obs_key, label_only=label_only)

    def __repr__(self) -> str:
        """
        Returns a string representation of the kNN instance.

        Returns:
            str: String representation of the kNN instance.
        """
        attrs = {
            "built": self._knn_idx_built,
            "n_obs": self._n_obs,
            "n_dim": self._n_dim,
        }
        repr_str = "k-nearest neighbor graph\n"
        for key, val in attrs.items():
            repr_str += f"\n  {key}: {val}"
        return repr_str
