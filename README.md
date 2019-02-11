# Receipt recognition project
### Goal
To build an application that automatically extracts information from pictures of receipts.
### Current progress
Working on detect regions based on a sample.
### Dependencies
* python3
* cv2 (OpenCV 3.4.4)
* numpy
### Usage
#### Download
```sh
$ git clone https://github.com/nv-quan/receipt-recognition.git
$ cd receipt-recognition
```
#### Config
In ./src/config.json, 
- `input file`: directory of input picture
- `input mode`: `single` to process one file at a time, `folder` to process all file in one folder
- `input folder`: directory of input folder if `input mode` is `folder`
- `run mode`: `normal` for normal mode, `debug` for debug

In ./docsample/sample.json, `sample` is the directory of the sample image
#### Register correct regions
```sh
python3 ./src/register.py
```
Drag in the image to detect sample region, type the ids for them.
#### Run
```
$ python3 ./src/main.py
```
