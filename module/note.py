from enum import Enum, unique

from nextcord import Interaction


@unique
class NoteState(Enum):
    UNBEGUN = 30
    STALLED = 31
    ONGOING = 32
    FINISHED = 33


class Note(object):
    def __init__(self, title, content, uuid, notes, state, data) -> None:
        self.title = title
        self.content = content
        self.uuid = uuid
        self.notes = notes
        self.state = state
        self.data = data

    async def update(self):
        return


class NoteContainer:
    def __init__(self, interaction: Interaction, note: Note) -> None:
        self.note = note

    async def update(self):
        pass
