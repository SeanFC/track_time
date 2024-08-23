from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

from track_time.repos import TimesRepo
from track_time.services import run_timer


class FakeNow:
    def __init__(self):
        self._called = False
        self._base_time = datetime(1993, 1, 1)

    def __call__(self):
        if self._called:
            return self._base_time + timedelta(hours=1)
        self._called = True
        return self._base_time


def test_run_timer():
    with NamedTemporaryFile() as f:
        from pathlib import Path

        repo = TimesRepo(Path(f.name))

        def fake_input(*args):
            return "a,b,c"

        run_timer(repo, fake_input, FakeNow())
        repo.get()
