from PIL import Image
import os

image_folder = "outputs/v2"

images = []

files = sorted([
    f for f in os.listdir(image_folder)
    if f.endswith(".png")
])

for file in files:
    images.append(
        Image.open(os.path.join(image_folder, file))
    )

images[0].save(
    os.path.join(image_folder, "projection.gif"),
    save_all=True,
    append_images=images[1:],
    duration=100,
    loop=0
)

print("GIF saved.")