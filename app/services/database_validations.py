def exists_by_field(model, field_name: str, value) -> bool:
    return model.query.filter(getattr(model, field_name) == value).first() is not None

def exists_by_two_fields(model, field_1: str, value_1, field_2: str, value_2) -> bool:
    return model.query.filter(
        getattr(model, field_1) == value_1,
        getattr(model, field_2) == value_2
    ).first() is not None