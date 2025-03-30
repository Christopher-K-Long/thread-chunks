from typing import Tuple, Any, Callable

class LabelledActor():
    """A ray actor that can execute the function `func` along with a label to
    allow an ordering of calls to be re-established. Additionally, as the actor
    stores `func` so that copying of `func` only occurs on initialisation opposed
    to every call of `func`.
    """
    def __init__(self, func: Callable):
        """Initialises a :class:`LabelledActor`

        Parameters
        ----------
        func : Callable
            The function saved by the actor.
        """
        self._func = func
    def run(self,
            label: Any,
            *args: Any
           ) -> Tuple[Any, Any]:
        """A wrapping that allows labelled execution of the function.

        Parameters
        ----------
        label : Any
            The label assigned to the execution.
        *args : Any
            The arguments to pass to the stored function `func`.

        Returns
        -------
        Tuple[Any, Any]
            The label followed by the return of `func`.
        """
        return label, self._func(*args)
    def set_func(self, func: Callable):
        """Updates the function `func` stored by the actor.

        Parameters
        ----------
        func : Callable
            The new function.
        """
        self._func = func
    def get_func(self) -> Callable:
        """Gets the function `func` stored by the actor.

        Returns
        -------
        Callable
            The stored function.
        """
        return self._func