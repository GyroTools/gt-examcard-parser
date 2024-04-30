from pathlib import Path
import examcard as ec


class TestExamCard:
    def test_parse(self):
        filename = Path(__file__).parent / 'data/DUAL_ECHO_EPI.ExamCard'
        examcard = ec.parse(filename)

        assert len(examcard) == 3
        assert examcard.get('General')
        assert examcard.get('GE-SE EPI 2Sh 1Sl')
        assert examcard.get('SE EPI 2Sh 1Sl')

        seq1 = examcard.get('GE-SE EPI 2Sh 1Sl')
        assert len(seq1.get('protocolParameter')) == 215
        assert len(seq1.get('enumDescriptions')) == 71
        assert len(seq1.get('enumMap')) == 119

        seq1 = examcard.get('GE-SE EPI 2Sh 1Sl')
        par_name = 'EX_ACQ_scan_mode'
        scan_mode = seq1.get('protocolParameter').get(par_name)
        enum_index = seq1.get('enumMap').get(par_name)
        if enum_index is not None:
            enum_desc = seq1.get('enumDescriptions')[enum_index]
            scan_mode = enum_desc.values[scan_mode]
        print(scan_mode)

