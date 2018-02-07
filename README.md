# TQEC Optimizer
本プログラムは, 任意の量子回路からTQEC回路生成し, その自動最適化を行うプログラムである.

## Requirements
* Python 3.0 or later
* etc...

## Usage
任意の量子回路が表現されたJSONファイルを入力として, 
tqec_viewerの入力フォーマットであるJSONファイルが出力される.
```
$ python main.py -i [file.json] -o [file.json] -t [primal or dual]
```
既存手法を実行するには以下のコマンド
```
$ python main.py -bp -i [file.json] -o [file.json]
```
## Project layout
```
.
├── data                # テスト用回路データ
└── tqec_optimizer      
    ├── braidpack       # 既存手法 Braidpack
    ├── relocation      # Reducing Loops 
    └── transformation  # 提案手法
```