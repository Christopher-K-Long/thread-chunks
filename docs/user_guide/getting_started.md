# Getting Started

## What is thread-chunks
``thread-chunks`` is a wrapper around [ray](https://www.ray.io/) that allows for easier memory management. It is often the case in scientific computing that a task is both memory intensive and parallelisable. As the task is memory intensive then we may run out of memory when we parallelise the task. A solution to this is to compute a *chunk* of the tasks at once. If we increase the size of the chunk more memory will be used but the wall clock time will decrease.

Naïvely, we could execute each chunk in series. However, a more efficient solution is to set off the next task as soon as one finishes. This is exactly what ``thread-chunks`` handles for you.
## Installation

The python package can be installed with pip as follows:
```bash
pip install thread-chunks
```

## Quick Start

Suppose we wish to execute the function
```python
def f(x,y):
    return x+y
```
over a range of ``x`` and ``y``. We can do this in series with a for-loop:
```python
x_values = [1, 2, 3]
y_values = [4, 5, 6]
outputs = []
for x, y in zip(x_values, y_values):
    output = f(x, y)
    outputs.append(output)
```

We can parallelise this with ``thread-chunks`` as follows:
```python
from thread_chunks import chunk
outputs = chunk(f, [[1, 4], [2, 5], [3, 6]])
```

---
[Previous](overview.md) | [Next](chunking.md)