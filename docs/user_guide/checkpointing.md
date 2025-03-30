# Checkpointing

Typically, we are interested in parallelising computationally intensive tasks. For this reason it is important to checkpoint the progress of the task in case the program crashes or your computer unexpectedly shuts down. To achieve this we employ the [saveable-objects](https://saveable-objects.readthedocs.io/) package.

Specifically, if we parallelise the function
```python
def f(x,y):
    return x+y
```
using
```python
from thread_chunks import chunk
outputs = chunk(f, [[1, 4], [2, 5], [3, 6]], path="checkpoint.pkl")
```
then as soon as each call to ``f`` completes [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) saves the result to the pickle file ``checkpoint.pkl``. If our computation crashes partway through we can simply call
```python
from thread_chunks import chunk
outputs = chunk(f, [[1, 4], [2, 5], [3, 6]], path="checkpoint.pkl")
```
again and the computation will pick up where it left off. That is no call already executed will be repeated.

However, the checkpoint also tracks the function name and the parameters. Thus if our computation crashed halfway through and we then execute
```python
from thread_chunks import chunk
outputs = chunk(g, [[1, 4], [2, 5], [3, 6]], path="checkpoint.pkl")
```
for some different function ``g`` or
```python
from thread_chunks import chunk
outputs = chunk(f, [[0, 4], [2, 5], [3, 6]], path="checkpoint.pkl") # different parameters
```
or 
```python
from thread_chunks import chunk
outputs = chunk(f, [[1, 4], [2, 5], [3, 6], [3, 7]], path="checkpoint.pkl") # more parameters
```
or 
```python
from thread_chunks import chunk
outputs = chunk(f, [[1, 4], [2, 5]], path="checkpoint.pkl") # less parameters
```
or
```python
from thread_chunks import chunk
outputs = chunk(f, [[2, 5], [1, 4], [3, 6]], path="checkpoint.pkl") # different order of parameters
```
then ``checkpoint.pkl`` will be overwritten and all function executions redone. 

The checkpoint is an instance of [``Checkpoint``](../reference/_autosummary/thread_chunks.Checkpoint.rst) and can be loaded to inspect the progress as follows:
```python
from thread_chunks import Checkpoint
checkpoint = Checkpoint.load("checkpoint.pkl")
```
The output of [``chunk()``](../reference/_autosummary/thread_chunks.chunk.rst) is stored as a list in ``checkpoint.output``. Uncompleted executions have the value ``None``.

In the next chapter we will delve deeper into the actors that underlie ``thread-chunks``.

---
[Previous](chunking.md) | [Next](actors.md)