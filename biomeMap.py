import leveldb
import struct
from biome_colors import BIOME_COLORS
from PIL import Image

# =========================================
# CONFIG
# =========================================

DB_PATH = "DB/PATH"
OUTPUT = "mapa_bioma_surface.png"

db = leveldb.LevelDB(DB_PATH)

# =========================================
# STORAGE
# =========================================

heightmaps = {}
biome_maps = {}

min_x = 999999
max_x = -999999

min_z = 999999
max_z = -999999

# =========================================
# BIOME DECODER
# =========================================

def decode_biome_storage(data):

    p = 0
    biome_subchunks = []

    while p < len(data):

        flags = data[p]
        p += 1

        bits_per_block = flags >> 1

        # special palette copy
        if bits_per_block == 127:
            biome_subchunks.append(None)
            continue

        # biome ids
        if bits_per_block == 0:

            biome_id = struct.unpack(
                "<I",
                data[p:p+4]
            )[0]

            p += 4

            biome_subchunks.append(
                [biome_id] * 4096
            )

            continue

        blocks_per_word = 32 // bits_per_block

        word_count = (
            4096 + blocks_per_word - 1
        ) // blocks_per_word

        mask = (1 << bits_per_block) - 1

        palette_ids = []

        for _ in range(word_count):

            temp = struct.unpack(
                "<I",
                data[p:p+4]
            )[0]

            p += 4

            for _ in range(blocks_per_word):

                if len(palette_ids) >= 4096:
                    break

                palette_ids.append(temp & mask)

                temp >>= bits_per_block

        palette_size = struct.unpack(
            "<I",
            data[p:p+4]
        )[0]

        p += 4

        palette = []

        for _ in range(palette_size):

            biome_id = struct.unpack(
                "<I",
                data[p:p+4]
            )[0]

            p += 4

            palette.append(biome_id)

        blocks = []

        for idx in palette_ids:

            if idx >= len(palette):
                blocks.append(0)
            else:
                blocks.append(palette[idx])

        biome_subchunks.append(blocks)

    return biome_subchunks

# =========================================
# LOAD DATA3D
# =========================================

print("Loading Data3D...")

for key, value in db.iterate():

    if len(key) != 9:
        continue

    # tag 43
    if key[8] != 0x2b:
        continue

    try:

        cx = struct.unpack("<i", key[0:4])[0]
        cz = struct.unpack("<i", key[4:8])[0]

        heights = struct.unpack(
            "<256h",
            value[:512]
        )

        biome_data = value[512:]

        biome_subchunks = decode_biome_storage(
            biome_data
        )

        heightmaps[(cx, cz)] = heights
        biome_maps[(cx, cz)] = biome_subchunks

        min_x = min(min_x, cx)
        max_x = max(max_x, cx)

        min_z = min(min_z, cz)
        max_z = max(max_z, cz)

    except Exception as e:
        print("Chunk error:", e)

print("Chunks:", len(heightmaps))

# =========================================
# IMAGE
# =========================================

width = (max_x - min_x + 1) * 16
height = (max_z - min_z + 1) * 16

print("Image:", width, height)

img = Image.new("RGB", (width, height))
pixels = img.load()

# =========================================
# RENDER
# =========================================

print("Rendering...")

for (cx, cz), heights in heightmaps.items():

    biome_subchunks = biome_maps.get(
        (cx, cz),
        []
    )

    base_x = (cx - min_x) * 16
    base_z = (cz - min_z) * 16

    for z in range(16):
        for x in range(16):

            idx2d = x + z * 16

            surface_y = heights[idx2d]

            if surface_y < 0:
                surface_y = 0

            if surface_y > 383:
                surface_y = 383

            subchunk_index = surface_y // 16

            local_y = surface_y % 16

            biome_id = 1

            if subchunk_index < len(biome_subchunks):

                sub = biome_subchunks[subchunk_index]

                if sub is not None:

                    idx3d = (
                        local_y * 16 * 16
                    ) + (
                        z * 16
                    ) + x

                    if idx3d < len(sub):
                        biome_id = sub[idx3d]

            biome_color = BIOME_COLORS.get(
                biome_id,
                (255, 0, 255)
            )

            # =====================================
            # SHADING
            # =====================================

            h = surface_y

            if x > 0:
                left_h = heights[
                    (x - 1) + z * 16
                ]
            else:
                left_h = h

            diff = h - left_h

            shade = 128 + diff * 8

            shade = max(40, min(255, shade))

            r, g, b = biome_color

            color = (
                int(r * shade / 128),
                int(g * shade / 128),
                int(b * shade / 128),
            )

            px = base_x + x
            pz = base_z + z

            pixels[px, pz] = color

# =========================================
# SAVE
# =========================================

print("Saving...")

img.save(OUTPUT)

print("DONE")