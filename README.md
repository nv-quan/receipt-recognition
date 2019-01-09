# Receipt recognition project
### Goal
To build an application that automatically extracts information from pictures of receipts.
### Current progress
Working on preprocessing images. The progress is reported [here](https://github.com/nv-quan/receipt-recognition/blob/master/report.md) (in Vietnamese).
### Dependencies
* python3
* cv2 (OpenCV 3.4.4)
* numpy
### Usage
```sh
$ git clone https://github.com/nv-quan/receipt-recognition.git
$ cd receipt-recognition
$ python3 ./src/main.py [input picture] [output file name]
```
For example:
```python3 ./src/main.py ./data/011.jpg 011
```
Change `debug` in ./src/preprocess.py to `True` to see all the middle steps.\
Ouputs are stored in ./output folder
