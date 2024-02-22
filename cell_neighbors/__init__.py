# __init__.py

import logging
import py_pkg_logging as ppl

log_config = ppl.LogConfig(log_file="cell_neighbors.log")

logger = logging.getLogger(f'cell_neighbors.{__name__}')
logger.info(f"Logs for cell_neighbors will be saved to: {log_config.log_fpath}")
logger.debug(f"Importing from local install location: {__file__}")

from ._kNN import kNN

from ._graph_query import GraphQuery, query_graph
from ._neighbor_attribute_map import NeighborAttributeMap, map_neighbor_attributes
from ._neighbor_attribute_counter import NeighborAttributeCounter, count_neighbor_attributes