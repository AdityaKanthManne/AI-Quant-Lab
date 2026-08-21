from research_copilot.models import ProjectCreate, ResearchProject
from research_copilot.storage import ProjectStore


def test_project_store_creates_research_memory(tmp_path):
    store = ProjectStore(tmp_path)
    request = ProjectCreate(name="Prediction Markets", research_question="Can markets forecast volatility?")
    project = ResearchProject(**request.model_dump(), slug=store.slugify(request.name))
    path = store.create_project(project)
    assert (path / "question.yaml").exists()
    assert (path / "experiments").is_dir()
    loaded, _ = store.find_project(project.id)
    assert loaded.id == project.id

