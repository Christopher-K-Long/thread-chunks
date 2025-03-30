import signal
from warnings import warn
from typing import Any, Callable, List, Optional

import ray
from ray.types import ObjectRef
from tqdm import tqdm as tqdm

from . import config
from ._remote_actor import RemoteLabelledActor
from ._checkpoint import Checkpoint, CheckpointFailedWarning

class Chunker():
    """A collection of
    :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` s
    pre-loaded with a function to execute that can be reused. Unlike
    :func:`chunk` this means that the function to parallelise only needs to be
    copied when the function is first executed in parallel and does not need to
    be copied to the
    :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` s every time.

    Notes
    -----
    If ``ray`` is not initialised when :class:`Chunker` is initialised then
    :class:`Chunker` will initialise ``ray``. In this case when :class:`Chunker`
    is deleted it will ``shutdown`` ``ray`` unless the attribute
    :attr:`persistent` is set to ``True``.
    """
    actors: List[ObjectRef]
    """The :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` s the
    :class:`Chunker` will use to execute tasks."""
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
            A list of remote
            :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` s.
            If actors is ``None`` then `func` will be used to generate a set of
            `chunk_size`
            :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` s.
            Note `func` and `actors` cannot be passed together. By default
            ``None``.
        chunk_size : int
            The number of threads to launch simultaneously (a chunk). By default
            :attr:`config.default_chunk_size <thread_chunks.config.default_chunk_size>`.
        progress_bar : bool
            Whether to display a progress bar in the terminal. By default
            :attr:`config.progress_bar <thread_chunks.config.progress_bar>`.
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
        self._ray_initialized_by_this_chunker: bool = ray.is_initialized()
        if (func is None) == (actors is None):
            raise ValueError("Either `func` or `actors` must be specified but not both.")
        self.actors = actors if actors is not None else [RemoteLabelledActor.remote(func) for _ in range(chunk_size)]
        if len(self.actors) != chunk_size:
            raise ValueError("`chunk_size` does not agree with the number of `actors`. Note that ``len(actors)`` must equal `chunk_size`.")
        self.progress_bar = progress_bar
        self.persistent = persistent
        self.path = path
        if not self._ray_initialized_by_this_chunker:
            ray.init(**config.ray_config, ignore_reinit_error=True)
    @property
    def chunk_size(self) -> int:
        "The number of threads to launch simultaneously (a chunk)."
        return len(self.actors)
    def __call__(self,
                 parameters: List[List[Any]],
                 func: Optional[Callable] = None,
                 progress_bar: Optional[bool] = None,
                 path: Optional[str] = None
                ) -> List[Any]:
        """The functions stored in each
        :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` in
        :attr:`actors` is called in parallel, a chunk at a time, for each set of
        ``*args`` in `parameters` and returns the outputs in an ordered
        ``list``. As only `chunk_size` threads are running `func` at any given
        time memory intensive operations will not exhaust the RAM capacity.

        Alternatively, `func` can be passed to override the functions stored in
        each :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` of
        :attr:`actors`.

        Parameters
        ----------
        parameters : List[List[Any]]
            A list of ``*args`` to pass to the function to be executed in
            parallel.
        func : Callable, optional
            The function to be executed in parallel. If ``None`` then the
            function stored in each
            :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>`
            in :attr:`actors` is used. Else the functions stored in the
            :attr:`actors` are replaced with `func`. By default ``None``.
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
        if progress_bar is None:
            progress_bar = self.progress_bar
        if path is None:
            path = self.path
        return chunk(func,
                     parameters,
                     self.actors,
                     self.chunk_size,
                     progress_bar,
                     path)
    def __del__(self):
        """Shuts down ``ray`` if ``ray`` was initialised by this instance of
        :class:`Chunker` and ``persistent==False``.
        """
        if (hasattr(self, "_ray_initialized_by_this_chunker")
            and not self._ray_initialized_by_this_chunker
            and not self.persistent):
            ray.shutdown()

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

    Alternatively, `actors` can be passed a list of
    :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` if `func` is passed
    ``None`` and the functions stored in each
    :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` will be used.

    Parameters
    ----------
    func : Optional[Callable]
        The function to parallelize. If ``None`` then the function saved in the
        `actors` is used.
    parameters : List[List[Any]]
        A list of ``*args`` to be passed to `func`.
    actors: Optional[List[ObjectRef]]
        A list of ray actors of type
        :class:`RemoteLabelledActor <thread_chunks.RemoteLabelledActor>` to use for the
        computation. By default ``None``.
    chunk_size : int, optional
        The number of threads to launch simultaneously (a chunk). By default
        :attr:`config.default_chunk_size <thread_chunks.config.default_chunk_size>`.
    progress_bar : bool, optional
        Whether to display a progress bar in the terminal. By default
        :attr:`config.progress_bar <thread_chunks.config.progress_bar>`.
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
    if actors is not None and len(actors) != chunk_size:
        raise ValueError("`chunk_size` does not agree with the number of `actors`. Note that ``len(actors)`` must equal `chunk_size`.")
    # Initialising ray if it has not yet been initialised.
    ray_initialized: bool = ray.is_initialized()
    if not ray_initialized:
        ray.init(**config.ray_config)
    try:
        updated_threads = None
        if func is not None:
            func_name = func.__name__
            # Copying the `func` to the `actors`
            func_ref = ray.put(func)
            if actors is None:
                # Creating the `actors`
                actors = [RemoteLabelledActor.remote(func_ref)
                          for _ in range(chunk_size)]
            else:
                # Updating the functions stored by the actors.
                updated_threads = [a.set_func.remote(func_ref) for a in actors]
        else:
            if actors is None:
                ValueError("`func` and `actors` cannot both be ``None``.")
            else:
                func_name = ray.get(actors[0].get_func.remote()).__name__

        num_params = len(parameters)
        # Loading checkpoint if it exists
        checkpoint, loaded_successfully = Checkpoint.loadifparams(func_name,
                                                                parameters,
                                                                [None]*num_params,
                                                                [False]*num_params,
                                                                index=0,
                                                                done=0,
                                                                path=path)
        index_map = list(range(num_params))
        if loaded_successfully:
            print("Picking up from previous checkpoint.")
            # Create the Boolean mask "`func` has not been executed".
            mask = [not completed for completed in checkpoint.completed]
            # Masking the parameters to get only the parameters left to execute
            #   `func` for.
            parameters = [p for i, p in enumerate(parameters) if mask[i]]
            # Masking the ``index_map``.
            index_map =  [i for i in index_map if mask[i]]

        # Initialising the index of the next parameters to run `func` for after a
        #   task in the current chunk completes.
        checkpoint.index = chunk_size
        # Initialising the current chunk
        chunk = parameters[:checkpoint.index]
        
        if progress_bar:
            pbar = tqdm(total=num_params, initial=checkpoint.done)
            cout = pbar.write
        else:
            cout = print

        if updated_threads is not None:
            # Waiting for function copy to complete
            ray.get(updated_threads)
        # Setting off the initial chunk
        threads = [actors[i].run.remote((index_map[i], i), *c)
                   for i, c in enumerate(chunk)]
        
        while threads: # Loops until no threads left computing
            # Collect all completed threads without waiting.
            done_threads, threads = ray.wait(threads,
                                             num_returns=len(threads),
                                             timeout=0)
            # Collect the outputs of the done threads
            values = ray.get(done_threads)
            num_values = len(values)
            if num_values != 0: # If any threads finished
                if progress_bar:
                    pbar.set_description(f"Results per iteration: {num_values}")
                try:
                    if path is not None:
                        # Save data to file.
                        # Block interrupt signals while saving is in progress.
                        signal.pthread_sigmask(signal.SIG_BLOCK,
                                               [signal.SIGINT])
                        cout("Interrupt signals have been blocked while the data is saved.")
                    for value in values:
                        # Updating checkpoint
                        checkpoint.output[value[0][0]] = value[1]
                        checkpoint.completed[value[0][0]] = True
                        checkpoint.done += 1
                        # Initialising new threads before saving so that these
                        #   can run in the background if the saving is slow.
                        if checkpoint.index < len(parameters):
                            # Getting the index of the actor that completed its
                            #   execution.
                            actor_index = value[0][1]
                            # Giving the actor the next task in the list.
                            thread = actors[actor_index].run\
                                        .remote((index_map[checkpoint.index], actor_index),
                                                *parameters[checkpoint.index])
                            threads.append(thread)
                            checkpoint.index += 1
                        if path is not None:
                            if not checkpoint.update_save():
                                warn("The checkpointing file has no saved argument values. Proceeding and continuing to save data, but you will not be able to pick up from this checkpoint.",
                                     CheckpointFailedWarning)
                        if progress_bar:
                            pbar.update(1)
                except BaseException as e:
                    if path is not None:
                        warn("There was an error while saving the data.",
                             CheckpointFailedWarning)
                    raise e
                else:
                    if path is not None:
                        cout("Data has saved successfully.")
                finally:
                    if path is not None:
                        cout("Interrupt signals have been unblocked.")
                        signal.pthread_sigmask(signal.SIG_UNBLOCK,
                                               [signal.SIGINT])
                    del done_threads
                    del values
        del threads
        del actors
    finally:
        # Shutting down ray if this function initialised it.
        if not ray_initialized:
            ray.shutdown()
    return checkpoint.output