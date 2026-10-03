"""
atk.component 的 4.2 新增模块单元测试 — access / vgt / constellation /
cat / coord / maneuver。

用 unittest.mock 模拟 SWIG 对象，断言调用序列。
枚举值经 vendored stub（ATKComponentPythonModule 测试替身）解析。
"""

import pytest
from unittest.mock import MagicMock

from atk import exceptions as atk_exc
from atk.component.session import _get_enum


# ----------------------------------------------------------------------
# component.access
# ----------------------------------------------------------------------

class TestAccessCalculator:
    """AccessCalculator（IAtkAccess 封装）的测试。"""

    def _make(self):
        from atk.component.access import AccessCalculator
        obj = MagicMock()
        return AccessCalculator(obj, "Facility/Fac1"), obj

    def test_get_access_called_with_target(self):
        calc, obj = self._make()
        obj.GetAccess.assert_called_once_with("Facility/Fac1")

    def test_set_time_period(self):
        calc, obj = self._make()
        calc.set_time_period("s", "e")
        obj.GetAccess.return_value.SetAccessTimePeriod.assert_called_once_with("s", "e")

    def test_set_time_step_and_use_ltd(self):
        calc, obj = self._make()
        calc.set_time_step(60.0)
        calc.set_use_ltd(True)
        acc = obj.GetAccess.return_value
        acc.SetTimeStep.assert_called_once_with(60.0)
        acc.SetUseLTD.assert_called_once_with(True)

    def test_compute_calls_compute_access(self):
        calc, obj = self._make()
        calc.compute()
        obj.GetAccess.return_value.ComputeAccess.assert_called_once_with()

    def test_intervals_normalizes_to_list(self):
        calc, obj = self._make()
        obj.GetAccess.return_value.ComputedAccessIntervalTimes.return_value = [
            ("t1", "t2")
        ]
        assert calc.intervals() == [("t1", "t2")]

    def test_output_report_resolves_enum(self):
        calc, obj = self._make()
        calc.output_report("AER_SUMMARY")
        obj.GetAccess.return_value.OutputAccessReport.assert_called_once_with(
            _get_enum("eACCESS_AER_SUMMARY_REP")
        )

    def test_output_report_naccess_prefix(self):
        calc, obj = self._make()
        calc.output_report("NACCESS_INTRVL")
        obj.GetAccess.return_value.OutputAccessReport.assert_called_with(
            _get_enum("eNACCESS_INTRVL_REP")
        )

    def test_output_report_rejects_unknown(self):
        calc, _ = self._make()
        with pytest.raises(atk_exc.ATKValueError):
            calc.output_report("BOGUS")

    def test_clear_and_remove(self):
        calc, obj = self._make()
        calc.clear()
        calc.remove()
        acc = obj.GetAccess.return_value
        acc.ClearAccess.assert_called_once()
        acc.RemoveAccess.assert_called_once()

    def test_constraints_delegates(self):
        calc, obj = self._make()
        cons = calc.constraints()
        cons.add("LineOfSight")
        cons.remove("LineOfSight")
        coll = obj.GetAccessConstraints.return_value
        coll.AddNamedConstraint.assert_called_once_with("LineOfSight")
        coll.RemoveNamedConstraint.assert_called_once_with("LineOfSight")
        cons.available()
        coll.AvailableConstraints.assert_called_once()
        cons.count()
        coll.GetCount.assert_called_once()


# ----------------------------------------------------------------------
# component.vgt
# ----------------------------------------------------------------------

