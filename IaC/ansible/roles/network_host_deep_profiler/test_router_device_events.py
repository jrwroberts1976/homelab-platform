"""Regression tests for ASUS router DHCP event parsing."""

import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

SOURCE = Path(__file__).parent / "templates/homelab-router-device-events.py.j2"
parser = SourceFileLoader("router_events", str(SOURCE)).load_module().parse_dhcp_ack

PREFIX = "Sep 24 15:28:17 RT-AC86U dnsmasq-dhcp[16216]: "
MAC = "2c:cf:67:30:be:20"


class RouterEventTests(unittest.TestCase):
    def test_valid_ack(self):
        self.assertEqual(
            parser(PREFIX + f"DHCPACK(br0) 192.168.2.196 {MAC} media-01"),
            {"mac": MAC, "ip": "192.168.2.196", "hostname": "media-01"},
        )

    def test_missing_hostname(self):
        result = parser(PREFIX + f"DHCPACK(br0) 192.168.2.197 {MAC}")
        self.assertEqual(result["hostname"], "")

    def test_invalid_ip(self):
        self.assertIsNone(parser(PREFIX + f"DHCPACK(br0) invalid-ip {MAC}"))

    def test_request_is_not_ack(self):
        self.assertIsNone(
            parser(PREFIX + f"DHCPREQUEST(br0) 192.168.2.196 {MAC}")
        )


if __name__ == "__main__":
    unittest.main()


class DeviceStateTests(unittest.TestCase):
    def setUp(self):
        self.apply = SourceFileLoader(
            "router_state", str(SOURCE)
        ).load_module().apply_dhcp_ack
        self.devices = {}
        self.event = {
            "mac": MAC,
            "ip": "192.168.2.196",
            "hostname": "media-01",
        }

    def test_new_device_queued_once(self):
        self.assertTrue(self.apply(self.devices, self.event, 1000))
        self.assertEqual(self.devices[MAC]["status"], "pending")
        self.assertFalse(self.apply(self.devices, self.event, 1100))

    def test_renewal_preserves_profile(self):
        self.apply(self.devices, self.event, 1000)
        self.devices[MAC]["status"] = "complete"
        self.assertFalse(self.apply(self.devices, self.event, 1100))
        self.assertEqual(self.devices[MAC]["status"], "complete")
        self.assertEqual(self.devices[MAC]["last_inventory_seen"], 1100)

    def test_ip_change_preserves_identity(self):
        self.apply(self.devices, self.event, 1000)
        self.devices[MAC]["status"] = "complete"
        changed = {**self.event, "ip": "192.168.2.195"}
        self.assertFalse(self.apply(self.devices, changed, 1200))
        self.assertEqual(self.devices[MAC]["last_ip"], "192.168.2.195")
        self.assertEqual(
            self.devices[MAC]["previous_ips"], ["192.168.2.196"]
        )
        self.assertEqual(self.devices[MAC]["status"], "complete")


