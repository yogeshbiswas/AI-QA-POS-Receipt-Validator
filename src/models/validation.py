from pydantic import BaseModel


from pydantic import BaseModel


class PairValidationResult(BaseModel):
    is_match: bool
    message: str


class ValidationResult(BaseModel):
    rule_name: str
    status: str
    message: str
    expected: str | None = None
    actual: str | None = None