class TestVgtBuilder:
    """VgtBuilder（ICrdnProvider 封装）的测试。"""

    def _make(self):
        from atk.component.vgt import VgtBuilder
        obj = MagicMock()
        return VgtBuilder(obj), obj

    def test_create_resolves_short_name(self):
        vgt, obj = self._make()
        vgt.create("vector", "V1", "d", "Displacement")
        obj.GetVGT.return_value.GetVectors.return_value.Create \
            .assert_called_once_with(
                "V1", "d", _get_enum("eCrdnVectorTypeDisplacement")
            )

    def test_create_accepts_full_enum_name(self):
        vgt, obj = self._make()
        vgt.create("angle", "A1", "d", "eCrdnAngleTypeBetweenVectors")
        obj.GetVGT.return_value.GetAngles.return_value.Create \
            .assert_called_once_with(
                "A1", "d", _get_enum("eCrdnAngleTypeBetweenVectors")
            )

    def test_create_rejects_unknown_group(self):
        vgt, _ = self._make()
        with pytest.raises(atk_exc.ATKValueError):
            vgt.create("bogus", "X", "d", "T")

    def test_create_rejects_unknown_type(self):
        vgt, _ = self._make()
        with pytest.raises(atk_exc.ATKValueError):
            vgt.create("vector", "X", "d", "NoSuchType")

    def test_remove_contains_item_supported(self):
        vgt, obj = self._make()
        vgt.remove("vector", "V1")
        vgt.contains("vector", "V1")
        vgt.item("vector", "V1")
        vgt.supported_types("vector")
        grp = obj.GetVGT.return_value.GetVectors.return_value
        grp.Remove.assert_called_once_with("V1")
        grp.Contains.assert_called_once_with("V1")
        grp.Item.assert_called_once_with("V1")
        grp.GetSupportedVGTTypes.assert_called_once()

    def test_create_vector_displacement_configures_points(self):
        vgt, obj = self._make()
        vec = vgt.create_vector_displacement("V1", "Origin", "Dest", "RefSys")
        vec.SetStartPoint.assert_called_once_with("Origin")
        vec.SetEndPoint.assert_called_once_with("Dest")
        vec.SetReferenceSystem.assert_called_once_with("RefSys")

    def test_create_vector_cross_product(self):
        vgt, _ = self._make()
        vec = vgt.create_vector_cross_product("V1", "A", "B")
        vec.SetVectorA.assert_called_once_with("A")
        vec.SetVectorB.assert_called_once_with("B")

    def test_create_angle_between_vectors(self):
        vgt, _ = self._make()
        ang = vgt.create_angle_between_vectors("A1", "F", "T")
        ang.SetVectorFrom.assert_called_once_with("F")
        ang.SetVectorTo.assert_called_once_with("T")


# ----------------------------------------------------------------------
# component.constellation
# ----------------------------------------------------------------------

class TestConstellationDesigner:
    """ConstellationDesigner（IConstellDesign 封装）的测试。"""

    def _make(self):
        from atk.component.constellation import ConstellationDesigner
        session = MagicMock()
        return ConstellationDesigner(session), session

    def test_walker_delta_call_signature(self):
        d, session = self._make()
        d.walker_delta(6678137, 0.0, 28.5, 0.0, 180.0, 180.0,
                       2, 8, 1.0, 360.0)
        session.root.GetConstellDesign.return_value \
            .ConstellDesignWalkerDelta.assert_called_once_with(
                6678137, 0.0, 28.5, 0.0, 180.0, 180.0, 2, 8, 1.0, 360.0
            )

    def test_walker_delta_by_seed_call_signature(self):
        d, session = self._make()
        d.walker_delta_by_seed("Satellite/S1", 2, 8, 1.0, 360.0)
        session.root.GetConstellDesign.return_value \
            .ConstellDesignWalkerDeltaBySeed.assert_called_once_with(
                "Satellite/S1", 2, 8, 1.0, 360.0
            )

    def test_flower_call_signature(self):
        d, session = self._make()
        d.flower(6678137, 0.0, 28.5, 0.0, 180.0, 180.0,
                 16.0, 1.0, 16.0, 1.0, 16, 360.0)
        session.root.GetConstellDesign.return_value \
            .ConstellDesignFlower.assert_called_once_with(
                6678137, 0.0, 28.5, 0.0, 180.0, 180.0,
                16.0, 1.0, 16.0, 1.0, 16, 360.0
            )

    def test_all_twelve_methods_reach_design(self):
        d, session = self._make()
        design = session.root.GetConstellDesign.return_value
        d.walker_custom(1, 0, 0, 0, 0, 0, 2, 20, 1.0, 1.0)
        d.walker_custom_by_seed("S", 2, 20, 1.0, 1.0)
        d.rosette(1, 0, 0, 0, 0, 0, 3, 9, 1.0)
        d.rosette_by_seed("S", 3, 9, 1.0)
        d.flower_by_seed("S", 16.0, 1.0, 16.0, 1.0, 16, 360.0)
        d.asymmetric_flower(1, 0, 0, 0, 0, 0, 16.0, 1.0, 16, 30.0)
        d.asymmetric_flower_by_seed("S", 16.0, 1.0, 16, 30.0)
        assert design.ConstellDesignWalkerCustom.call_count == 1
        assert design.ConstellDesignWalkerCustomBySeed.call_count == 1
        assert design.ConstellDesignRosette.call_count == 1
        assert design.ConstellDesignRosetteBySeed.call_count == 1
        assert design.ConstellDesignFlowerBySeed.call_count == 1
        assert design.ConstellDesignNonSymFlower.call_count == 1
        assert design.ConstellDesignNonSymFlowerBySeed.call_count == 1


# ----------------------------------------------------------------------
# component.cat
# ----------------------------------------------------------------------

