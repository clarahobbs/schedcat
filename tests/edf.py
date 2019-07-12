from __future__ import division

import unittest

from fractions import Fraction

import schedcat.sched.edf.bak as bak
import schedcat.sched.edf.bar as bar
import schedcat.sched.edf.bcl_iterative as bcli
import schedcat.sched.edf.bcl as bcl
import schedcat.sched.edf.da as da
import schedcat.sched.edf.ffdbf as ffdbf
import schedcat.sched.edf.gfb as gfb
import schedcat.sched.edf.rta as rta
import schedcat.sched.edf.gy_rta as gy_rta
import schedcat.sched.edf as edf

import schedcat.sched as sched

import schedcat.model.tasks as tasks


# TODO: add unit tests for EDF schedulability tests

class DA(unittest.TestCase):
    def setUp(self):
        self.ts = tasks.TaskSystem([
                tasks.SporadicTask(80, 100),
                tasks.SporadicTask(33, 66),
                tasks.SporadicTask(7, 10),
            ])

    def test_util_bound(self):
        self.assertTrue(da.has_bounded_tardiness(2, self.ts))
        self.assertFalse(da.has_bounded_tardiness(1, self.ts))

    def test_bound_is_integral(self):
        self.assertTrue(da.bound_response_times(2, self.ts))
        self.assertTrue(isinstance(self.ts[0].response_time, int))
        self.assertTrue(isinstance(self.ts[1].response_time, int))
        self.assertTrue(isinstance(self.ts[2].response_time, int))

        self.assertFalse(da.bound_response_times(1, self.ts))

class Test_bar(unittest.TestCase):
    def setUp(self):
        self.ts = tasks.TaskSystem([
            tasks.SporadicTask(10, 100),
            tasks.SporadicTask(33, 200),
            tasks.SporadicTask(10, 300, 100),
        ])

    def test_basic_functionality(self):
        self.assertTrue(bar.is_schedulable(1, self.ts))

        self.ts.append(tasks.SporadicTask(27, 28))
        self.assertFalse(bar.is_schedulable(1, self.ts))
        self.assertTrue(bar.is_schedulable(2, self.ts))

class Test_ffdbf(unittest.TestCase):

    def setUp(self):
        self.t1 = tasks.SporadicTask(5000, 10000)
        self.t2 = tasks.SporadicTask(5000, 10000, deadline = 7000)

    def test_ffdbf1(self):
        one = Fraction(1)
        self.assertEqual(
            ffdbf.ffdbf(self.t1, 0, one),
            0)
        self.assertEqual(
            ffdbf.ffdbf(self.t1, 5000, one),
            0)
        self.assertEqual(
            ffdbf.ffdbf(self.t1, 5001, one),
            1)
        self.assertEqual(
            ffdbf.ffdbf(self.t1, 7000, one),
            2000)
        self.assertEqual(
            ffdbf.ffdbf(self.t1, 9999, one),
            4999)
        self.assertEqual(
            ffdbf.ffdbf(self.t1, 10001, one),
            5000)
        self.assertEqual(
            ffdbf.ffdbf(self.t1, 14001, one),
            5000)

    def test_ffdbf_constrained(self):
        one = Fraction(1)
        self.assertEqual(
            ffdbf.ffdbf(self.t2, 0, one),
            0)
        self.assertEqual(
            ffdbf.ffdbf(self.t2, 1000, one),
            0)
        self.assertEqual(
            ffdbf.ffdbf(self.t2, 2001, one),
            1)
        self.assertEqual(
            ffdbf.ffdbf(self.t2, 4000, one),
            2000)
        self.assertEqual(
            ffdbf.ffdbf(self.t2, 6999, one),
            4999)
        self.assertEqual(
            ffdbf.ffdbf(self.t2, 10001, one),
            5000)
        self.assertEqual(
            ffdbf.ffdbf(self.t2, 12001, one),
            5001)

    def test_test_points(self):
        one = Fraction(1)
        pts = ffdbf.test_points(self.t1, one, 0)
        pts = iter(pts)
        self.assertEqual(next(pts),  5000)
        self.assertEqual(next(pts), 10000)
        self.assertEqual(next(pts), 15000)
        self.assertEqual(next(pts), 20000)


        pts = ffdbf.test_points(self.t2, one, 0)
        pts = iter(pts)
        self.assertEqual(next(pts),  2000)
        self.assertEqual(next(pts),  7000)
        self.assertEqual(next(pts), 12000)
        self.assertEqual(next(pts), 17000)


        pts = ffdbf.test_points(self.t1, Fraction(1, 2), 0)
        pts = iter(pts)
        self.assertEqual(next(pts), 10000)
        self.assertEqual(next(pts), 10000)
        self.assertEqual(next(pts), 20000)

        pts = ffdbf.test_points(self.t2, Fraction(8, 10), 0)
        pts = iter(pts)
        self.assertEqual(next(pts),   750)
        self.assertEqual(next(pts),  7000)
        self.assertEqual(next(pts), 10750)
        self.assertEqual(next(pts), 17000)

    def test_testing_set(self):
        one = Fraction(1)
        ts = tasks.TaskSystem([self.t1, self.t2])
        pts = ffdbf.testing_set(ts, one, 0)
        ts = iter(pts)
        self.assertEqual(next(pts),  2000)
        self.assertEqual(next(pts),  5000)
        self.assertEqual(next(pts),  7000)
        self.assertEqual(next(pts), 10000)
        self.assertEqual(next(pts), 12000)
        self.assertEqual(next(pts), 15000)
        self.assertEqual(next(pts), 17000)
        self.assertEqual(next(pts), 20000)


