from .._typecast import DeepCast, deepcast


@deepcast.register
def object_from_object(
    deepcast: DeepCast, cls: type[object], val: object, *Ts: type
) -> object:
    # 메타클래스를 사용하지 않는 타입에 대해 적용되는 폴백 캐스터.
    # 타입 시스템으로 캐스터를 매핑할 수 없는 타입들을 다룬다.
    return deepcast.apply(cls[Ts] if Ts else cls, val)
