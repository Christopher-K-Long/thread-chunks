import ray

from thread_chunks import RemoteLabelledActor

FUNC = lambda x: 2*x
FUNC2 = lambda x: 3*x
TEST_VALUE = 3
LABEL = "label"

def test_LabelledActor():
    actor = RemoteLabelledActor.remote(FUNC)
    thread = actor.run.remote(LABEL, TEST_VALUE)
    out_label, out_value = ray.get(thread)
    assert out_value == FUNC(TEST_VALUE)
    assert out_label == LABEL

def test_set_func():
    actor = RemoteLabelledActor.remote(FUNC)
    thread = actor.set_func.remote(FUNC2)
    ray.get(thread)
    thread = actor.run.remote(LABEL, TEST_VALUE)
    out_label, out_value = ray.get(thread)
    assert out_value == FUNC2(TEST_VALUE)
    assert out_label == LABEL

def test_get_func():
    actor = RemoteLabelledActor.remote(FUNC)
    thread = actor.run.remote(LABEL, TEST_VALUE)
    _, out_value = ray.get(thread)
    assert ray.get(actor.get_func.remote())(TEST_VALUE) == out_value