from src.orchestration.planner import Planner


def test_detect_domains():
    p = Planner()
    assert "git" in p.detect_domains("create a pull request for the branch")
    assert "design" in p.detect_domains("build a responsive UI component")
    assert "general" in p.detect_domains("hello")


def test_create_graph():
    p = Planner()
    g = p.create_graph("s1", "inspect the git status and fix the frontend layout")
    assert g.root_task_id is not None
    assert len(g.tasks) >= 1
