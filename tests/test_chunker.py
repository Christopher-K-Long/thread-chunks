import os
import threading
import datetime
import inspect

from thread_chunks import Chunker, config, Checkpoint

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
SAVE_DIR = os.path.join(TEST_DIR, "__test_write_directory__")

class UniquePath():
    def __init__(self):
        thread_id = threading.current_thread().ident
        datetime.datetime.now().strftime("%Z%Y%m%d%H%M%S%f")
        self.unique_path = os.path.join(SAVE_DIR, f"calling_function_{__name__}_{inspect.stack()[1][3]}__thread_id_{thread_id}__datetime_{datetime.datetime.now().strftime('%Z%Y%m%d%H%M%S%f')}.pkl")
    def __enter__(self):
        return self.unique_path
    def __exit__(self, exception_type, exception_value, exception_traceback):
        if os.path.exists(self.unique_path):
            os.remove(self.unique_path)

func = lambda x: 2*x
parameters = [[1], [2], [3]]*config.default_chunk_size

def test_func_call_chunker():
    chunker = Chunker(func)
    output = chunker(parameters)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_func_call_chunker_func_update():
    chunker = Chunker(lambda x: None)
    output = chunker(parameters, func=func)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_func_call_chunker_custom_chunk_size():
    chunker = Chunker(func, chunk_size=config.default_chunk_size+1)
    output = chunker(parameters)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_func_call_chunker_oposite_progress_bar():
    chunker = Chunker(func, progress_bar=not config.progress_bar)
    output = chunker(parameters)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_func_call_chunker_oposite_progress_bar_update():
    chunker = Chunker(func)
    output = chunker(parameters, progress_bar=not config.progress_bar)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_actor_call_chunker():
    actors = Chunker(func, persistent=True).actors
    chunker = Chunker(actors=actors)
    output = chunker(parameters)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_actor_call_chunker_oposite_progress_bar():
    actors = Chunker(func, persistent=True).actors
    chunker = Chunker(actors=actors, progress_bar=not config.progress_bar)
    output = chunker(parameters)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_actor_call_chunker_oposite_progress_bar_update():
    actors = Chunker(func, persistent=True).actors
    chunker = Chunker(actors=actors)
    output = chunker(parameters, progress_bar=not config.progress_bar)
    assert all([func(*p) == o for p, o in zip(parameters, output)])

def test_actor_call_chunker_oposite_chunk_size_greater_than_actors():
    actors = Chunker(func, persistent=True).actors
    raised = False
    try:
        Chunker(actors=actors, chunk_size=len(actors)+1)
    except ValueError:
        raised = True
    assert raised

def test_actor_call_chunker_oposite_chunk_size_less_than_actors():
    actors = Chunker(func, persistent=True).actors
    raised = False
    try:
        Chunker(actors=actors, chunk_size=len(actors)-1)
    except ValueError:
        raised = True
    assert raised

def test_checkpointing():
    with UniquePath() as path:
        chunker = Chunker(func, path=path)
        chunker(parameters)
        checkpoint = Checkpoint.load(path)
        assert checkpoint.func_name == func.__name__
        assert checkpoint.parameters == parameters
        assert all([func(*p) == o for p, o in zip(parameters, checkpoint.output)])
        assert checkpoint.completed == [True]*len(parameters)
        assert checkpoint.index == len(parameters)
        assert checkpoint.done == len(parameters)
        assert checkpoint.path == path

def test_checkpointing_update():
    with UniquePath() as path:
        chunker = Chunker(func)
        chunker(parameters, path=path)
        checkpoint = Checkpoint.load(path)
        assert checkpoint.func_name == func.__name__
        assert checkpoint.parameters == parameters
        assert all([func(*p) == o for p, o in zip(parameters, checkpoint.output)])
        assert checkpoint.completed == [True]*len(parameters)
        assert checkpoint.index == len(parameters)
        assert checkpoint.done == len(parameters)
        assert checkpoint.path == path
        