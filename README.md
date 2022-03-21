# single-cell-image-registration

This is designed to perform image registration for multiple channel images for live-cell microscopy experiments. Live-cell images show a significant shift over time due to many factors (e.g.  imperfect relocation of microscopy focus and evaporation of medium), this brings difficulty for cell tracking, given that cells are also moving. This tool allows maximization of image alighment over time and thus increases number of cells being tracked.

The ‘test.py’ and example images will show you the robustness of this algorithm. This work was done during my PhD at Prof. Alexander Loewer's lab, see details in [paper](https://doi.org/10.1016/j.celrep.2019.03.031).

# testing

Clone this repository,

```sh
$ git clone https://github.com/CaibinSh/single-cell-image-registration.git
```

Folders 'calibrated' and 'calibrate3' with cropped images should appear in folder example/mov1

```sh
>>> import imgreg
>>> mydir = 'example/'
>>> total_time_point = 2
>>> Posperplate = 1
>>> total_position = 2
>>> imgreg.align(mydir,total_time_point,Posperplate,total_position)
```