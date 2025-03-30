from thread_chunks import LabelledActor

FUNC = lambda x: 2*x
FUNC2 = lambda x: 3*x
TEST_VALUE = 3
LABEL = "label"

def test_LabelledActor():
    actor = LabelledActor(FUNC)
    out_label, out_value = actor.run(LABEL, TEST_VALUE)
    assert out_value == FUNC(TEST_VALUE)
    assert out_label == LABEL

def test_set_func():
    actor = LabelledActor(FUNC)
    actor.set_func(FUNC2)
    out_label, out_value = actor.run(LABEL, TEST_VALUE)
    assert out_value == FUNC2(TEST_VALUE)
    assert out_label == LABEL

def test_get_func():
    actor = LabelledActor(FUNC)
    _, out_value = actor.run(LABEL, TEST_VALUE)
    assert actor.get_func()(TEST_VALUE) == out_value