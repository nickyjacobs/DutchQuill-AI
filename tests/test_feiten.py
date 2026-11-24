from dutchquill import feiten

ORIG = ('Volgens het CBS fietste in 2025 27% van de studenten dagelijks. De Fietsersbond noemt dit "een '
        'trend die al tien jaar doorzet" (Jansen, 2024). Meer op https://cbs.nl/fiets. Het budget was 1.200 euro.')


def test_niets_veranderd():
    nieuw = ('In 2025 fietste 27% van de studenten elke dag, zegt het CBS. Volgens de Fietsersbond is het "een '
             'trend die al tien jaar doorzet" (Jansen, 2024). Zie https://cbs.nl/fiets. Budget: 1.200 euro.')
    v = feiten.vergelijk(ORIG, nieuw)
    assert v["ok"], v


def test_getal_citaat_en_bron_weg():
    nieuw = ('Een groot deel van de studenten fietst dagelijks, zegt het CBS. De Fietsersbond ziet een '
             'trend (Jansen, 2023). Het budget was 1.500 euro.')
    v = feiten.vergelijk(ORIG, nieuw)
    assert not v["ok"]
    assert "27%" in v["ontbreekt"]["getallen"] and "1.200euro" in v["ontbreekt"]["getallen"]
    assert "1.500euro" in v["nieuw"]["getallen"]
    assert v["ontbreekt"]["citaten"] and v["ontbreekt"]["urls"] == ["https://cbs.nl/fiets"]
    assert v["ontbreekt"]["bronverwijzingen"] == ["Jansen, 2024"]
    assert v["nieuw"]["bronverwijzingen"] == ["Jansen, 2023"]
