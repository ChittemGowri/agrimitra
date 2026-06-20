# Sample images for demoing AgriMitra

A tiny placeholder image (`test_leaf.jpg`) is included so the app has
something to point to immediately, but for an actual demo/recording
you should replace it with real leaf photos. Two easy ways to get them:

## Option A — use your own phone photos (best, most authentic)
Take 2-3 photos of any plant leaves you have access to (healthy or
diseased) and drop the .jpg/.png files into this folder. Real photos
make for a far more convincing demo than stock images.

## Option B — download a few from the public PlantVillage dataset
This is the standard open dataset used for plant disease research and
is safe to use for a non-commercial student capstone demo:
https://www.kaggle.com/datasets/emmarex/plantdisease

Download a handful of images (e.g. a few "Tomato_Early_blight" and a
few "Tomato_healthy" examples) and place them here. Suggested files
to grab for the demo script in docs/DEMO_SCRIPT.md:
- one clearly diseased tomato leaf
- one healthy tomato leaf
- one groundnut or mango leaf if available

## Naming convention used in this repo
- `test_leaf.jpg` — tiny placeholder (already included, safe to delete)
- Add your own as `tomato_diseased_01.jpg`, `tomato_healthy_01.jpg`, etc.

None of these are required for the app to run -- the Streamlit file
uploader lets you pick any image from anywhere on your machine at
demo time. This folder just keeps a few handy ones in the repo so the
project is self-contained and a judge cloning the repo has something
to test with immediately.
