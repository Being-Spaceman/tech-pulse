import contextlib
import io
import os
import unittest
from unittest import mock

from pulse import alerts

SECRET = "https://hc-ping.example/0b1c2d3e-secret"


class Response:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Ping(unittest.TestCase):
    def call(self, env, urlopen):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env), mock.patch("pulse.alerts.time.sleep"), \
                mock.patch("pulse.alerts.urllib.request.urlopen", urlopen), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            ok = alerts.ping("HC_TEST_URL", "/fail")
        self.assertNotIn("secret", out.getvalue() + err.getvalue())
        return ok

    def test_missing_env_is_quiet(self):
        opener = mock.Mock()
        self.assertFalse(self.call({"HC_TEST_URL": ""}, opener))
        opener.assert_not_called()

    def test_success_and_suffix(self):
        opener = mock.Mock(return_value=Response(200))
        self.assertTrue(self.call({"HC_TEST_URL": SECRET}, opener))
        self.assertEqual(opener.call_args[0][0].full_url, SECRET + "/fail")

    def test_failures_never_raise(self):
        for effect in (OSError("down " + SECRET), ValueError("x"), [Response(500)] * 2):
            with self.subTest(effect=effect):
                opener = mock.Mock(side_effect=effect)
                self.assertFalse(self.call({"HC_TEST_URL": SECRET}, opener))
                self.assertEqual(opener.call_count, 2)


if __name__ == "__main__":
    unittest.main()
