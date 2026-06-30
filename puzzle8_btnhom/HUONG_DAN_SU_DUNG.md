# Bao Cao 8-Puzzle Search Visualizer

Day la tai lieu mo ta tong quan va giai thich cac thuat toan trong chuong trinh 8-Puzzle Search Visualizer.
No duoc viet theo dang bao cao de de theo doi, bao gom phan tich PEAS, mo hinh hoa bai toan va giai thich tung
thuat toan duoc hien thi trong giao dien.

## 1. Muc tieu

Chuong trinh mo phong bai toan 8-puzzle va cho phep nguoi dung:

- chinh sua `START` va `GOAL`
- chay tung buoc hoac chay tu dong
- xem trang thai cua frontier, children, search tree va ket qua
- so sanh nhieu thuat toan tim kiem khac nhau
- thu nghiem cac che do mo phong dac biet nhu Hidden Tiles, Blind Mode, No Start/Goal va Local Search

Muc tieu chinh la giup nguoi dung hieu ro:

- cach mo ta bai toan trong AI
- cach cac thuat toan tim kiem lam viec
- diem manh va han che cua tung thuat toan
- vi sao mot so thuat toan tim duoc loi giai nhanh, con mot so thuat toan de bi ket

## 2. Cach chay chuong trinh

```bash
pip install pygame
python main.py
```

Neu dang o thu muc cha:

```bash
cd puzzle8_btnhom
python main.py
```

## 3. Mo hinh bai toan 8-Puzzle

Bai toan 8-puzzle gom:

- 1 bang 3x3
- 8 mieng ghep mang so `1..8`
- 1 o trong ky hieu boi so `0`

Nguoi choi hoac thuat toan can dua bang tu trang thai bat dau ve trang thai muc tieu bang cach di chuyen o trong.
Moi buoc di la hoan vi giua o trong va mot o ke ben hop le.

### 3.1 Khong gian trang thai

Moi trang thai duoc mo ta bang mot tuple gom 9 phan tu.
Vi du:

```text
(1, 2, 3,
 4, 0, 6,
 7, 5, 8)
```

### 3.2 Hanh dong

Hanh dong hop le cua o trong:

- UP
- DOWN
- LEFT
- RIGHT

Chi nhung huong nao khong vuot bien moi la hop le.

### 3.3 Ham muc tieu

Thu thuat toan tim xem trang thai hien tai co trung voi `GOAL` hay khong.
Neu trung khop, bai toan duoc xem la da giai xong.

### 3.4 Ham chi phi

Voi nhieu thuat toan, moi buoc di co chi phi `1`.
Tong chi phi duong di thuong duoc ky hieu la `g(n)`.

### 3.5 Heuristic

Chuong trinh dung heuristic Manhattan:

- moi mieng ghep tinh khoang cach hang + cot tu vi tri hien tai den vi tri trong goal
- tong tat ca khoang cach cua cac mieng ghep la `h(n)`

Heuristic nay rat pho bien vi don gian, de tinh va phu hop voi 8-puzzle.

## 4. Phan tich PEAS

PEAS la khung mo ta mot tac nhan thong minh:

- `P` - Performance measure
- `E` - Environment
- `A` - Actuators
- `S` - Sensors

### 4.1 Performance measure

Day la cac tieu chi danh gia chat luong cua tac nhan:

- tim duoc loi giai hay khong
- loi giai co ngan hay khong
- so nut da mo rong (`expanded`)
- so nut da sinh ra (`generated`)
- thoi gian chay
- bo nho su dung
- do on dinh cua ket qua
- tinh toan ven va tinh toi uu

Voi 8-puzzle, thuat toan tot thuong la thuat toan:

- giai duoc nhieu truong hop
- tim loi giai ngan
- khong ton qua nhieu bo nho

### 4.2 Environment

Moi truong cua tac nhan la:

- bang 3x3
- cac o so 1..8 va o trong
- trang thai bat dau va trang thai dich
- tap nuoc di hop le cua o trong
- rang buoc tinh hop le cua bang
- tinh chia het parity de biet bai toan co giai duoc hay khong

Trong giao dien hien tai, moi truong con bao gom:

- cac tab thuat toan
- cac nut dieu khien
- popup modes
- cac panel thong tin

