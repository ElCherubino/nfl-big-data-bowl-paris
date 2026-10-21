"""Versioned, predeclared calculation settings shared by the pipeline."""
import math

SCHEMA_VERSION = "1.0.0"
CALCULATION_VERSION = "1.0.0"
DEFAULT_PARAMETERS = {
    "pressureRadiusYd": 2.0,
    "openDistanceYd": 2.5,
    "maxQbDistanceYd": 15.0,
    "minLosProgressYd": -1.0,
    "maxFacingAngleDeg": 90.0,
    "includeFb": True,
    "minSeasonN": 20,
    "shrinkageK": 20,
    "bootstrapReplicates": 2000,
    "randomSeed": 20261021,
}


def merged_parameters(parameters=None):
    result = {**DEFAULT_PARAMETERS, **(parameters or {})}
    for key in ("pressureRadiusYd", "openDistanceYd", "maxQbDistanceYd"):
        if type(result[key]) not in (int, float) or not math.isfinite(result[key]) or result[key] <= 0:
            raise ValueError(f"{key} must be positive")
    for key in ("minSeasonN", "bootstrapReplicates"):
        if type(result[key]) is not int or result[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if type(result['randomSeed']) is not int or result['randomSeed'] < 0:
        raise ValueError('randomSeed must be a nonnegative integer')
    if type(result['includeFb']) is not bool:
        raise ValueError('includeFb must be boolean')
    if type(result['shrinkageK']) not in (int, float) or not math.isfinite(result['shrinkageK']) or result['shrinkageK'] < 0:
        raise ValueError('shrinkageK must be finite and nonnegative')
    angle = result['maxFacingAngleDeg']
    if angle is not None and (type(angle) not in (int, float) or not math.isfinite(angle) or not 0 < angle <= 180):
        raise ValueError('maxFacingAngleDeg must be in (0, 180], or null to disable')
    if type(result['minLosProgressYd']) not in (int, float) or not math.isfinite(result['minLosProgressYd']):
        raise ValueError('minLosProgressYd must be finite')
    return result
