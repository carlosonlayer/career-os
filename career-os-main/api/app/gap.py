def calculate_gap(current_level: float, target_level: float, evidence_level: float) -> dict:
    gap = max(target_level - current_level, 0)
    proof_gap = max(10 - evidence_level, 0)
    return {"gap": gap, "proof_gap": proof_gap}
