from pathlib import Path
import tempfile

from celery.signals import heartbeat_sent, worker_ready, worker_shutdown


def _get_safe_tempdir() -> Path:
    """Return a writable, existing tempdir Path. If the system tempdir looks
    invalid or cannot be created/written to, fall back to a project-local
    `tmp/` directory or current working directory.
    """
    t = Path(tempfile.gettempdir())
    try:
        if not t.is_absolute() or (t.drive == "" and str(t).startswith("\\\\")):
            raise ValueError(f"tempdir path looks invalid: {t}")
        t.mkdir(parents=True, exist_ok=True)
        test_file = t / ".maxkb_tmp_test"
        with test_file.open("w") as f:
            f.write("")
        try:
            test_file.unlink()
        except Exception as e:
            print("Tempdir unlink test error:", e)
            pass
        return t
    except Exception as e:
        print("Tempdir test error:", e)
        fallback = Path.cwd() / "tmp"
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback
        except Exception as e:
            print("Tempdir fallback test error:", e)
            return Path.cwd()


@heartbeat_sent.connect
def heartbeat(sender, **kwargs):
    worker_name = sender.eventer.hostname.split('@')[0]
    tempdir = _get_safe_tempdir()
    heartbeat_path = tempdir / f'worker_heartbeat_{worker_name}'
    try:
        heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Heartbeat mkdir error for {heartbeat_path.parent}:", e)
    try:
        heartbeat_path.touch(exist_ok=True)
    except Exception as e:
        print("Heartbeat signal error:", e)


@worker_ready.connect
def worker_ready(sender, **kwargs):
    worker_name = sender.hostname.split('@')[0]
    tempdir = _get_safe_tempdir()
    ready_path = tempdir / f'worker_ready_{worker_name}'
    try:
        ready_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Worker ready mkdir error for {ready_path.parent}:", e)
    try:
        ready_path.touch(exist_ok=True)
    except Exception as e:
        print("Worker ready signal error:", e)


@worker_shutdown.connect
def worker_shutdown(sender, **kwargs):
    worker_name = sender.hostname.split('@')[0]
    tempdir = _get_safe_tempdir()
    for signal in ['ready', 'heartbeat']:
        path = tempdir / f'worker_{signal}_{worker_name}'
        try:
            # Python 3.8+ supports missing_ok
            path.unlink(missing_ok=True)
        except TypeError:
            try:
                if path.exists():
                    path.unlink()
            except Exception as e:
                print("Worker shutdown signal error:", e)
        except Exception as e:
            print("Worker shutdown signal error:", e)
