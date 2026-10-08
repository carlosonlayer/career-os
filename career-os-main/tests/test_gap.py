from api.app.gap import calculate_gap


def test_gap_calculation():
    assert calculate_gap(2, 8, 3) == {"gap": 6, "proof_gap": 7}
