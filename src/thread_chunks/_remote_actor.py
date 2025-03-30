import ray

from ._actor import LabelledActor

RemoteLabelledActor = ray.remote(LabelledActor)