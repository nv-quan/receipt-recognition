# Receipt recognition project
### Goal
To build an application that automatically extracts information from pictures of receipts.
### Current progress
Working on preprocessing images. The progress is reported [here](https://github.com/nv-quan/receipt-recognition/blob/report/report.md) (in Vietnamese).
### Dependencies
* python3
* cv2 (OpenCV 3.4.4)
* numpy
### Usage
0. Download
```sh
$ git clone https://github.com/nv-quan/receipt-recognition.git
$ cd receipt-recognition
```
1. Config
In ./src/config.json, 
- `input file`: directory of input picture
- `input mode`: `single` for to process file at a time, `folder` for process all file in one folder
- `input folder`: directory of input folder if `input mode` is `folder`
- `run mode`: `normal` for normal mode, `debug` for debug
In ./docsample/sample.json, change `sample` to the directory of the sample image
2. Regisger correct regions
```sh
python3 ./src/register.py
```
Drag in the image to detect sample region, type the ids for them.
3. Run
```
$ python3 ./src/main.py
```