### 4.3 Actuators

Tac nhan co the tac dong len moi truong bang:

- di chuyen o trong len/xuong/trai/phai
- chon nut `Next Step`
- chon `Auto Run`
- chon `Reset`
- chon `Solve Full`
- chon tab thuat toan
- chon mode trong popup
- chinh sua START/GOAL bang ban phim

Noi cach khac, actuators trong chuong trinh la cac hanh dong dieu khien trang thai thuat toan va trang thai giao dien.

### 4.4 Sensors

Tac nhan lay thong tin tu moi truong qua:

- trang thai `START`
- trang thai `GOAL`
- trang thai hien tai cua thuat toan
- danh sach nuoc di hop le
- frontier hien tai
- cac child vua sinh
- path hien tai
- parity solvable/unsolvable
- cac thong so thong ke nhu step, expanded, generated
- trang thai cua popup mode va toolbar

### 4.5 Ket luan PEAS

Neu viet gon:

- `P`: giai duoc, nhanh, ngan, it ton bo nho
- `E`: 8-puzzle 3x3 co o trong va cac rang buoc di chuyen
- `A`: di chuyen o trong, chon nut dieu khien, cap nhat bang
- `S`: doc START, GOAL, current state, frontier, heuristic, parity

## 5. Mo hinh hoa bai toan

Bai toan duoc mo hinh theo 5 thanh phan:

1. `State space`: toan bo trang thai hop le cua 8-puzzle
2. `Initial state`: trang thai bat dau
3. `Actions`: cac nuoc di hop le cua o trong
4. `Transition model`: hoan vi o trong voi o ke ben
5. `Goal test`: kiem tra trang thai co bang goal hay khong

Voi nhieu thuat toan tim kiem, ta con can:

- `g(n)`: chi phi da di
- `h(n)`: uoc luong chi phi con lai
- `f(n) = g(n) + h(n)`: ham danh gia

## 6. Cac thuat toan tim kiem

## 6.1 BFS - Breadth-First Search

### Y tuong

BFS mo rong cac nut theo tung tang mot, dung hang doi FIFO.
Nut duoc sinh truoc se duoc xu ly truoc.

### Cach chay trong chuong trinh

Chuong trinh co 2 cach kiem tra goal:

- Mode 1: kiem tra goal ngay khi sinh child
- Mode 2: kiem tra goal khi dequeue ra khoi queue

### Uu diem

- tim duoc loi giai ngan nhat neu moi buoc co cung chi phi
- don gian de hieu
- co tinh hoan chinh

### Nhuoc diem

- ton rat nhieu bo nho
- frontier co the tang nhanh
- khong phu hop neu khong gian trang thai qua lon

### Khi nao nen dung

- khi can loi giai ngan nhat
- khi khong qua lo ve bo nho

## 6.2 DFS - Depth-First Search

### Y tuong

DFS di sau toi da co the roi moi lui lai.
No dung stack LIFO.

### Cach chay

Nut moi sinh ra duoc day len dinh stack.
Nut vua vao sau se duoc xu ly truoc.

### Uu diem

- dung it bo nho hon BFS
- co the tim ra loi giai nhanh neu may man di dung nhanh

### Nhuoc diem

- khong dam bao tim ra loi giai ngan nhat
- de mac ket neu nhanh di sai
- co the di qua nhieu nhanh khong can thiet

### Dac diem

DFS phu hop de minh hoa:

- tinh chat stack
- xu huong di sau
- nguy co lap vo han neu khong quan ly cycle tot

## 6.3 DFS L - Depth-Limited DFS

### Y tuong

Day la DFS nhung chi cho phep mo rong toi mot do sau toi da.

### Muc dich

- tranh DFS di qua sau va treo lau
- tao co hoi kiem soat do phuc tap

### Uu diem

- an toan hon DFS thuong
- giam nguy co di sai qua sau

### Nhuoc diem

- neu gioi han qua nho thi co the bo sot loi giai
- van khong dam bao toi uu

## 6.4 A* Search

### Y tuong

A* su dung:

```text
f(n) = g(n) + h(n)
```

Trong do:

- `g(n)` la chi phi da di
- `h(n)` la chi phi uoc luong con lai

