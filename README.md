# Prediction Editor

This app is created to be able to visualize the result of predictions done with models trained to segment nuclei, cell and lysosome.
If a prediction is wrong the user may edit the label, and obtain new labels to continue train the models and improve them.

**Program is still under construction and some bugs are to be fixed in the drawing window**

Icons used are from https://icons8.com

Buttons were created using https://www.imagefu.com

## Installation

Easiest is to install it via [conda](https://docs.conda.io/en/latest/miniconda.html).

In your terminal type:
```bash
conda env create -f predAppEnv.yml
```
To run the program type:

```bash
python prediction_editor.py
```

If you want to install it without conda, you can find the packages and versions used in predAppEnv.yml

## Usage

In the folder you find 3 example images for each channel (Nuclei, Cell and Lysosome). When you open the program, the folder for nuclei channel is opened as default. You may change the folder. Then you can chose which model to see the prediction from.

![image1](/graphics/1.png)

You can look at the labels that was predicted, brighten the image and look at the boundaries. If you are looking at a lysosome prediction, you will have the option to also see circles around the objects to find them easier. You may zoom on the image by clicking the left mouse button, and zoom out by clicking the right mouse button. Pressing "Edit annotation" will take you to the next window where you can edit the label.
![image2](/graphics/2.png)

![image3](/graphics/3.png)

Here you may edit the label by adding to a label or erasing from it. If two labels are connected, the eraser can be used to separate them. The wand tool will add to an existing label, and the pencil will give the option to create a new label. When the label is approved it can be saved to a default folder by pressing the save button.

![image4](/graphics/4.png)
