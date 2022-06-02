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
