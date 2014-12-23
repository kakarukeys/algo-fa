import unittest
from unittest.mock import patch, MagicMock

from requests.exceptions import ConnectionError

from fa.miner import http


class TestHTTP(unittest.TestCase):
    def test_liberal_get(self):
        class MockResponse(object):
            def __init__(self, url):
                """ HTTP response from accessing the URL """
                self.status_code = 200
                self.text = url[7:]

        with patch("fa.miner.wsj.requests.get", MagicMock(side_effect=MockResponse)) as mock_get:
            data = http.lenient_get("http://foo")

            mock_get.assert_called_once_with("http://foo")

        self.assertEqual(data, "foo")

    def test_liberal_get_server_error(self):
        class MockResponse(object):
            def __init__(self, url):
                """ HTTP response from accessing the URL """
                self.status_code = 400
                self.reason = "bad request"
                self.url = url

        with patch("fa.miner.wsj.requests.get", MagicMock(side_effect=MockResponse)):
            data = http.lenient_get("http://err")

        self.assertEqual(data, '')

    def test_liberal_get_error_exception_handling(self):
        with patch("fa.miner.wsj.requests.get", MagicMock(side_effect=ConnectionError)):
            data = http.lenient_get("http://ex")

        self.assertEqual(data, '')

if __name__ == "__main__":
    unittest.main()
