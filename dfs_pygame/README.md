# 8-Puzzle DFS Pygame

Game 8-puzzle don gian bang Pygame, dung Depth First Search de tim duong di tu trang thai hien tai ve dich.

## Chay trong VS Code

```bash
cd dfs_pygame
python -m pip install -r requirements.txt
python main.py
```

## Chuc nang

- Bam `Xao` de tao trang thai bat dau.
- Bam `DFS` de tim duong di bang DFS co gioi han do sau.
- Xem trang thai DFS dang tham, so node da mo, kich thuoc stack va depth hien tai.
- Bam `Buoc <`, `Buoc >`, `Chay`, `Dung`, `Ve dau` de xem lai duong di.
- Bam `Depth -/+` de doi gioi han do sau neu DFS chua tim thay.
- Bam `Toc -/+` de doi toc do tim va toc do playback.
- Co the click vao o ke ben o trong de tu choi bang tay.

## Phan DFS nam o dau?

Trong `main.py`, class `DFSSearcher` la phan thuat toan DFS:

- `stack` luu bien can mo.
- `parent` luu cha cua moi trang thai de dung lai duong di.
- `best_depth` tranh lap trang thai o depth kem hon.
- `step()` mo tung trang thai de Pygame co the hien truc quan qua tung frame.
