from typing import Tuple, Any, Callable
from ._actor import LabelledActor

class RemoteLabelledActor(LabelledActor):
    """A remote ray actor that can execute the function `func` along with a
    label to allow an ordering of calls to be re-established. Additionally, as
    the actor stores `func` so that copying of `func` only occurs on
    initialisation opposed to every call of `func`.

    Notes
    -----
    All method calls must be proceeded by ``.remote``. For example, to call the
    ``__init__`` method use:

    .. code-block:: python
    
        remote_labelled_actor = RemoteLabelledActor.remote(func)

    To call the ``run`` method use:
    
    .. code-block:: python
    
        remote_labelled_actor.run.remote(label, *args)

    This is required as the instance is a remote ``ray`` actor.
    """
    def __init__(self, func: Callable):
        """Initialises a :class:`RemoteLabelledActor`

        Parameters
        ----------
        func : Callable
            The function saved by the actor.
        """