# Actors
## What are actors?

``thread-chunks`` utilises [ray](https://www.ray.io/) actors to execute functions in parallel. When [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) is called with a function ``f`` and a chunk of size ``chunk_size`` then ``f`` is copied to ``chunk_size`` actors. Actors are remote python classes. The class used by ``thread-chunks`` is [``LabelledActor``](../reference/_autosummary/thread_chunks.LabelledActor.rst) and the remote version ([``RemoteLabelledActor``](../reference/_autosummary/thread_chunks.RemoteLabelledActor.rst)) is defined as
```python
RemoteLabelledActor = ray.remote(LabelledActor)
```

## Reusing actors

Every time we call [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) new actors are initialised and ``f`` is copied to these new actors. If ``f`` takes up a lot of memory this copy may be slow and it makes sense to reuse these actors. To solve this problem we can initialise an instance of [``Chunker``](../reference/_autosummary/thread_chunks.Chunker.rst)
```python
from thread_chunks import Chunker
chunker = Chunker(f, chunk_size=chunk_size)
```
which generates ``chunk_size`` actors and pre-loads them with the function ``f``. We can then call
```python
output = chunker(parameters)
```
as many times as we like without copying ``f``. The output is equivalent to
 ```python
output = chunk(f, parameters, chunk_size=chunk_size)
```

If we call
```python
output = chunker(parameters, g)
```
the function stored in the actors will be replaced with ``g`` which requires ``g`` to be copied to all the actors. However, subsequent calls of
```python
output = chunker(parameters)
```
will then execute ``g``, as ``g`` is now the saved function in the actors.

The actors can also be extracted from ``chunker`` and passed to ``chunk`` as follows:
```python
actors = chunker.actors
output = chunk(None, parameters, actors, chunk_size=chunk_size)
```
Note that now [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) will use the function stored in the ``actors``.

In a similar manner to before, if we pass a new function ``h`` and ``actors`` to [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) then the function stored in the ``actors`` will be overwritten. That is
```python
output = chunk(h, parameters, actors, chunk_size=chunk_size)
```
will execute ``h`` in parallel using the passed ``actors``

### Ray initialisations

In a similar vein to reusing actors we can also reuse [ray](https://www.ray.io/) initialisations to decrease wall clock times. If [ray](https://www.ray.io/) is not initialised when [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) is called, then [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) will initialise [ray](https://www.ray.io/) and shutdown [ray](https://www.ray.io/) when it has completed. However, if [ray](https://www.ray.io/) was initialised before calling [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) then [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) will not shutdown [ray](https://www.ray.io/) when it has completed. Similarly, when an instance of [``Chunker``](../reference/_autosummary/thread_chunks.Chunker.rst) is initialised [ray](https://www.ray.io/) will be initialised if it has not already been. When the instance of [``Chunker``](../reference/_autosummary/thread_chunks.Chunker.rst) is deleted then [ray](https://www.ray.io/) will be shutdown if [ray](https://www.ray.io/) was initialised by the instance of [``Chunker``](../reference/_autosummary/thread_chunks.Chunker.rst). However, if the argument [``persistent``](../reference/_autosummary/thread_chunks.Chunker.rst#thread_chunks.Chunker.persistent) is passed as ``True`` when initialising [``Chunker``](../reference/_autosummary/thread_chunks.Chunker.rst), then [ray](https://www.ray.io/) will not be shutdown when the instance is deleted. Finally, if different [ray](https://www.ray.io/) options to [``config.ray_config``](../reference/_autosummary/thread_chunks.config.ray_config.rst) are desired then [ray](https://www.ray.io/) should be initialised before using [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) or [``Chunker``](../reference/_autosummary/thread_chunks.Chunker.rst).

## Custom actors

Finally, ``thread-chunks`` can be extended by creating a custom remote actor that inherits [``LabelledActor``](../reference/_autosummary/thread_chunks.LabelledActor.rst):
```python
@ray.remote
class CustomRemoteLabelledActor(LabelledActor):
    ...
```
We can then pass these custom actors to [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst):
```python
actors = [CustomRemoteLabelledActor.remote(f) for _ in range(chunk_size)]
output = chunk(None, parameters, actors, chunk_size=chunk_size)
```
or to [``Chunker``](../reference/_autosummary/thread_chunks.Chunker.rst):
```python
chunker = Chunker(actors=actors, chunk_size=chunk_size)
```
Note that the function ``f`` is pre-loaded into the ``actors``. We can also change the pre-loaded function to another function, say ``g``, as follows:
```python
output = chunk(g, parameters, actors, chunk_size=chunk_size)
```

Now you know everything you need to go and use ``thread-chunks``!

---
[Previous](checkpointing.md)