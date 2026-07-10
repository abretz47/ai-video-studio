from types import SimpleNamespace

import pytest

from app.api.v1.endpoints.scripts import quality as quality_endpoint
from app.models.task import TaskStatus
from app.schemas.script_quality import ScriptLintOptions
from app.services.script_quality import lint_script_content, lint_script_content_async
from app.services.script_quality import task_entrypoints


class _CliffhangerManager:
    def __init__(self, passed=True, score=1.0, success=True):
        self.passed = passed
        self.score = score
        self.success = success
        self.calls = []

    async def generate_text(self, **kwargs):
        self.calls.append(kwargs)
        if not self.success:
            return SimpleNamespace(success=False, error="provider down")
        return SimpleNamespace(
            success=True,
            provider="fake",
            model=kwargs.get("model") or "fake-model",
            data={
                "passed": self.passed,
                "score": self.score,
                "reason": "Jie Wei Zhi Zao continue Kan issue" if self.passed else "Jie Wei Shou Shu",
                "evidence": "final San Xing",
                "suggestion": "Bu Yi Ge Xin issue",
            },
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lint_passes_minimal_compliant_script():
    script = """
[Di1Chang] [Hao Zhai Men Wai] [rainy night/EXT]
【sound effect】：Pa！
【fast】【emotion goal：Xiu Ru】
Zhang Mu Niang：Li Hun！
Su Chen：Xian Zai Jiu Gun？
【slow】【emotion goal：counterattack】
（close-up）Su Chen Tai Tou，Ca Diao Xue。
Su Chen：Kan Qing Chu？
"""
    result = await lint_script_content_async(
        script,
        options=ScriptLintOptions(pass_threshold=9.0),
        ai_manager=_CliffhangerManager(),
    )
    assert result.passed is True
    assert result.overall_score >= 9.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lint_flags_unfilmable_language_and_long_dialogue():
    script = """
Ta Gan Dao Bei Shang。
Xiao Ming：Wo Zhen De Fei Chang Fei Chang Fei Chang Sheng Qi Ni why Zhe Yang Zuo
Ni Hao。
Jie Shu。
"""
    result = await lint_script_content_async(
        script,
        options=ScriptLintOptions(pass_threshold=9.0),
        ai_manager=_CliffhangerManager(passed=False, score=0.0),
    )
    assert result.passed is False
    rule_ids = {r.rule_id for r in result.rules}
    assert "visual_language" in rule_ids
    assert "dialogue_length" in rule_ids
    issue_rule_ids = {i.rule_id for i in result.issues}
    assert "visual_language" in issue_rule_ids
    assert "dialogue_length" in issue_rule_ids
    assert "cliffhanger" in issue_rule_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lint_accepts_commercial_vertical_drama_format():
    script = """
Di1Ji
1-1 INT. Huang Gong Pian Dian - night
Ren Wu： Lin Xue、Chen Mo
▲【sound effect】Peng！Dian Men be Zhuang Kai，Zhu Huo Meng Di Yi Huang。
Lin Xue(Leng Xiao)：Ni Cang ledger，Wo Zhao Dao。
Chen Mo(Hou Tui)：Ni Bu Gai Peng it！
▲Lin Xue ledger Shuai Dao An on，red Zhi Yin Lu Chu。
Lin Xue(Bi Jin)：Na Jiu Gao Su Wo，who Qian Zi？
Chen Mo(Ya Di Sheng)：Ni Zhen Xiang Zhi Dao？
▲【close-up】final Yi Ye Fan Kai，Ling Yi Ge name Ya Zai Lin Xue Zhi Jian。
"""
    manager = _CliffhangerManager()
    result = await lint_script_content_async(
        script, options=ScriptLintOptions(pass_threshold=9.0), ai_manager=manager
    )

    assert result.passed is True
    assert result.overall_score >= 9.0
    rule_ids = {r.rule_id for r in result.rules}
    assert "pacing_markers" in rule_ids
    assert manager.calls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lint_accepts_alarm_blackout_cliffhanger():
    script = """
Di1Ji
▲【sound effect】Peng！frame Zhi Jie Qie Ru conflict Xian Chang。

1-1 INT. living room - night
Ren Wu： Wen Wen、Old Guai
▲Wen Wen phone Zhuan Xiang Old Guai，Zhong Duan Guang Zhao in Liang Ren Lian Shang。
Wen Wen(calm)：don't move。
Old Guai(Huang Luan)：Ni Zuo Shen Me？
▲Wen Wen Zhi Jian Xuan Zai Hui Che Jian on。
Wen Wen(Wei Xie)：Shi Miao after Xiao Hui。
Old Guai(Shi Kong)：Ni Feng！
▲Wen Wen Zhi Jian La Xia，An Xia Hui Che Jian。
▲【sound effect】Jing Bao Sheng Chi Xu，living room Xian Ru Hei An。
"""

    result = await lint_script_content_async(
        script,
        options=ScriptLintOptions(pass_threshold=9.0),
        ai_manager=_CliffhangerManager(passed=True, score=0.95),
        model="deepseek:deepseek-v4-flash",
        prefer_provider="deepseek",
    )

    assert result.passed is True
    cliffhanger = next(rule for rule in result.rules if rule.rule_id == "cliffhanger")
    assert cliffhanger.passed is True
    assert cliffhanger.details["model"] == "deepseek:deepseek-v4-flash"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lint_fails_when_cliffhanger_llm_unavailable():
    result = await lint_script_content_async(
        "Di1Ji\n【sound effect】Peng！\nScene 1 living room - night\nSu Chen：who？\n",
        options=ScriptLintOptions(pass_threshold=9.0),
        ai_manager=None,
    )

    assert result.passed is False
    cliffhanger = next(rule for rule in result.rules if rule.rule_id == "cliffhanger")
    assert cliffhanger.details["error"] == "cliffhanger_llm_unavailable"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_lint_uses_strong_local_cliffhanger_when_llm_unavailable():
    script = """
Di1Ji
1-1 INT. conference room - night
Ren Wu： AP、Chen Mo
▲Tou Ying Shu Zi Bian Hong，client Shou Zhi Chong Chong Qiao in error data on。
AP(calm)：Zheng Ju in this。
Chen Mo(Huang Luan)：Wo not Zhi Dao。
▲APphone Ju Dao camera before，Duan Xin countdown from30seconds Tiao to29seconds。
▲【close-up】camera Ting in key Xian Suo on，Suo You Sheng Yin Tu Ran Ya Di。
AP(Ya Di Sheng)：Ni Zhen Yi Wei，this Jiu Shi Quan Bu truth？
"""

    result = await lint_script_content_async(
        script,
        options=ScriptLintOptions(pass_threshold=0.0),
        ai_manager=None,
    )

    cliffhanger = next(rule for rule in result.rules if rule.rule_id == "cliffhanger")
    assert cliffhanger.passed is True
    assert cliffhanger.details["provider"] == "local_strong_cliffhanger_fallback"


@pytest.mark.unit
def test_sync_lint_requires_async_cliffhanger_judgement():
    result = lint_script_content(
        "Di1Ji\n【sound effect】Peng！\nScene 1 living room - night\nSu Chen：who？\n",
        options=ScriptLintOptions(pass_threshold=9.0),
    )

    cliffhanger = next(rule for rule in result.rules if rule.rule_id == "cliffhanger")
    assert result.passed is False
    assert cliffhanger.details["error"] == "cliffhanger_llm_unavailable"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_quality_endpoint_uses_default_model_when_no_generation_model(
    monkeypatch,
):
    manager = _CliffhangerManager()
    monkeypatch.setattr(
        quality_endpoint,
        "ai_service",
        SimpleNamespace(ai_manager=manager),
    )

    class _Service:
        def get_script(self, script_id, user):
            return SimpleNamespace(content="Di1Ji\n【sound effect】Peng！\nScene 1\nSu Chen：who？")

    result = await quality_endpoint.quality_check_script(
        script_id=1,
        options=ScriptLintOptions(pass_threshold=0.0),
        current_user=SimpleNamespace(id=1),
        service=_Service(),
    )

    assert manager.calls
    assert manager.calls[0].get("model") is None
    assert result.rules


@pytest.mark.unit
def test_script_quality_task_uses_default_model_without_generation_metadata(
    monkeypatch,
):
    manager = _CliffhangerManager()
    task = SimpleNamespace(
        parameters=None,
        status=TaskStatus.PENDING,
        description=None,
        error_message=None,
        result_file_path=None,
    )
    script = SimpleNamespace(
        content="Di1Ji\n【sound effect】Peng！\nScene 1 living room - night\nSu Chen：who？",
        is_deleted=False,
        extra_metadata={},
    )

    class _Session:
        def __init__(self):
            self.commits = 0

        def commit(self):
            self.commits += 1

        def close(self):
            pass

    class _TaskRepository:
        def __init__(self, session):
            self.session = session

        def get_by_id(self, task_id):
            return task

    class _ScriptRepository:
        def __init__(self, session):
            self.session = session

        def get_by_id(self, script_id):
            return script

    session = _Session()
    monkeypatch.setattr(task_entrypoints, "SessionLocal", lambda: session)
    monkeypatch.setattr(task_entrypoints, "TaskRepository", _TaskRepository)
    monkeypatch.setattr(task_entrypoints, "ScriptRepository", _ScriptRepository)
    monkeypatch.setattr(
        task_entrypoints,
        "ai_service",
        SimpleNamespace(ai_manager=manager),
    )

    task_entrypoints.process_script_quality_task(
        task_id=1, payload={"script_id": 2}, user_id=3
    )

    assert task.status == TaskStatus.COMPLETED
    assert task.result_file_path == "script:2:quality"
    assert manager.calls
    assert manager.calls[0].get("model") is None
    assert script.extra_metadata["script_quality"]["result"]["rules"]
