import mock
from jobs.sim1mod1 import analyze
from pysparkling import Context


@mock.patch('jobs.sim1mod1.WordCountJobContext.initalize_counter')
@mock.patch('jobs.sim1mod1.WordCountJobContext.inc_counter')
def test_wordcount_analyze(_, __):
    result = analyze(Context())
    assert len(result) == 327
    assert result[:6] == [('ut', 17), ('eu', 16), ('vel', 14), ('nec', 14), ('quis', 12), ('vitae', 12)]
