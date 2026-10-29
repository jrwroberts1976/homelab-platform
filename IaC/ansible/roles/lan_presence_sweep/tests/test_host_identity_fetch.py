import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)
from host_identity import fetch_exporter_interfaces


class HostIdentityFetchTests(unittest.TestCase):
    def test_successful_retrieval(self):
        payload = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{
                    "metric": {
                        "target_name": "admin-01",
                        "address": "b8:27:eb:e8:36:cd",
                        "instance": "192.168.2.48:9100",
                    },
                    "value": [1000, "1"],
                }],
            },
        }
        response = io.BytesIO(json.dumps(payload).encode())

        with patch(
            "urllib.request.urlopen",
            return_value=response,
        ):
            result = fetch_exporter_interfaces()

        self.assertEqual(
            result[0]["metric"]["target_name"], "admin-01"
        )

    def test_invalid_response_rejected(self):
        response = io.BytesIO(
            b'{"status":"error","data":{}}'
        )
        with patch(
            "urllib.request.urlopen",
            return_value=response,
        ):
            with self.assertRaises(ValueError):
                fetch_exporter_interfaces()


if __name__ == "__main__":
    unittest.main()
