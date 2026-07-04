from dataclasses import dataclass


@dataclass(slots=True)
class Task:

    id: int | None
    title: str
    remind_at: str
    repeat_type: str
    enabled: bool
    created_at: str
    updated_at: str
