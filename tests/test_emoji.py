import clishelf.emoji as emoji


def test_demojize_and_emojize():
    msg: str = "🎯 feat"
    assert ":dart: feat" == emoji.demojize(msg)
    assert "🎯" in emoji.emojize(":dart:")

    msg: str = "⬆️ deps: upgrade"
    assert ":arrow_up: deps: upgrade" == emoji.demojize(msg)
