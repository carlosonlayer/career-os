import re
from typing import Any

SKILL_RULES = (("Python","Programming",(r"\bpython\b",)),("FastAPI","Backend",(r"\bfastapi\b",)),("Django","Backend",(r"\bdjango\b",)),("SQL","Data",(r"\bsql\b",)),("PostgreSQL","Data",(r"\bpostgres(?:ql)?\b",)),("Git","Engineering",(r"\bgit\b",)),("GitHub","Engineering",(r"\bgithub\b",)),("Docker","DevOps",(r"\bdocker\b",)),("CI/CD","DevOps",(r"\bci\s*/\s*cd\b",r"\bci\s*cd\b")),("AWS","Cloud",(r"\baws\b",)),("Azure","Cloud",(r"\bazure\b",)),("GCP","Cloud",(r"\bgcp\b",)),("LLM APIs","Generative AI",(r"\bllm(?:s)?\b",r"large language model",r"openai api")),("Prompt Engineering","Generative AI",(r"prompt engineering",)),("RAG","Generative AI",(r"\brag\b",r"retrieval[- ]augmented generation")),("Embeddings","Generative AI",(r"\bembeddings?\b",)),("pgvector","Generative AI",(r"\bpgvector\b",)),("Vector Databases","Generative AI",(r"vector database",r"vector db")),("LangChain","Generative AI",(r"\blangchain\b",)),("LangGraph","Generative AI",(r"\blanggraph\b",)),("Agents","Generative AI",(r"\bagentic ai\b",r"\bai agents?\b",r"\bagents?\b")),("Tool Calling","Generative AI",(r"tool calling",r"function calling")),("MCP","Generative AI",(r"\bmcp\b",r"model context protocol")),("Redis","Data",(r"\bredis\b",)),("Observability","Operations",(r"\bobservability\b",)),("AI Evaluation","Generative AI",(r"\bllm eval(?:uation|s)?\b",r"model evaluation")),("Kubernetes","Infrastructure",(r"\bkubernetes\b",r"\bk8s\b")),("Terraform","Infrastructure",(r"\bterraform\b",)),("Machine Learning","Machine Learning",(r"machine learning",)),("PyTorch","Machine Learning",(r"\bpytorch\b",)),("TensorFlow","Machine Learning",(r"\btensorflow\b",)))
OPTIONAL=("nice to have","nice-to-have","preferred","plus","bonus","diferencial","desejável","desejavel","optional")

def extract_deterministic(job: dict[str, Any]) -> dict[str, Any]:
    text=job["description"]; lower=text.lower(); skills=[]
    for name,category,patterns in SKILL_RULES:
        m=next((re.search(p,lower,re.I) for p in patterns if re.search(p,lower,re.I)),None)
        if not m: continue
        evidence=" ".join(text[max(0,m.start()-110):min(len(text),m.end()+110)].split())
        optional=any(x in evidence.lower() for x in OPTIONAL)
        skills.append({"canonical_name":name,"category":category,"required":not optional,"importance":0.6 if optional else 1.0,"evidence":evidence})
    return {"company":job["company"],"title":job["title"],"seniority":job.get("seniority"),"location":job.get("location"),"employment_type":job.get("employment_type"),"skills":skills,"responsibilities":[],"experience_requirements":[],"education_requirements":[],"language_requirements":[],"extractor":"deterministic"}
