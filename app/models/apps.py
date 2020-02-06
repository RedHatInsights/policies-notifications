from uuid import UUID

from pydantic import BaseModel


class Base(BaseModel):
    id: str

    class Config:
        orm_mode = True


# Do we want to tie some endpoints for a single app only?
class App(BaseModel):
    name: str
    description: str
    # Do we link app with something? Why do we need it?


class AppOut(App):
    id: UUID

    class Config:
        orm_mode = True