class Test_QPA(unittest.TestCase):

    def setUp(self):
        self.ts =  tasks.TaskSystem([
            tasks.SporadicTask(6000, 31000, deadline=18000),
            tasks.SporadicTask(2000,  9800, deadline= 9000),
            tasks.SporadicTask(1000, 17000, deadline=12000),
            tasks.SporadicTask(  90,  4200, deadline= 3000),
            tasks.SporadicTask(   8,    96, deadline=   78),
            tasks.SporadicTask(   2,    12, deadline=   16),
            tasks.SporadicTask(  10,   280, deadline=  120),
            tasks.SporadicTask(  26,   660, deadline=  160),
            ])

    def test_qpa_schedulable(self):
        qpa = edf.native.QPATest(1)
        self.assertTrue(qpa.is_schedulable(sched.get_native_taskset(self.ts)))

    def test_edf_schedulable(self):
        self.assertTrue(edf.is_schedulable(1, self.ts))

    def test_qpa_not_schedulable(self):
        self.ts.append(tasks.SporadicTask(   10,    100, deadline=15))
        qpa = edf.native.QPATest(1)
        self.assertFalse(qpa.is_schedulable(sched.get_native_taskset(self.ts)))

    def test_edf_not_schedulable(self):
        self.ts.append(tasks.SporadicTask(   10,    100, deadline=15))
        self.assertFalse(edf.is_schedulable(1, self.ts))

    def test_qpa_known_unschedulable(self):
        qpa = edf.native.QPATest(1)
        ts1 = tasks.TaskSystem([
            tasks.SporadicTask(331, 15000, deadline=2688),
            tasks.SporadicTask(3654, 77000, deadline=3849)
            ])
        self.assertFalse(qpa.is_schedulable(sched.get_native_taskset(ts1)))

        ts2 =  tasks.TaskSystem([tasks.SporadicTask(331, 15000, deadline=2688),
            tasks.SporadicTask(413, 34000, deadline=1061),
            tasks.SporadicTask(3654, 77000, deadline=3849),
            tasks.SporadicTask(349, 70000, deadline=20189),
            tasks.SporadicTask(1113, 83000, deadline=10683),
            ])
        self.assertFalse(qpa.is_schedulable(sched.get_native_taskset(ts2)))

