# Chunking

The basic building block of ``thread-chunks`` is the function [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst). So far we have seen that we can parallelise a function such as
```python
def f(x,y):
    return x+y
```
with the following call to [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst)
```python
from thread_chunks import chunk
outputs = chunk(f, [[1, 4], [2, 5], [3, 6]])
```
This calls ``f`` in parallel three times:
```python
f(1, 4)
f(2, 5)
f(3, 6)
```
The number of calls running in parallel (a chunk) is by default given by the number of CPUs. This can be increased or reduced with the ``chunk_size`` parameter. For example,
```python
outputs = chunk(f, [[1, 4], [2, 5], [3, 6]], chunk_size=2)
```
will run the first two calls in parallel [``f(1, 4)`` and ``f(2, 5)``] and the next call ``f(3, 6)`` as soon as one of the previous calls finishes.

For long computations, often it is helpful to be able to visually monitor the progress. To achieve this a progress bar is printed to the terminal using [tqdm](https://tqdm.github.io/). To disable/enable the progress bar the ``progress_bar`` parameter can be set to ``False``/``True``:
```python
outputs = chunk(f, [[1, 4], [2, 5], [3, 6]], progress_bar=False)
```

In the next chapter we will consider how to checkpoint our computations.

---
[Previous](getting_started.md) | [Next](checkpointing.md)