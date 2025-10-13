import pytest

from clishelf.bump.version_part import (
    ConfiguredPartConf,
    NumericPartConf,
    VersionPart,
    labels_for_format,
)


@pytest.fixture(params=[None, (("0", "1", "2"),), (("0", "3"),)])
def conf_vs_part(request):
    """Return a three-part and a two-part version part configuration."""
    if request.param is None:
        return NumericPartConf()
    else:
        return ConfiguredPartConf(*request.param)


def test_version_part_init(conf_vs_part):
    assert (
        VersionPart(conf_vs_part.first_value, conf_vs_part).value
        == conf_vs_part.first_value
    )


def test_version_part_copy(conf_vs_part):
    vp = VersionPart(conf_vs_part.first_value, conf_vs_part)
    vc = vp.copy()
    assert vp.value == vc.value
    assert id(vp) != id(vc)


def test_version_part_bump(conf_vs_part):
    vp = VersionPart(conf_vs_part.first_value, conf_vs_part)
    vc = vp.bump()
    assert vc.value == conf_vs_part.bump(conf_vs_part.first_value)


def test_version_part_check_optional_false(conf_vs_part):
    assert (
        not VersionPart(conf_vs_part.first_value, conf_vs_part)
        .bump()
        .is_optional()
    )


def test_version_part_check_optional_true(conf_vs_part):
    assert VersionPart(conf_vs_part.first_value, conf_vs_part).is_optional()


def test_version_part_format(conf_vs_part):
    assert (
        f"{VersionPart(conf_vs_part.first_value, conf_vs_part)}"
        == conf_vs_part.first_value
    )


def test_version_part_equality(conf_vs_part):
    assert VersionPart(conf_vs_part.first_value, conf_vs_part) == VersionPart(
        conf_vs_part.first_value, conf_vs_part
    )


def test_version_part_null(conf_vs_part):
    assert VersionPart(
        conf_vs_part.first_value, conf_vs_part
    ).null() == VersionPart(conf_vs_part.first_value, conf_vs_part)


def test_labels_for_format():
    assert labels_for_format("{major}.{minor}.{patch}") == [
        "major",
        "minor",
        "patch",
    ]

    assert labels_for_format("{major}.{minor}.{patch}{release}") == [
        "major",
        "minor",
        "patch",
        "release",
    ]
