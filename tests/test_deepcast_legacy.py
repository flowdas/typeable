from typeable import declare, deepcast


Integer = int


def test_declare():
    with declare("Integer") as Ref:
        T = list[Ref]

    assert deepcast(T, [2]) == [2]
    assert deepcast(T, ["2"]) == [2]
