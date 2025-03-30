import os
import threading
import datetime
import inspect
from warnings import warn, filterwarnings

from thread_chunks import Checkpoint, CheckpointFailedWarning

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

def test_Checkpoint():
    with UniquePath() as path:
        a = Checkpoint("name",
                       [[1], [2], [3]],
                       [None]*3,
                       [False]*3,
                       2,
                       0,
                       path)
        b = Checkpoint.load(path)
        assert b.func_name == "name"
        assert b.parameters == [[1], [2], [3]]
        assert b.output == [None]*3
        assert b.completed == [False]*3
        assert b.index == 2
        assert b.done == 0
        assert b.path == path

def test_CheckpointFailedWarning():
    filterwarnings("error")
    raised = False
    try:
        warn("test_warning", CheckpointFailedWarning)
    except Warning:
        raised = True
    assert raised
    raised = False
    try:
        warn("test_warning", CheckpointFailedWarning)
    except CheckpointFailedWarning:
        raised = True
    assert raised