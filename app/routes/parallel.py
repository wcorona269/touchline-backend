from concurrent.futures import ThreadPoolExecutor
from flask import current_app


def run_parallel(*calls):
    """Run independent zero-argument calls concurrently and return their results in order.
    For routes that need several API calls: they still cost the same quota, but the response
    waits for the slowest call instead of the sum of all of them. Each thread gets the app
    context (the cache needs it). The first exception raised by a call propagates."""
    if not calls:
        return []
    app = current_app._get_current_object()

    def run(call):
        with app.app_context():
            return call()

    with ThreadPoolExecutor(max_workers=len(calls)) as pool:
        return list(pool.map(run, calls))