class TestCatAnalysis:
    """CatAnalysis（ICat 封装）的测试。"""

    def _make(self):
        from atk.component.cat import CatAnalysis
        session = MagicMock()
        return CatAnalysis(session), session

    def test_set_primary_satellites_builds_vectors(self):
        cat, session = self._make()
        cat.set_primary_satellites(["Sat1", "Sat2"], "tle.txt",
                                   exclude_ssc=["25544"])
        args = session.root.GetCat.return_value \
            .SetSatelliteFromScenario.call_args[0]
        assert list(args[0]) == ["Sat1", "Sat2"]
        assert args[1] == "tle.txt"
        assert list(args[2]) == ["25544"]

    def test_set_all_tle_objects(self):
        cat, session = self._make()
        cat.set_all_tle_objects("tle.txt")
        session.root.GetCat.return_value.SetAllTLEObjects \
            .assert_called_once()

    def test_time_range_and_compute(self):
        cat, session = self._make()
        cat.use_scenario_time(False)
        cat.set_time_period("s", "e")
        cat.set_max_range(10000.0)
        cat.compute()
        icat = session.root.GetCat.return_value
        icat.SetUseScenarioTimePeriod.assert_called_once_with(False)
        icat.SetTimePeriod.assert_called_once_with("s", "e")
        icat.SetMaxRange.assert_called_once_with(10000.0)
        icat.Compute.assert_called_once()

    def test_get_results_returns_twelve_lists(self):
        cat, _ = self._make()
        result = cat.get_results()
        assert len(result) == 12
        assert all(v == [] for v in result.values())
        assert set(result) == {
            "primary_ssc", "secondary_ssc", "equiv_dist", "miss_distance",
            "miss_dist_r", "miss_dist_t", "miss_dist_n", "angle_ca",
            "relative_velocity", "tca", "tin", "tout",
        }

    def test_advance_config_delegates(self):
        cat, session = self._make()
        cat.advance.set_yellow_threshold(50.0)
        cat.advance.set_red_threshold(20.0)
        cat.advance.set_equival_factor(1.5)
        adv = session.root.GetCat.return_value.GetAdvance.return_value
        adv.SetYellowDistThreshold.assert_called_once_with(50.0)
        adv.SetRedDistThreshold.assert_called_once_with(20.0)
        adv.SetEquivalFactor.assert_called_once_with(1.5)


# ----------------------------------------------------------------------
# component.coord
# ----------------------------------------------------------------------

class TestBatchCoordinateTransform:
    """BatchCoordinateTransform（IATKBatchCrdnTransform 封装）的测试。"""

    def _make(self):
        from atk.component.coord import BatchCoordinateTransform
        session = MagicMock()
        return BatchCoordinateTransform(session), session

    def _transform(self, session):
        return session.root.GetBatchCrdnTransform.return_value

    def test_set_time_utc(self):
        t, session = self._make()
        t.set_time_utc("UTCG")
        tr = self._transform(session)
        tr.SetTimeType.assert_called_once_with(_get_enum("eUTCTIME"))
        tr.SetUTCTimeType.assert_called_once_with("UTCG")

    def test_set_time_relative(self):
        t, session = self._make()
        t.set_time_relative("1 Jul 2024 00:00:00.000")
        tr = self._transform(session)
        tr.SetTimeType.assert_called_with(_get_enum("eRELATIVETIME"))
        tr.SetRelativeTimeStart.assert_called_once_with(
            "1 Jul 2024 00:00:00.000"
        )

    def test_set_source_destination_units(self):
        t, session = self._make()
        t.set_source("Earth", "J2000")
        t.set_destination("Earth", "Fixed")
        t.set_units("m", "s")
        tr = self._transform(session)
        tr.SetSrcCoordinate.assert_called_once_with("Earth", "J2000")
        tr.SetDstCoordinate.assert_called_once_with("Earth", "Fixed")
        tr.SetDistanceUnit.assert_called_once_with("m")
        tr.SetTimeUnit.assert_called_once_with("s")

    def test_set_data_sequence_pushes_ints(self):
        t, session = self._make()
        t.set_data_sequence(0, 1, 2, 3)
        vec = self._transform(session).SetCrdnTransformParam.call_args[0][0]
        assert list(vec) == [0, 1, 2, 3]

    def test_set_import_file(self):
        t, session = self._make()
        t.set_import_file("/tmp/in.txt")
        tr = self._transform(session)
        tr.SetImportFileType.assert_called_once_with(_get_enum("eTxt"))
        tr.SetImportFilePath.assert_called_once_with("/tmp/in.txt")

    def test_set_import_file_ephemeris(self):
        t, session = self._make()
        t.set_import_file("/tmp/in.e", file_type="ephemeris")
        self._transform(session).SetImportFileType.assert_called_once_with(
            _get_enum("eEPHEMERIS")
        )

    def test_set_import_file_rejects_unknown_type(self):
        t, _ = self._make()
        with pytest.raises(atk_exc.ATKValueError):
            t.set_import_file("/tmp/x", "bogus")

    def test_export(self):
        t, session = self._make()
        t.export("/tmp/out.txt")
        self._transform(session).Export.assert_called_once_with("/tmp/out.txt")


