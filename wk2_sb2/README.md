# I’ll be Needin’ Stitches

## Usage
Look at `test_stitch_custom.py` for usage examples. Here is the `jigsaw` API:

# API

## `jigsaw.Image`
A wrapper around a `cv2`/`np` array image representation, with tons of cached computations for OTF image stitching.

| Attr/Method | Usage |
| - | - |
| `mat` | The original image |
| `size` | The original image's size, in WxH |
| `kp` | The key feature points discovered in the original image's coordinates |
| `des` | The feature descriptors matching `kp` |
| `T` | The image→world transform |
| `world_mat` | The image, transformed to world coordinates (without the translation to reduce memory usage) |
| `world_corner` | The corner (min x/y) of the transformed image |
| `world_size` | The size of the transformed image |
| `depopulate_world()` | As scary as this sounds, this just clears the `world_*` attributes to uncache them |
| `populate_world()` | Recreate the `world_*` attributes. Safe to call multiple times, as only the first will have performance overhead |

## `jigsaw.Match`
Just a data container for a single match. See `jigsaw.Mapper`.

| Attr/Method | Usage |
| - | - |
| `kp_a` | `cv2.KeyPoint` for image A |
| `kp_b` | `cv2.KeyPoint` for image B |
| `match` | `cv2.DMatch` result |

## `jigsaw.Matches`
Just a data container for matches. See `jigsaw.Mapper`.

| Attr/Method | Usage |
| - | - |
| `img_a` | `Image` A |
| `img_b` | `Image` B |
| `matches` | A list of `Match`es |

## `jigsaw.Mapper`
A mapper class that handles feature detection, matching, and transformation.

| Attr/Method | Usage |
| - | - |
| `orb` | `cv2`'s ORB feature detector |
| `matcher` | `cv2`'s feature matcher |
| `lowe_ratio` | A ratio for feature filtering which ensures only "good" feature matches are preserved. Each match is compared to its next best, and if the distance is this much of a factor lower compared to next best, then it is kept since it is distinct. Otherwise, it is too similar to be considered usable |
| `min_n_feats` | Minimum number of features/matches for RANSAC to actually apply (soft limit, technically it can work with just one) |
| `min_score` | Score for RANSAC is defined as $\frac{n_{inlier}}{n_{all}}$ where $n$ is the number of matches. This is a soft filter for scores |
| `min_scale` | Minimum scale to prevent bogus RANSAC results from placing an image into just a very small section of another, since we expect continuous, similar images |
| `max_scale` | Maximum scale to prevent bogus RANSAC results from allocating a huge amount of memory due to huge scales, since we expect continuous, similar images |
| `detect(img)` | Populates `kp` and `des` of an `Image` |
| `match(img_a, img_b)` | Matches image B onto A. Does Lowe ratio filtering. If `detect()` was not called on these images, it will be called |
| `transform_b_onto_a(matches)` | Expects results from `match()`, returns transformation ($T$) and score or `None` if rejected |
| `apply_b_onto_a(img_a, img_b, *, T_cache)` | Applies the transformation from `transform_b_onto_a()` onto image B. If `T_cache` isn't provided, it is computed directly. Otherwise, it just does a dummy transform application and depopulates B. Returns `None` if rejected |

## `jigsaw.Map`
A map class that requires a `Mapper` to handle the full lifecycle of image stitching and adding. Functions via grid to prevent memory over/reallocation.

| Attr/Method | Usage |
| - | - |
| `add_chunk(cx, cy)` | Attempts to create a chunk of zero-ed pixels. Returns that created(?) chunk |
| `add_chunks(corner, size)` | Fills in chunks in a certain pixel range. Returns all the chunks covered |
| `add_image_to(img, chunk_pos)` | Adds an image to a chunk, automatically performing slicing and checking to fit that image directly in. Does not perform any sort of merging algorithm between overlap images |
| `add_image(img)` | Adds an already-transformed image to the map, into the correct chunks |
| `map_and_add_image(img)` | Adds an image to the map by checking with existing images for the best transformation/fit, then computing that before adding it to the map. Will return a boolean describing success (`True` means successful) |
| `combine()` | Create a huge image (ready for saving) of the whole map |
