from .models import TagGFK, TagExplicit, ProfileA, ProfileB, ProfileC, ProfileD


def serialize_profile_a(profile_a: ProfileA) -> dict:
    return {
        "type": "profile_a",
        "id": profile_a.pk,
        "name": profile_a.name,
        "age": profile_a.age,
    }

def serialize_profile_b(profile_b: ProfileB) -> dict:
    return {
        "type": "profile_b",
        "id": profile_b.pk,
        "name": profile_b.name,
        "email": profile_b.email,
        "extra_info": profile_b.extra_data.info if profile_b.extra_data else None,
    }

def serialize_profile_c(profile_c: ProfileC) -> dict:
    return {
        "type": "profile_c",
        "id": profile_c.pk,
        "name": profile_c.name,
        "address": profile_c.address,
    }

def serialize_profile_d(profile_d: ProfileD) -> dict:
    return {
        "type": "profile_d",
        "id": profile_d.pk,
        "name": profile_d.name,
        "phone": profile_d.phone,
    }

def serialize_tag_gfk(tag: TagGFK) -> dict:
    obj = tag.content_object
    if isinstance(obj, ProfileA):
        return serialize_profile_a(obj)
    elif isinstance(obj, ProfileB):
        return serialize_profile_b(obj)
    elif isinstance(obj, ProfileC):
        return serialize_profile_c(obj)
    elif isinstance(obj, ProfileD):
        return serialize_profile_d(obj)
    else:
        return {
            "type": "unknown",
            "id": tag.pk,
            "content_type": tag.content_type.model,
            "object_id": tag.object_id,
        }

def serialize_tag_explicit(tag: TagExplicit) -> dict:
    if tag.profile_a:
        return serialize_profile_a(tag.profile_a)
    elif tag.profile_b:
        return serialize_profile_b(tag.profile_b)
    elif tag.profile_c:
        return serialize_profile_c(tag.profile_c)
    elif tag.profile_d:
        return serialize_profile_d(tag.profile_d)
    else:
        return {
            "type": "empty",
            "id": tag.pk,
            "profile_a": None,
            "profile_b": None,
            "profile_c": None,
            "profile_d": None,
        }