### Noi dung trong chuong trinh

Chuogn trinh dung Manhattan distance lam heuristic.
Thu tu mo rong nut duoc quyet dinh boi heap/priority queue.

### Uu diem

- neu heuristic tot va dam bao tinh thich hop, A* co the tim duoc loi giai toi uu
- hieu qua hon BFS trong nhieu truong hop

### Nhuoc diem

- ton bo nho hon nhieu thuat toan keo sap xep
- phu thuoc vao chat luong heuristic

### Khi nao nen dung

- khi can tinh toi uu
- khi co heuristic tot

## 6.5 Greedy Best-First Search

### Y tuong

Greedy chi nhin vao `h(n)`.
No luon chon trang thai co heuristic nho nhat ma khong quan tam chi phi da di.

### Cong thuc

```text
f(n) = h(n)
```

### Uu diem

- chay nhanh
- thuong di sat muc tieu hon trong giai doan dau

### Nhuoc diem

- khong dam bao toi uu
- de bi "tham" va bi lap huong
- co the di vao duong xau roi kho thoat

### Khac gi A*

- A* can bang giua da di va con lai
- Greedy chi quan tam cai truoc mat

## 6.6 Manhattan A*

Trong giao dien, mode nay nhan manh ro hon vai tro cua heuristic Manhattan.
Ve ban chat, no van la A* voi:

- `g(n)`: so buoc da di
- `h(n)`: tong khoang cach Manhattan

### Y nghia

Mode nay giup nguoi dung thay ro:

- cach heuristic danh gia do gan goal
- su ket hop giua chi phi da di va uoc luong con lai

## 6.7 IDS - Iterative Deepening Search

### Y tuong

IDS la ket hop giua:

- DFS
- va viec tang dan depth limit

No lap lai DFS nhieu lan voi do sau:

- 1
- 2
- 3
- ...

### Uu diem

- dung it bo nho hon BFS
- van dam bao tim ra loi giai ngan nhat neu co

### Nhuoc diem

- lap lai nhieu lan
- co the mo rong nhieu nut trung lap

### Y nghia su phoi hop

IDS rat hay trong bai toan tim kiem vi:

- bo nho thap
- van giu duoc tinh chat tim loi giai ngan nhat

## 6.8 Hill Climbing - First Improvement

### Y tuong

Thuat toan nhin vao cac trang thai ke ben.
Neu gap mot trang thai co heuristic tot hon trang thai hien tai, no di ngay.

### Dac diem

- dung heuristic Manhattan
- chi can thay trang thai dau tien tot hon la chon
- rat nhanh

### Uu diem

- don gian
- toc do cao
- phu hop de minh hoa local search

### Nhuoc diem

- de bi ket o cuc tri cuc bo
- khong dam bao tim ra loi giai

## 6.9 Steepest-Ascent Hill Climbing

### Y tuong

Khac voi first-improvement, thuat toan nay xet tat ca lang gieng hop le roi chon trang thai co heuristic tot nhat.

### Uu diem

- lua chon co chu y hon first-improvement
- thuong cho buoc di "tot nhat" trong so cac lang gieng hien tai

### Nhuoc diem

- van co the ket o cuc tri cuc bo
- ton cong hon first-improvement vi phai xet nhieu lang gieng

### So sanh voi first-improvement

- First-improvement: thay gi tot la di ngay
- Steepest-ascent: xet het roi moi chon cai tot nhat

## 6.10 Stochastic Hill Climbing

### Y tuong

Thu thuat toan chon ngau nhien mot lang gieng co heuristic tot hon.

### Uu diem

- co tinh ngau nhien nen doi khi thoat duoc duong di xau
- thuong linh hoat hon first-improvement

### Nhuoc diem

- ket qua khong on dinh
- van co the bi ket

## 6.11 Random-Restart Hill Climbing

### Y tuong

Neu bi ket o cuc tri cuc bo, thuat toan se:

1. restart lai tu mot trang thai moi
2. tiep tuc hill climbing
3. lap lai nhieu lan

### Y nghia

Day la ky thuat khac phuc mot phan van de cuc tri cuc bo cua hill climbing.

### Uu diem

