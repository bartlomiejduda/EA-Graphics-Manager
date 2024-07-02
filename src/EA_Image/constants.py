# EA Image constants

# fmt: off
PALETTE_TYPES = (33, 34, 35, 36, 41, 42, 44, 45, 46, 47, 48, 49, 50, 58, 59)
CONVERT_IMAGES_SUPPORTED_TYPES = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 20, 22, 24, 25, 30, 33, 34, 35, 59, 64,
                                  65, 66, 67, 88, 89, 90, 91, 92, 93, 96, 97, 98, 104, 109, 115, 119, 120, 121, 123,
                                  125, 126, 127, 130, 131, 192, 193, 194, 237, 248, 251]

IMPORT_IMAGES_SUPPORTED_TYPES = [5, ]

OLD_SHAPE_ALLOWED_SIGNATURES = (
    "SHPI",  # PC games
    "SHPP",  # PS1 games
    "SHPS",  # PS2 games
    "SHPX",  # XBOX games
    "SHPM",  # PSP games
    "SHPG",  # WII/Gamecube games
    "SHPA",  # Game Boy Advance games
)

NEW_SHAPE_ALLOWED_SIGNATURES = (
    "ShpF",  # PC games
    "ShpS",  # PS2 games
    "ShpX",  # XBOX games
    "ShpM",  # PSP games
    "ShpG",  # WII/Gamecube games
    "ShpA",  # Game Boy Advance games
)
# fmt: on
