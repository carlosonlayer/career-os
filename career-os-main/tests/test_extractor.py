from api.app.extractor import extract_deterministic

def test_deterministic_extractor():
    result=extract_deterministic({"company":"Example","title":"AI Engineer","description":"Required: Python, FastAPI, Postgres, Docker and RAG. Kubernetes is a nice to have."})
    skills={x["canonical_name"]:x for x in result["skills"]}
    assert {"Python","FastAPI","PostgreSQL","Docker","RAG","Kubernetes"} <= set(skills)
    assert skills["PostgreSQL"]["required"] is True
    assert skills["Kubernetes"]["required"] is False
    assert "Postgres" in skills["PostgreSQL"]["evidence"]

def test_absent_skill_is_not_invented():
    result=extract_deterministic({"company":"Example","title":"Backend Engineer","description":"Build APIs with Python and FastAPI."})
    assert {x["canonical_name"] for x in result["skills"]} == {"Python","FastAPI"}
