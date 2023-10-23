# Visual Odometry for Localization in Autonomous Driving

## Overview

This is a Visual Odometry which estimates the vehicle trajectory based on visual data captured by the vehicle monocular camera.

<img src="./doc/pair-imgs-pxls.png" width="600" style="border:0px solid #FFFFFF; padding:1px; margin:1px"> 

The system takes visual data (i.e: images, videos ) as input and performs the following tasks: 
- Extract features from the photographs taken with a camera setup on the vehicle.
- Use the extracted features to find matches between the features in different photographs.
- Use the found matches to estimate the camera motion between subsequent photographs.
- Use the estimated camera motion to build the vehicle trajectory (based on image pair in the dataset)

### Dataset Description : images, images_rbg, depth_maps ... 

The input datas were collected from Carla Simulator.

- [data](self-driving-car-projects\p6-visual-odometry-for-localization\data) folder (600MB)
  - `depth` - 52 data frames
  - `rgb` - 52 data frames

We use the `DatasetHandler()` class defined in the [m2bk module](./m2bk.py), to access and extract datas from the dataset.

```python
dataset_handler = DatasetHandler()
```
We then use the `dataset_handler` to access the specific frame we want.

For example, to access a single image frame and visualize it.

```python
image = dataset_handler.image
plt.imshow(image)
```

To access a single image sample

```python
image = dataset_handler.images[0]
```

Other attributes:

```
- dataset_handler.images : grayscales samples
- dataset_handler.images_rgb : colored imgs
- dataset_handler.depth_maps : depth maps
- dataset_handler.num_frame : number of frames
- dataset_handler.k : Calibration matrix K
```

## Requirements

```sh
pip install -r requirements.txt
```
or if you're on conda

```sh
conda install -r requirements.txt
```

## Usage

You'll need a notebook tool such as a [Google Colab](https://colab.research.google.com/?utm_source=scs-index#scrollTo=5fCEDCU_qrC0) or [Jupyter notebook](https://jupyter.org/) 

Then simply run the notebook each cell sequentially to see the results.

## Final Results

<img src="./doc/vo-trajectory-ouput-0.png" width="800" style="border:0px solid #FFFFFF; padding:1px; margin:1px"> 

## Contributing

Please create a pull request if you want to take this project grow. there are still many stuffs to be added on. Also, do not hesitate to open an issue if you encounter any problem


`@TODO - list`

```
- Split the notebook into python modules
- Package the project into a PyPi package
- Create a C++ version of the model
...
```


