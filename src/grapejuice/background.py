import logging
import threading
import traceback
from typing import Union, Callable

from grapejuice_common.util.event import Event

OptionalCallback = Union[Callable, None]


class Task:
    _log: logging.Logger
    _on_finish_callback: OptionalCallback = None
    _on_error_callback: OptionalCallback = None

    def __init__(
        self, name,
        on_finish_callback: OptionalCallback = None,
        on_error_callback: OptionalCallback = None
    ):
        self._log = logging.getLogger(f"{Task.__name__}/{name}")

        self._on_finish_callback = on_finish_callback
        self._on_error_callback = on_error_callback
        self._name = name
        self._finished = False
        self._collection: Union[None, TaskCollection] = None

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

    def on_finished(self):
        if callable(self._on_finish_callback):
            self._on_finish_callback(self)

    def on_error(self, e: Exception):
        self._log.error(str(e))

        try:
            self._log.error(traceback.format_exc())

        except Exception as format_error:
            # There was an error while you were formatting your error
            # So let's error while erroring
            # ...dawg
            self._log.error(str(format_error))

        if callable(self._on_error_callback):
            self._on_error_callback(self, e)

    def finish(self):
        self.on_finished()
        self._finished = True

        if self.collection is not None:
            self.collection.remove(self)

    def work(self):
        pass

    @property
    def name(self):
        return self._name


class BackgroundTask(threading.Thread, Task):
    def __init__(self, name="Untitled task", **kwargs):
        threading.Thread.__init__(self)
        Task.__init__(self, name, **kwargs)

    def run(self) -> None:
        try:
            self.work()

        except Exception as e:
            self.on_error(e)

        self.finish()

    def __repr__(self):
        return "BackgroundTask: {}".format(self._name)


class MockBackgroundTask(Task):
    def start(self):
        pass


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
        if task in self._tasks:
            self._tasks.remove(task)

        self.task_removed(task)
        self.tasks_changed()

    @property
    def count(self):
        return len(self._tasks)


tasks = TaskCollection()
