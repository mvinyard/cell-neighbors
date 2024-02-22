
# -- import packages: ---------------------------------------------------------
import ABCParse
import numpy as np
import annoy


# -- set typing: --------------------------------------------------------------
from typing import Generator, Optional


# -- operational class: -------------------------------------------------------
class GraphQuery(ABCParse.ABCParse):
    def __init__(self, *args, **kwargs) -> None:
        self.__parse__(locals())

    def forward(self) -> Generator:
        for x_query in self._X_query:
            yield self._idx.get_nns_by_vector(x_query, self._n_neighbors)

    def _format(self, output: Generator) -> np.ndarray:
        return np.array(list(output))

    def __call__(
        self,
        idx: annoy.AnnoyIndex,
        X_query: np.ndarray,
        n_neighbors: int = 20,
        *args,
        **kwargs,
    ) -> np.ndarray:
        """

        Args:
            idx (annoy.AnnoyIndex)

            X_query (np.ndarray)

            n_neighbors (int): Number of neighbors to return. **Default**: 20.

        Returns:
            (np.ndarray)
        """
        self.__update__(locals())

        print(f"X_query shape: {X_query.shape}")

        return self._format(self.forward())


# -- API-facing function: -----------------------------------------------------
def query_graph(idx, X_query: np.ndarray, n_neighbors=20):
    """
    Args:
        idx
        
        X_query (np.ndarray)
        
        n_neighbors (int)
    """
    query = GraphQuery()
    return query(idx=idx, X_query=X_query, n_neighbors=n_neighbors)