class Test_gy_rta(unittest.TestCase):
    def setUp(self):
        self.ts1 = tasks.TaskSystem([tasks.SporadicTask(3,12), tasks.SporadicTask(2,4)])
        self.ts2 = tasks.TaskSystem([tasks.SporadicTask(3,12), tasks.SporadicTask(2,3), tasks.SporadicTask(2,4)])
        self.ts3 = tasks.TaskSystem([tasks.SporadicTask(2,9), tasks.SporadicTask(3,12), tasks.SporadicTask(2,4)])
        self.ts4 = tasks.TaskSystem([tasks.SporadicTask(1,4), tasks.SporadicTask(1,12), tasks.SporadicTask(3,16)])
        self.ts5 = tasks.TaskSystem([tasks.SporadicTask(1,4), tasks.SporadicTask(2,4)])
        self.ts6 = tasks.TaskSystem([tasks.SporadicTask(2,5,4), tasks.SporadicTask(3,6,5)])
        self.ts7 = tasks.TaskSystem([tasks.SporadicTask(2,4,3), tasks.SporadicTask(3,12,10), tasks.SporadicTask(2,9,7)])

    def test_approx_wcrt(self):
        gy_rta.approx_wcrt(self.ts1)
        self.assertEqual(self.ts1[0].response_time, 2)
        self.assertEqual(self.ts1[1].response_time, 9)

        self.assertFalse(gy_rta.approx_wcrt(self.ts2))

        gy_rta.approx_wcrt(self.ts3)
        self.assertEqual(self.ts3[0].response_time, 3)
        self.assertEqual(self.ts3[1].response_time, 8)
        self.assertEqual(self.ts3[2].response_time, 11)

        gy_rta.approx_wcrt(self.ts4)
        self.assertEqual(self.ts4[0].response_time, 1)
        self.assertEqual(self.ts4[1].response_time, 4)
        self.assertEqual(self.ts4[2].response_time, 8)

        gy_rta.approx_wcrt(self.ts5)
        self.assertEqual(self.ts5[0].response_time, 3)
        self.assertEqual(self.ts5[1].response_time, 3)

        gy_rta.approx_wcrt(self.ts6)
        self.assertEqual(self.ts6[0].response_time, 4)
        self.assertEqual(self.ts6[1].response_time, 5)

        gy_rta.approx_wcrt(self.ts7)
        self.assertEqual(self.ts7[0].response_time, 3)
        self.assertEqual(self.ts7[1].response_time, 7)
        self.assertEqual(self.ts7[2].response_time, 10)

    def test_exact_wcrt(self):
        gy_rta.exact_wcrt(self.ts1)
        self.assertEqual(self.ts1[0].response_time, 2)
        self.assertEqual(self.ts1[1].response_time, 7)

        self.assertFalse(gy_rta.exact_wcrt(self.ts2))

        gy_rta.exact_wcrt(self.ts3)
        self.assertEqual(self.ts3[0].response_time, 3)
        self.assertEqual(self.ts3[1].response_time, 8)
        self.assertEqual(self.ts3[2].response_time, 11)

        gy_rta.exact_wcrt(self.ts4)
        self.assertEqual(self.ts4[0].response_time, 1)
        self.assertEqual(self.ts4[1].response_time, 2)
        self.assertEqual(self.ts4[2].response_time, 6)

        gy_rta.exact_wcrt(self.ts5)
        self.assertEqual(self.ts5[0].response_time, 3)
        self.assertEqual(self.ts5[1].response_time, 3)

        gy_rta.exact_wcrt(self.ts6)
        self.assertEqual(self.ts6[0].response_time, 4)
        self.assertEqual(self.ts6[1].response_time, 5)

        gy_rta.exact_wcrt(self.ts7)
        self.assertEqual(self.ts7[0].response_time, 3)
        self.assertEqual(self.ts7[1].response_time, 7)
        self.assertEqual(self.ts7[2].response_time, 10)

