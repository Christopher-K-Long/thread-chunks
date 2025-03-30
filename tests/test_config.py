import thread_chunks as tc

def test_default_chunk_size():
    chunker0 = tc.Chunker(lambda: None)
    assert chunker0.chunk_size == tc.config.default_chunk_size