# ----------------------------------------------------------------------
# component.maneuver
# ----------------------------------------------------------------------

class TestManeuverDetectionAnalysis:
    """ManeuverDetectionAnalysis（IMnvPODDataBaseDetection 封装）的测试。"""

    def _make(self):
        from atk.component.maneuver import ManeuverDetectionAnalysis
        sat = MagicMock()
        return ManeuverDetectionAnalysis(sat), sat

    def test_chains_maneuver_detection(self):
        _, sat = self._make()
        sat.GetManeuverDetection.return_value.GetPODDataBaseDetection \
            .assert_called_once()

    def test_set_orbit_propagator_resolves_name(self):
        md, sat = self._make()
        md.set_orbit_propagator("PropagatorTwoBody")
        sat.GetManeuverDetection.return_value \
            .GetPODDataBaseDetection.return_value.SetOrbitPropagator \
            .assert_called_once_with(_get_enum("ePropagatorTwoBody"))

    def test_set_orbit_propagator_rejects_unknown(self):
        md, _ = self._make()
        with pytest.raises(atk_exc.ATKValueError):
            md.set_orbit_propagator("PropagatorNoSuch")

    def test_set_object_states(self):
        md, sat = self._make()
        pod = sat.GetManeuverDetection.return_value \
            .GetPODDataBaseDetection.return_value
        md.set_object_a_time("t0")
        md.set_object_a_j2000(1, 2, 3, 4, 5, 6)
        md.set_object_a_vvlh(7, 8, 9, 10, 11, 12)
        md.set_object_b_time("t1")
        md.set_object_b_j2000(13, 14, 15, 16, 17, 18)
        md.set_object_b_vvlh(19, 20, 21, 22, 23, 24)
        pod.SetObjectATime.assert_called_once_with("t0")
        pod.SetObjectAJ2000Frame.assert_called_once_with(1, 2, 3, 4, 5, 6)
        pod.SetObjectAVVLHFrame.assert_called_once_with(7, 8, 9, 10, 11, 12)
        pod.SetObjectBTime.assert_called_once_with("t1")
        pod.SetObjectBJ2000Frame.assert_called_once_with(13, 14, 15, 16, 17, 18)
        pod.SetObjectBVVLHFrame.assert_called_once_with(19, 20, 21, 22, 23, 24)

    def test_compute_returns_dict(self):
        md, _ = self._make()
        result = md.compute()
        assert set(result) == {
            "mnv_res", "detect_dv_utc", "detect_dv", "sma", "inc",
            "ecc", "raan", "time", "mahalanobis_dist",
        }
        assert result["time"] == []
        assert result["mahalanobis_dist"] == []


class TestTLEManeuverDetection:
    """TLEManeuverDetection（IMnvTLEDataBaseDetection 封装）的测试。"""

    def _make(self):
        from atk.component.maneuver import ManeuverDetectionAnalysis
        sat = MagicMock()
        md = ManeuverDetectionAnalysis(sat)
        return md, sat

    def test_tle_database_property_chains(self):
        md, sat = self._make()
        tle = md.tle_database
        sat.GetManeuverDetection.return_value.GetTLEDataBaseDetection \
            .assert_called_once()
        assert tle.raw is sat.GetManeuverDetection.return_value \
            .GetTLEDataBaseDetection.return_value

    def test_set_tle_data_and_config(self):
        md, _ = self._make()
        tle = md.tle_database
        tle.set_tle_data("/tmp/tle.txt")
        tle.set_jud_method_id(3.0)
        tle.set_step_of_cross_propagation(60.0)
        raw = tle.raw
        raw.SetTLEData.assert_called_once_with("/tmp/tle.txt")
        raw.SetJudMethodID.assert_called_once_with(3.0)
        raw.SetStepOfCrossPropagation.assert_called_once_with(60.0)

    def test_compute_passes_time_vector_and_returns_lists(self):
        md, _ = self._make()
        tle = md.tle_database
        result = tle.compute("1 Jul 2035 00:00:00.000")
        args = tle.raw.Compute.call_args[0]
        assert list(args[0]) == ["1 Jul 2035 00:00:00.000"]
        assert set(result) == {
            "outliers", "sma_dev", "radial", "transverse", "normal",
        }
        assert all(v == [] for v in result.values())
