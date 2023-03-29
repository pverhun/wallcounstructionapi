from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings


def get_wall_construction(query_params: dict, input_file: str = ''):
    """ Create Wall Construction class based on specified VERSION_PARAM and return it
        :arg query_params: Request query param dict.
        :arg input_file: Input data file path.
    """
    v = query_params.get(settings.VERSION_PARAM)

    path = f'{settings.INPUTS_BASE_DIRECTORY}/input.txt'

    if v == settings.MT:
        from .modules.wall_construction.mt import WallConstructionMt as WallConstruction
        path = f'{settings.MT_INPUTS_BASE_DIRECTORY}/input.txt'
    elif v == settings.MT_VER2:
        from .modules.wall_construction.mt2 import WallConstructionMt2 as WallConstruction
        path = f'{settings.MT_INPUTS_BASE_DIRECTORY}/input.txt'
    else:
        # If no v param load default sync implementation
        from .modules.wall_construction.basic import WallConstruction

    return WallConstruction(file_input=input_file or path)


@api_view()
def daily(request, wall_profile=None, day=None):
    wall_construction = get_wall_construction(request.query_params)
    ice_amount, _ = wall_construction.get_wall_costs(wall_profile, day)

    return Response({
        "day": str(day),
        "ice_amount": "{:,}".format(ice_amount)
    })


@api_view()
def overview(request, wall_profile=None, day=None):
    wall_construction = get_wall_construction(request.query_params)

    _, cost = wall_construction.get_wall_costs(wall_profile, day, accumulate=True)

    return Response({
        "day": str(day),
        "cost": "{:,}".format(cost)
    })
