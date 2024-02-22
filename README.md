# cell-neighbors

Neighbor graphs for single-cell data (AnnData)

This repository provides a Python package for building k-nearest neighbor (kNN) graphs from AnnData objects.
The package is built on the `Annoy` library from Spotify.

## Features
- Efficient kNN Graph Construction from `Annoy`.
- Direct `AnnData` integration
- Flexible querying of neighbors in the constructed `kNN` graph index.


## Installation

You can install the package using pip:
```
pip install cell-neighbors
```

## Example
```python
import cell_neighbors

# Initialize kNN graph builder
knn_graph = cell_neighbors.kNN(adata), use_key="X_pca")

# Query neighbors
X_query = [...]  # Your query points as numpy array
neighbors = knn_graph.query(X_query)
```

## Documentation

For real examples, detailed usage instructions, and API reference, please refer to the documentation.