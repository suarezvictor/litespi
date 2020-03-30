import unittest

from migen import *

from litespi.core import LiteSPICore


class TestSPIXIP(unittest.TestCase):
    def test_spi_xip_core_syntax(self):
        spi_xip = LiteSPICore()

    def test_spi_xip_read_test(self):
        dut = LiteSPICore()

        def wb_gen(dut, addr, data):
            dut.data_ok = 0

            yield dut.bus.adr.eq(addr)
            yield dut.bus.we.eq(0)
            yield dut.bus.cyc.eq(1)
            yield dut.bus.stb.eq(1)

            while (yield dut.bus.ack) == 0:
                yield

            if (yield dut.bus.dat_r) == data:
                dut.data_ok = 1

        def phy_gen(dut, addr, data):
            dut.addr_ok = 0
            dut.cmd_ok = 0

            yield dut.sink.valid.eq(0)
            yield dut.source.ready.eq(1)

            while (yield dut.source.valid) == 0:
                yield

            if (yield dut.source.addr) == (addr<<2): # address cmd
                dut.addr_ok = 1
            if (yield dut.source.cmd) == 1:
                dut.cmd_ok += 1

            yield

            while (yield dut.source.valid) == 0:
                yield

            if (yield dut.source.cmd) == 0: # read cmd
                dut.cmd_ok += 1

            yield dut.source.ready.eq(0)
            yield

            yield dut.sink.data.eq(data)
            yield dut.sink.valid.eq(1)

            while (yield dut.sink.ready) == 0:
                yield

            yield
            yield dut.sink.valid.eq(0)
            yield

        addr = 0xcafe
        data = 0xdeadbeef

        run_simulation(dut, [wb_gen(dut, addr, data), phy_gen(dut, addr, data)])
        self.assertEqual(dut.data_ok, 1)
        self.assertEqual(dut.addr_ok, 1)
        self.assertEqual(dut.cmd_ok, 2)
