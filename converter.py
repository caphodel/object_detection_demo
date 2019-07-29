from PIL import Image  # Python Image Library - Image Processing
import glob
import os
for file in glob.glob("./data/raw/*.*"):
    print(file)
    im = Image.open(file)
    rgb_im = im.convert('RGB')
    rgb_im.save(os.path.splitext(file)[0]+".jpg", quality=95)