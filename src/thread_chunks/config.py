"The default configuration for the thread-chunks python package."

import multiprocessing


default_chunk_size = multiprocessing.cpu_count()
"""The number of threads to launch simultaneously (a chunk) unless otherwise
specified. The value is set to the number of CPUs on the device. In the
documentation this will read as the number of CPUs on the device that compiled
the documentation.
"""

ray_config: dict = {"num_cpus": default_chunk_size}
"""Configuration options to be used for ray if ray is not initialised by the
user. The value for ``"num_cpus"`` is set to :attr:`default_chunk_size`.
"""

progress_bar: bool = True
"Whether to display a progress bar in the terminal by default."