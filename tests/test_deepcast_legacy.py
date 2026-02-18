from typeable import declare, typecast

Integer = int


def test_declare():
    with declare("Integer") as Ref:
        T = list[Ref]

    assert typecast(T, [2]) == [2]
    assert typecast(T, ["2"]) == [2]