class PersistenceTests(unittest.TestCase):
    def test_restart_does_not_rediscover_device(self):
        from tempfile import TemporaryDirectory

        module = SourceFileLoader(
            "router_persistence", str(SOURCE)
        ).load_module()
        event = {"mac": MAC, "ip": "192.168.2.196",
                 "hostname": "media-01"}

        with TemporaryDirectory() as directory:
            path = Path(directory) / "devices.json"
            devices = {}
            self.assertTrue(module.apply_dhcp_ack(devices, event, 1000))
            module.save_devices(path, devices)

            restored = module.load_devices(path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertFalse(module.apply_dhcp_ack(restored, event, 1100))
            self.assertEqual(restored[MAC]["status"], "pending")

            path.write_text('{"schema_version":1,"devices":[]}')
            with self.assertRaises(ValueError):
                module.load_devices(path)


class LogReaderTests(unittest.TestCase):
    def test_partial_line_and_restart(self):
        from tempfile import TemporaryDirectory

        module = SourceFileLoader(
            "router_reader", str(SOURCE)
        ).load_module()
        prefix = PREFIX + "DHCPACK(br0) "
        first = f"{prefix}192.168.2.196 {MAC} media-01\n".encode()
        second = (
            f"{prefix}192.168.2.219 ec:91:61:9c:a4:45"
        ).encode()

        with TemporaryDirectory() as directory:
            log = Path(directory) / "router.log"
            state = Path(directory) / "devices.json"
            log.write_bytes(first + second)

            with log.open("rb") as stream:
                self.assertEqual(
                    module.consume_complete_lines(
                        stream, state, {}, 0, 1000
                    ), (1, 1)
                )

            devices, cursor = module.load_checkpoint(state)
            self.assertEqual(cursor["offset"], len(first))

            with log.open("ab") as stream:
                stream.write(b" phone\n")

            with log.open("rb") as stream:
                self.assertEqual(
                    module.consume_complete_lines(
                        stream, state, devices, cursor["offset"], 1100
                    ), (1, 1)
                )

            devices, cursor = module.load_checkpoint(state)
            with log.open("rb") as stream:
                self.assertEqual(
                    module.consume_complete_lines(
                        stream, state, devices, cursor["offset"], 1200
                    ), (0, 0)
                )
            self.assertEqual(len(devices), 2)


class LogRotationTests(unittest.TestCase):
    def test_rotation_and_missing_log(self):
        from tempfile import TemporaryDirectory

        module = SourceFileLoader(
            "router_rotation", str(SOURCE)
        ).load_module()

        with TemporaryDirectory() as directory:
            log = Path(directory) / "rt-ac86u.log"
            log.write_text("old router event\n")
            cursor = {"inode": log.stat().st_ino, "offset": 4}

            self.assertEqual(
                module.locate_resume_log(log, cursor),
                (log, 4, False),
            )

            rotated = Path(f"{log}.1")
            log.rename(rotated)
            log.write_text("new router event\n")

            self.assertEqual(
                module.locate_resume_log(log, cursor),
                (rotated, 4, True),
            )

            rotated.unlink()
            with self.assertRaises(RuntimeError):
                module.locate_resume_log(log, cursor)


class RotationIntegrationTests(unittest.TestCase):
    def test_process_events_across_rotation(self):
        from tempfile import TemporaryDirectory

        module = SourceFileLoader(
            "router_integration", str(SOURCE)
        ).load_module()
        prefix = PREFIX + "DHCPACK(br0) "

        with TemporaryDirectory() as directory:
            log = Path(directory) / "rt-ac86u.log"
            state = Path(directory) / "devices.json"

            log.write_text(
                f"{prefix}192.168.2.196 {MAC} media-01\n"
            )
            self.assertEqual(
                module.process_log_once(log, state, 1000), (1, 1)
            )

            with log.open("a") as output:
                output.write(
                    f"{prefix}192.168.2.219 "
                    "ec:91:61:9c:a4:45 phone\n"
                )

            log.rename(Path(f"{log}.1"))
            log.write_text(
                f"{prefix}192.168.2.195 {MAC} media-01\n"
            )

            self.assertEqual(
                module.process_log_once(log, state, 1100), (1, 2)
            )

            devices, cursor = module.load_checkpoint(state)
            self.assertEqual(len(devices), 2)
            self.assertEqual(devices[MAC]["last_ip"], "192.168.2.195")
            self.assertEqual(
                devices[MAC]["previous_ips"], ["192.168.2.196"]
            )
            self.assertEqual(cursor["inode"], log.stat().st_ino)

            self.assertEqual(
                module.process_log_once(log, state, 1200), (0, 0)
            )


class IncompleteRotationTests(unittest.TestCase):
    def test_incomplete_rotated_log_preserves_checkpoint(self):
        from tempfile import TemporaryDirectory

        module = SourceFileLoader(
            "router_incomplete", str(SOURCE)
        ).load_module()

        with TemporaryDirectory() as directory:
            log = Path(directory) / "rt-ac86u.log"
            state = Path(directory) / "devices.json"
            log.write_text(PREFIX + f"DHCPACK(br0) 192.168.2.196 {MAC}\n")
            module.process_log_once(log, state, 1000)
            _, original_cursor = module.load_checkpoint(state)

            with log.open("a") as output:
                output.write(PREFIX + "DHCPACK(br0) 192.168.2.219")

            log.rename(Path(f"{log}.1"))
            log.write_text(PREFIX + f"DHCPACK(br0) 192.168.2.195 {MAC}\n")

            with self.assertRaises(RuntimeError):
                module.process_log_once(log, state, 1100)

            _, recovered_cursor = module.load_checkpoint(state)
            self.assertEqual(recovered_cursor, original_cursor)


class BootstrapTests(unittest.TestCase):
    def test_baseline_then_new_device(self):
        from tempfile import TemporaryDirectory

        module = SourceFileLoader("bootstrap", str(SOURCE)).load_module()
        old = PREFIX + f"DHCPACK(br0) 192.168.2.196 {MAC} media-01\n"
        renewal = PREFIX + f"DHCPACK(br0) 192.168.2.195 {MAC} media-01\n"
        new = PREFIX + "DHCPACK(br0) 192.168.2.220 aa:bb:cc:dd:ee:ff new-device\n"

        with TemporaryDirectory() as directory:
            log = Path(directory) / "router.log"
            state = Path(directory) / "devices.json"
            Path(f"{log}.1").write_text(old)
            log.write_text(renewal)

            self.assertEqual(module.bootstrap_existing(log, state, 1000), 1)
            devices, _ = module.load_checkpoint(state)
            self.assertEqual(devices[MAC]["status"], "baseline")
            self.assertEqual(devices[MAC]["previous_ips"], ["192.168.2.196"])

            with self.assertRaises(FileExistsError):
                module.bootstrap_existing(log, state, 1100)

            with log.open("a") as output:
                output.write(renewal + new)

            self.assertEqual(module.process_log_once(log, state, 1200), (1, 2))
            devices, _ = module.load_checkpoint(state)
            self.assertEqual(devices[MAC]["status"], "baseline")
            self.assertEqual(devices["aa:bb:cc:dd:ee:ff"]["status"], "pending")
            self.assertEqual(module.process_log_once(log, state, 1300), (0, 0))
