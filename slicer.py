import image_bbox_slicer as ibs

im_src = './data/images/train'
an_src = './data/images/train'
im_dst = './dst/images/train'
an_dst = './dst/images/train'

slicer = ibs.Slicer()
slicer.config_dirs(img_src=im_src, ann_src=an_src,
                   img_dst=im_dst, ann_dst=an_dst)

slicer.slice_bboxes_by_number(number_tiles=4)
slicer.visualize_sliced_random()
