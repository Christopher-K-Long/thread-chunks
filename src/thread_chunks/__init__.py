"""A python package for performing memory intensive computations in parallel
using chunks and checkpointing."""

from . import config
from ._chunker import Chunker, chunk
from ._checkpoint import Checkpoint, CheckpointFailedWarning
from ._actor import LabelledActor
from ._remote_actor import RemoteLabelledActor