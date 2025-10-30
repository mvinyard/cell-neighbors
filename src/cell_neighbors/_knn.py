# -- import packages: ---------------------------------------------------------
import adata_query
import anndata
import logging
import numpy as np
import voyager

# -- set type hints: ----------------------------------------------------------
from typing import Optional

# -- configure logger: --------------------------------------------------------
logger = logging.getLogger(__name__)


# -- operational class: -------------------------------------------------------
class kNN:
    
    _KNN_IDX_BUILT: bool = False

    def __init__(
        self,
        adata: anndata.AnnData,
        use_key: str = "X_pca",
        space: voyager.Space = voyager.Space.Euclidean,
    ):

        self.adata = adata
        self.use_key = use_key
        self.space = space

        self._build()

    @property
    def X(self) -> np.ndarray:
        return adata_query.fetch(self.adata, self.use_key)

    @property
    def n_dim(self) -> int:
        return self.X.shape[1]

    @property
    def index(self) -> voyager.Index:
        if not hasattr(self, "_index"):
            self._index = voyager.Index(space=self.space, num_dimensions=self.n_dim)
        return self._index

    def _build(self):
        self._build_indices = [self.index.add_item(x_cell) for x_cell in self.X]
        self._KNN_IDX_BUILT = True
        logger.info(f"Built kNN index with {len(self._build_indices)} items")

    @property
    def n_obs(self) -> int:
        return len(self._build_indices)

    def __repr__(self) -> str:

        """
        Returns:
            representation (str): String representation of the kNN instance.
        """
        attrs = {
            "built": self._KNN_IDX_BUILT,
            "n_obs": self.n_obs,
            "n_dim": self.n_dim,
        }
        repr_str = "k-nearest neighbor graph\n"
        for key, val in attrs.items():
            repr_str += f"\n  {key}: {val}"
        return repr_str
