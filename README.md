# TQEC Optimizer
本プログラムは, 任意の量子回路からTQEC回路生成し, その自動最適化を行うプログラムである.

## Requirements
* g++ 6.3 or later
* CMake 3.2 or later
* Python 3.0 or later
* etc...

## How to build
```
$ cd build
$ cmake ..
$ make
```

## Usage
任意の量子回路が表現されたJSONファイルを入力として, 
tqec_viewerの入力フォーマットであるJSONファイルが出力される.
```
$ python main.py -f [file.json]
```

## Directory hierarchy
```
tqec_optimizer/
├── README.md
└── main.py
```