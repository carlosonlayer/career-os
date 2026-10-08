import json
import os
from typing import Any

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api.app.extractor import extract_deterministic

DATABASE_URL = os.environ["DATABASE_URL"]
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none").lower()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

app = FastAPI(title="Career OS API", version="0.2.0")

class JobInput(BaseModel):
    external_url: str | None = None
    source: str = "manual"
    company: str
    title: str
    seniority: str | None = None
    location: str | None = None
    employment_type: str | None = None
    description: str = Field(min_length=50)

def extract_job(job: JobInput) -> dict[str, Any]:
    payload = job.model_dump()
    if LLM_PROVIDER == "none":
        return extract_deterministic(payload)
    if LLM_PROVIDER != "openai":
        raise RuntimeError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
    from openai import OpenAI
    response = OpenAI(api_key=api_key).responses.create(
        model=MODEL,
        instructions="""Extract only requirements explicitly present in the job description.
Normalize technology names. Return only valid JSON with company,title,seniority,location,
employment_type,skills:[{canonical_name,category,required,importance,evidence}],
responsibilities,experience_requirements,education_requirements,language_requirements.""",
        input=json.dumps(payload, ensure_ascii=False),
    )
    try:
        return json.loads(response.output_text.strip())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"LLM returned invalid JSON: {response.output_text}") from exc

def persist_job(job: JobInput, extracted: dict[str, Any]) -> dict[str, Any]:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO jobs
                (external_url,source,company,title,seniority,location,employment_type,description)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (external_url) DO UPDATE SET
                company=EXCLUDED.company,title=EXCLUDED.title,seniority=EXCLUDED.seniority,
                location=EXCLUDED.location,employment_type=EXCLUDED.employment_type,
                description=EXCLUDED.description,updated_at=NOW()
                RETURNING id""",
                (job.external_url,job.source,extracted.get("company") or job.company,
                 extracted.get("title") or job.title,extracted.get("seniority") or job.seniority,
                 extracted.get("location") or job.location,extracted.get("employment_type") or job.employment_type,
                 job.description))
            job_id=cur.fetchone()[0]
            for skill in extracted.get("skills",[]):
                name=skill["canonical_name"].strip()
                if not name: continue
                cur.execute("""INSERT INTO skills(canonical_name,category) VALUES(%s,%s)
                    ON CONFLICT(canonical_name) DO UPDATE SET category=COALESCE(EXCLUDED.category,skills.category)
                    RETURNING id""",(name,skill.get("category")))
                skill_id=cur.fetchone()[0]
                cur.execute("""INSERT INTO job_skills(job_id,skill_id,importance,required,evidence)
                    VALUES(%s,%s,%s,%s,%s)
                    ON CONFLICT(job_id,skill_id) DO UPDATE SET importance=EXCLUDED.importance,
                    required=EXCLUDED.required,evidence=EXCLUDED.evidence""",
                    (job_id,skill_id,float(skill.get("importance",1)),bool(skill.get("required",True)),skill.get("evidence","")))
                cur.execute("INSERT INTO skill_inventory(skill_id) VALUES(%s) ON CONFLICT DO NOTHING",(skill_id,))
                cur.execute("""INSERT INTO market_skill_demand(skill_id,jobs_count,required_count,demand_score)
                    VALUES(%s,1,%s,%s)
                    ON CONFLICT(skill_id) DO UPDATE SET jobs_count=market_skill_demand.jobs_count+1,
                    required_count=market_skill_demand.required_count+EXCLUDED.required_count,
                    demand_score=market_skill_demand.demand_score+EXCLUDED.demand_score,updated_at=NOW()""",
                    (skill_id,1 if skill.get("required",True) else 0,float(skill.get("importance",1))))
        conn.commit()
    return {"job_id":job_id,"extracted":extracted}

def priority(required: bool, importance: float, jobs_count: int, current: float, target: float, evidence: float):
    gap=max(target-current,0); proof_gap=max(10-evidence,0); demand=min(jobs_count/10,1)
    value=((1 if required else .5)*.35+demand*.25+(gap/10)*.25+(proof_gap/10)*.15)*importance
    return round(value,4),gap,proof_gap,demand

@app.get("/health")
def health():
    with psycopg.connect(DATABASE_URL) as conn: conn.execute("SELECT 1")
    return {"status":"ok","llm_provider":LLM_PROVIDER}

@app.post("/jobs/intake")
def intake(job: JobInput):
    try:
        result=persist_job(job,extract_job(job))
        result["llm_provider"]=LLM_PROVIDER
        return result
    except Exception as exc:
        raise HTTPException(status_code=500,detail=str(exc)) from exc

@app.get("/jobs/{job_id}/gap")
def job_gap(job_id:int):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT js.skill_id,s.canonical_name,js.required,js.importance,js.evidence,
                COALESCE(si.current_level,0),COALESCE(si.target_level,8),COALESCE(si.evidence_level,0),
                COALESCE(msd.jobs_count,0) FROM job_skills js JOIN skills s ON s.id=js.skill_id
                LEFT JOIN skill_inventory si ON si.skill_id=js.skill_id
                LEFT JOIN market_skill_demand msd ON msd.skill_id=js.skill_id WHERE js.job_id=%s
                ORDER BY js.importance DESC,s.canonical_name""",(job_id,))
            rows=cur.fetchall()
            if not rows: raise HTTPException(status_code=404,detail="Job not found or has no extracted skills")
            gaps=[]
            for sid,name,required,importance,evidence,current,target,proof,jobs_count in rows:
                p,gap,proof_gap,demand=priority(required,float(importance),jobs_count,float(current),float(target),float(proof))
                title=f"Implement {name} proof in AI Engineering Lab"
                criteria="\\n".join([f"- Working implementation using {name}","- Automated or reproducible test","- README with architecture and trade-offs","- Git commit with implementation","- Publishable evidence URL"])
                cur.execute("""INSERT INTO learning_tasks(skill_id,job_id,task_type,title,priority,acceptance_criteria)
                    VALUES(%s,%s,'build',%s,%s,%s) RETURNING id""",(sid,job_id,title,p,criteria))
                task_id=cur.fetchone()[0]
                gaps.append({"skill":name,"required":required,"current_level":float(current),"target_level":float(target),
                    "evidence_level":float(proof),"gap":gap,"proof_gap":proof_gap,"demand":demand,"priority":p,
                    "proof_task":{"id":task_id,"title":title,"market_evidence":evidence}})
            match_score=0.0
            cur.execute("UPDATE jobs SET match_score=%s,status='analyzed',updated_at=NOW() WHERE id=%s",(match_score,job_id))
        conn.commit()
    return {"job_id":job_id,"match_score":match_score,"gaps":sorted(gaps,key=lambda x:x["priority"],reverse=True)}