- co co hoi vuot qua cac diem ket
- thuc te hon hill climbing don thuan

### Nhuoc diem

- van khong dam bao thanh cong
- mat them thoi gian cho cac lan restart

## 6.12 Local Beam Search

### Y tuong

Local Beam giu lai nhieu trang thai tot nhat cung luc thay vi chi giu 1 trang thai.

### Quy trinh

1. sinh cac lang gieng tu tap trang thai hien tai
2. danh gia heuristic
3. giu lai `k` trang thai tot nhat
4. lap lai

### Uu diem

- giam nguy co ket sat hon so voi hill climbing don
- duyet duoc nhieu huong song song

### Nhuoc diem

- van co the mat huong neu tap beam khong du manh
- ton bo nho hon hill climbing don

## 6.13 Simulated Local Search Mode

Che do nay trong giao dien la mot phien ban mo phong local search co huong dan boi heuristic.
Trong app hien tai, no duoc hien thi theo kieu:

- lap duong di noi bo
- replay tung nuoc di
- cho nguoi dung thay rong qua trinh di chuyen

### Y nghia

Che do nay khong chi de tim loi giai, ma con de:

- quan sat ban chat local search
- xem heuristic dan duong nhu the nao
- nhin ro tung buoc di cua o trong

## 7. Cac che do popup dac biet

### 7.1 Hidden Tiles Mode

Mot so mieng ghep se bi an tren UI.
Muc dich:

- mo phong tinh huong thong tin visual bi thieu
- van cho AI giai dua tren trang thai noi bo

### 7.2 Blind Mode

START va GOAL khong hien tren UI.
Muc dich:

- mo phong tac nhan "khong thay ro" trang thai dau va dich
- van phai lap ke hoach ben trong de giai

### 7.3 No Start/Goal Mode

Chuong trinh tu sinh START va GOAL hop le ben trong.
Muc dich:

- mo phong tinh huong khong co dau vao san
- he thong phai tao bai toan roi tu giai no

### 7.4 Simulated Local Search Mode

Che do local search mo phong tung buoc.
Muc dich:

- quan sat do doc cua heuristic
- xem duong di duoc tao ra va replay tung buoc tren giao dien

## 8. Cach doc cac khu vuc tren giao dien

- `START`: trang thai bat dau
- `GOAL`: trang thai muc tieu
- `CURRENT BOARD`: trang thai hien tai cua thuat toan
- `CHILDREN GENERATED`: cac nut con vua sinh ra
- `SEARCH TREE`: cay tim kiem cuc bo cua buoc hien tai
- `FRONTIER`: tap nut dang cho xu ly
- `ALGORITHM INFORMATION`: thong tin chi tiet ve mode dang chay
- `RESULT SUMMARY`: tong ket ket qua

## 9. Tinh chat cua tung nhom thuat toan

### Nhom tim kiem co bao dam

- BFS
- IDS
- A*

### Nhom tim kiem nhanh nhung khong toi uu

- DFS
- DFS L
- Greedy Best-First
- Hill Climbing
- Random-Restart Hill Climbing
- Local Beam Search

### Nhom local search

- Hill Climbing
- Steepest-Ascent Hill Climbing
- Stochastic Hill Climbing
- Random-Restart Hill Climbing
- Local Beam Search

## 10. Nhan xet tong ket

Neu muon:

- loi giai ngan nhat: uu tien BFS hoac A*
- kiem soat bo nho: IDS hoac DFS
- minh hoa heuristic: Greedy, A*, Manhattan A*
- minh hoa tim kiem cuc bo: cac mode hill climbing va local beam

Dung 8-puzzle de hoc AI rat phu hop vi:

- trang thai don gian
- co the quan sat bang mat
- co nhieu cach tim kiem khac nhau
- de so sanh uu nhieu nhoc diem cua tung thuat toan

## 11. Ghi chu su dung

- `Space`: chay 1 buoc
- `Auto Run`: tu dong chay
- `Prev Step`: quay lai buoc truoc
- `Reset`: khoi tao lai mode hien tai
- `Solve Full`: chay den khi xong hoac cham gioi han

---

Tai lieu nay co the dung lam co so de viet bao cao, thuyet trinh hoac do an mon AI ve bai toan 8-puzzle.
