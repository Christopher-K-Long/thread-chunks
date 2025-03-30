from typing import Any, Callable, List, Optional

from ray.types import ObjectRef
from tqdm import tqdm as tqdm

from . import config

class Chunker():
    """A collection of
    ``RemoteLabelledActor`` s pre-loaded with a function to execute that can be
    reused. Unlike :func:`chunk` this means that the function to parallelise
    only needs to be copied when the function is first executed in parallel and
    does not need to be copied to the ``RemoteLabelledActor`` s every time.

    Notes
    -----
    If ``ray`` is not initialised when :class:`Chunker` is initialised then
    :class:`Chunker` will initialise ``ray``. In this case when :class:`Chunker`
    is deleted it will ``shutdown`` ``ray`` unless the attribute
    :attr:`persistent` is set to ``True``.
    """
    actors: List[ObjectRef]
    """The ``RemoteLabelledActor`` s the :class:`Chunker` will use to execute
    tasks."""
    progress_bar: bool
    "Whether to display a progress bar in the terminal."
    persistent: bool
    """Whether to allow the ``ray`` instance (if created by this
    :class:`Chunker`) to persist after this :class:`Chunker` is deleted."""
    path: Optional[str]
    "The path of the checkpointing file associated with this :class:`Chunker`."
    def __init__(self,
                 func: Optional[Callable] = None,
                 actors: Optional[List[ObjectRef]] = None,
                 chunk_size: int = config.default_chunk_size,
                 progress_bar: bool = config.progress_bar,
                 persistent: bool = False,
                 path: Optional[str] = None):
        """Initialises a :class:`Chunker`.

        Parameters
        ----------
        func : Callable, optional
            The function to be executed in parallel. Note `func` and `actors`
            cannot be passed together. By default ``None``.
        actors : List[ObjectRef], optional
            A list of remote ``RemoteLabelledActor`` s. If actors is ``None``
            then `func` will be used to generate a set of `chunk_size`
            ``RemoteLabelledActor`` s. Note `func` and `actors` cannot be passed
            together. By default ``None``.
        chunk_size : int
            The number of threads to launch simultaneously (a chunk). By default
            ``config.default_chunk_size``.
        progress_bar : bool
            Whether to display a progress bar in the terminal. By default
            ``config.progress_bar``.
        persistent : bool
            Whether to allow the ray instance (if created by this
            :class:`Chunker`) to persist after this :class:`Chunker` is deleted.
            By default ``False``.
        path : str, optional
            The path of the checkpointing file associated with this
            :class:`Chunker`. By default ``None``.

        Raises
        ------
        ValueError
            "Either `func` or `actors` must be specified but not both."
        ValueError
            "`chunk_size` does not agree with the number of `actors`. Note that
            ``len(actors)`` must equal `chunk_size`."
        """
        ...
    @property
    def chunk_size(self) -> int:
        "The number of threads to launch simultaneously (a chunk)."
        ...
    def __call__(self,
                 parameters: List[List[Any]],
                 func: Optional[Callable] = None,
                 progress_bar: Optional[bool] = None,
                 path: Optional[str] = None
                ) -> List[Any]:
        """The functions stored in each
        ``RemoteLabelledActor`` in
        :attr:`actors` is called in parallel, a chunk at a time, for each set of
        ``*args`` in `parameters` and returns the outputs in an ordered
        ``list``. As only `chunk_size` threads are running `func` at any given
        time memory intensive operations will not exhaust the RAM capacity.

        Alternatively, `func` can be passed to override the functions stored in
        each ``RemoteLabelledActor`` of :attr:`actors`.

        Parameters
        ----------
        parameters : List[List[Any]]
            A list of ``*args`` to pass to the function to be executed in
            parallel.
        func : Callable, optional
            The function to be executed in parallel. If ``None`` then the
            function stored in each ``RemoteLabelledActor`` in :attr:`actors` is
            used. Else the functions stored in the :attr:`actors` are replaced
            with `func`. By default ``None``.
        progress_bar : bool, optional
            Whether to display a progress bar in the terminal. If ``None`` is
            passed then :attr:`progress_bar` is used. By default ``None``.
        path : str, optional
            The path to save the checkpoints to. By default ``None``.

        Returns
        -------
        List[Any]
            A List of the outputs of `func`. The ``i`` th element corresponds to
            the ``i`` th element of parameters [``func(*parameters[i])``].

        Warns
        -----
        CheckpointFailedWarning
            The checkpointing file has no saved argument values. Proceeding and
            continuing to save data, but you will not be able to pick up from
            this checkpoint.
        CheckpointFailedWarning
            There was an error while saving the data.
        """
        ...
    def __del__(self):
        """Shuts down ``ray`` if ``ray`` was initialised by this instance of
        :class:`Chunker` and ``persistent==False``.
        """
        ...

def chunk(func: Optional[Callable],
          parameters: List[List[Any]],
          actors: Optional[List[ObjectRef]] = None,
          chunk_size: int = config.default_chunk_size,
          progress_bar: bool = config.progress_bar,
          path: Optional[str] = None
         ) -> List[Any]:
    """Calls `func` in parallel, a chunk at a time, for each set of ``*args`` in
    `parameters` and returns the outputs in an ordered ``list``. As only
    `chunk_size` threads are running `func` at any given time memory intensive
    operations will not exhaust the RAM capacity.

    Alternatively, `actors` can be passed a list of ``RemoteLabelledActor`` if
    `func` is passed ``None`` and the functions stored in each
    ``RemoteLabelledActor`` will be used.

    Parameters
    ----------
    func : Optional[Callable]
        The function to parallelize. If ``None`` then the function saved in the
        `actors` is used.
    parameters : List[List[Any]]
        A list of ``*args`` to be passed to `func`.
    actors: Optional[List[ObjectRef]]
        A list of ray actors of type ``RemoteLabelledActor`` to use for the
        computation. By default ``None``.
    chunk_size : int, optional
        The number of threads to launch simultaneously (a chunk). By default
        ``config.default_chunk_size``.
    progress_bar : bool, optional
        Whether to display a progress bar in the terminal. By default
        ``config.progress_bar``.
    path : str, optional
        If specified then after each new data point a checkpoint is saved to the
        `path`. If the checkpoint file exists when :func:`chunk` is called then
        :func:`chunk` will pick up from the checkpoint.

    Returns
    -------
    List[Any]
        A List of the outputs of `func`. The ith element corresponds to the ith
        element of parameters [``func(*parameters[i])``].

    Raises
    ------
    ValueError
        "`func` and `actors` cannot both be ``None``."
    ValueError
        "`chunk_size` does not agree with the number of `actors`. Note that
        ``len(actors)`` must equal `chunk_size`."
        
    Warns
    -----
    CheckpointFailedWarning
        The checkpointing file has no saved argument values. Proceeding and
        continuing to save data, but you will not be able to pick up from this
        checkpoint.
    CheckpointFailedWarning
        There was an error while saving the data.
    """
    ...