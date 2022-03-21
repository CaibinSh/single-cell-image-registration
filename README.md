# single-cell-image-registration

This is designed to do image registration for multiple channel images for live-cell microscopy experiments. The ‘test.py’ and example images will show you the robustness of this algorithm.

# testing

folders 'calibrated' and 'calibrate3' with cropped images should appear in mydir

```sh
>>> import imgreg
>>> mydir = 'imgreg/example/'
>>> total_time_point = 2;
>>> Posperplate = 1;
>>> total_position = 2
>>> imgreg.align(mydir,total_time_point,Posperplate,total_position)
```