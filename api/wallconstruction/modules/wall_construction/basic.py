"""
WallConstruction Base Class and basic sync implementation

"""
from .base import BaseWallConstruction


class WallConstruction(BaseWallConstruction):

    def get_profile_ice_volume(self,
                               sections: BaseWallConstruction.SectionsHeights,
                               day: int | None = None,
                               accumulate: bool = False) -> int:
        total_ice_volume = 0

        if not day:
            workload_per_profile = 0
            for section_height in sections:
                workload_per_profile += self.SECTION_HEIGHT - section_height

            total_ice_volume = workload_per_profile * self.ICE_VOLUME_PER_FOOT
        else:
            working_days_per_section = [self.WORKING_DAYS_PER_SECTION - worked_days for worked_days in sections]

            for working_days in working_days_per_section:
                if day <= working_days:
                    if accumulate:
                        total_ice_volume += day * self.ICE_VOLUME_PER_FOOT
                    else:
                        total_ice_volume += self.ICE_VOLUME_PER_FOOT

        return total_ice_volume

    def get_wall_costs(self,
                       profile_no: int | None = None,
                       day: int | None = None,
                       accumulate: bool | None = False) -> (int, int):

        total_ice_volume = 0

        if profile_no is not None:
            profile = self.wall_profiles[profile_no - 1]
            total_ice_volume = self.get_profile_ice_volume(profile, day, accumulate)
        else:
            for profile in self.wall_profiles:
                total_ice_volume += self.get_profile_ice_volume(profile, day, accumulate)

        return total_ice_volume, total_ice_volume * self.COST_PER_ICE_VOLUME
