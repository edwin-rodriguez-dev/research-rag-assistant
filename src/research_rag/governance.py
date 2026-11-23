from research_rag.models import ROLES

def normalize_role(role: str) -> str:
    value = role.strip().upper()
    if value not in ROLES:
        raise ValueError(f"Unknown role {role}; expected one of {ROLES}")
    return value

def may_access(role: str, allowed_roles: list[str]) -> bool:
    normalized = normalize_role(role)
    return normalized == "ADMIN" or normalized in {
        value.upper() for value in allowed_roles
    }
