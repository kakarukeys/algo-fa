import unittest
from unittest.mock import patch, MagicMock

from requests.exceptions import ConnectionError

from fa.miner import http
from fa.miner.exceptions import GetError


class TestHTTP(unittest.TestCase):
    def test_strict_get(self):
        class MockResponse(object):
            def __init__(self, url):
                """ HTTP response from accessing the URL """
                self.status_code = 200
                self.text = url[7:]

        with patch("fa.miner.http.requests.get", MagicMock(side_effect=MockResponse)) as mock_get:
            data = http.strict_get("http://foo")

            mock_get.assert_called_once_with("http://foo")

        self.assertEqual(data, "foo")

    def test_strict_get_error_response(self):
        class MockResponse(object):
            def __init__(self, url):
                """ HTTP response from accessing the URL """
                self.status_code = 400
                self.reason = "bad request"
                self.url = url

        with patch("fa.miner.http.requests.get", MagicMock(side_effect=MockResponse)):
            self.assertRaises(GetError, http.strict_get, "http://err")

    def test_strict_get_exception_handling(self):
        with patch("fa.miner.http.requests.get", MagicMock(side_effect=ConnectionError)):
            self.assertRaises(GetError, http.strict_get, "http://ex")

    def test_strict_get_test_for_error(self):
        test_for_error = lambda r: "404" in r.url

        class MockResponse(object):
            def __init__(self, url):
                """ HTTP response from accessing the URL """
                self.status_code = 200
                self.text = "bar"
                self.reason = ''
                self.url = url

        with patch("fa.miner.http.requests.get", MagicMock(side_effect=MockResponse)):
            data = http.strict_get("http://foo", test_for_error)
            self.assertRaises(GetError, http.strict_get, "http://foo/404.html", test_for_error)

        self.assertEqual(data, "bar")

if __name__ == "__main__":
    unittest.main()
