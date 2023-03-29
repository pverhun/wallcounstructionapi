import typing
from dataclasses import dataclass


@dataclass(slots=True)
class Workload:
    profile: int | None = None
    section: int | None = None
    is_relieve: bool = False
    section_height: int | None = None


class BaseWallConstruction:
    # Define Section
    SectionsHeights = tuple[int]
    WallProfiles = tuple[SectionsHeights]

    # Define constants
    SECTION_HEIGHT = WORKING_DAYS_PER_SECTION = 30
    FOOTS_PER_DAY = 1
    ICE_VOLUME_PER_FOOT = 195
    COST_PER_ICE_VOLUME = 1900

    def workflow_gen(self):
        """As long as our workload can only be in 2 states:
          'Assigned and done' OR 'waiting for assignment'
          and cannot be reassigned we can implement workflow generator"""
        for profile_idx, profile in enumerate(self.wall_profiles):
            for section_idx, section in enumerate(profile):
                if section < self.SECTION_HEIGHT:
                    yield Workload(profile_idx, section_idx, section_height=section)

    def __init__(self, file_input: str | typing.TextIO):
        if type(file_input) == str:
            file_input = open(file_input, "r")

        wall_profiles = tuple(
            tuple(int(section_height) for section_height in profile.split()) for profile in file_input.readlines()
        )
        file_input.close()
        self.wall_profiles = wall_profiles
