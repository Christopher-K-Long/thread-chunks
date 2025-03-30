from typing import Any, List, Optional

from saveable_objects import SaveableObject

class CheckpointFailedWarning(Warning):
    "Warns that a checkpoint failed to save."
    pass

class Checkpoint(SaveableObject):
    """A data structure to store the progress of the parallel execution of a
    function `func`.
    """
    func_name : str
    """The name of the function being executed in parallel.
    """
    
    parameters : List[List[Any]]
    """A list of argument lists for the function. The ``i`` th call of the
    function is ``func_name(*parameters[i])``."""
    
    output : List[Any]
    """An ordered list of the outputs of the function:
    ``output[i]=func_name(*parameters[i])``. ``output[i]`` should be set
    to ``None`` if `func_name(*parameters[i])` is yet to finish execution."""

    completed : List[bool]
    """A list of which outputs have been computed. ``True`` represents the ith
    output has been computed."""
    
    index : int
    """The largest index of the parameter list currently being computed."""
    
    done : int
    """The number of outputs already computed."""
    
    def __init__(self,
                 func_name: str,
                 parameters: List[List[Any]],
                 output: List[Any],
                 completed: List[bool],
                 index: int,
                 done: int,
                 path: Optional[str] = None):
        """Initialises a data structure to store the progress of the parallel
        execution of a function.

        Parameters
        ----------
        func_name : str
            The name of the function being executed in parallel.
        parameters : List[List[Any]]
            A list of argument lists for the function. The `i`th call of the
            function is ``func_name(*parameters[i])``.
        output : List[Any]
            An ordered list of the outputs of the function:
            ``output[i]=func_name(*parameters[i])``. ``output[i]`` should be set
            to `None` if `func_name(*parameters[i])` is yet to finish execution.
        completed : List[bool]
            A list of which outputs have been computed. ``True`` represents the
            ith output has been computed.
        index : int
            The largest index of the parameter list currently being computed.
        done : int
            The number of outputs already computed.
        path : str, optional
            File path to save the object to. If ``None`` then the object is not
            saved. By default ``None``.
        """
        self.func_name = func_name
        self.parameters = parameters
        self.output = output
        self.completed = completed
        self.index = index
        self.done = done
        super().__init__(path=path)
