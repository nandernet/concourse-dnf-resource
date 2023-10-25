import pytest


def test_import():
    import concourse_dnf.cli  # noqa: F401


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (["foo", "bar"], [{"ref": "foo"}, {"ref": "bar"}]),
    ],
)
def test_ref_wrap(n, expected):
    from concourse_dnf.cli import ref_wrap

    assert ref_wrap(n) == expected
