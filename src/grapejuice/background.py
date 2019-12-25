import threading
from typing import Union

from grapejuice_common.event import Event


class BackgroundTask(threading.Thread):
    def __init__(self, name="Untitled task"):
        super().__init__()
        self._name = name
        self._finished = False
        self._collection: Union[None, TaskCollection] = None

    def on_finished(self):
        pass

    def finish(self):
        self.on_finished()
        self._finished = True

        if self.collection is not None:
            self.collection.remove(self)

    @property
    def finished(self):
        return self._finished

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        assert self._collection is None, "Can only set collection once"
        self._collection = value

    @property
    def name(self):
        return self._name

    def run(self) -> None:
        raise NotImplementedError()

    def __repr__(self):
        return "BackgroundTask: {}".format(self._name)


class TaskCollection:
    def __init__(self):
        self._tasks = []

        self.task_added = Event()
        self.task_removed = Event()
        self.tasks_changed = Event()

    def add(self, task: BackgroundTask):
        task.collection = self
        self._tasks.append(task)
        task.start()

        self.task_added(task)
        self.tasks_changed()

    def remove(self, task):
        self._tasks.remove(task)
        self.task_removed(task)
        self.tasks_changed()

    @property
    def count(self):
        return len(self._tasks)


tasks = TaskCollection()