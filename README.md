# 桌游比赛管理系统

这是一个局域网私有部署的桌游比赛管理系统，后端使用 FastAPI + SQLite，前端使用 Vue3 + TypeScript，管理端使用 Element Plus，裁判扫码端使用 Vant。

## 环境要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- npm

## 下载后部署

macOS / Linux：

```bash
git clone https://github.com/StarXUz/deskgame.git
cd deskgame

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
npm run build
cd ..

uvicorn main:app --host 0.0.0.0 --port 8000
```

Windows PowerShell：

```powershell
git clone https://github.com/StarXUz/deskgame.git
cd deskgame

py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd frontend
npm install
npm run build
cd ..

uvicorn main:app --host 0.0.0.0 --port 8000
```

启动后访问：

- 管理端：`http://本机局域网IP:8000/admin`
- 后端接口文档：`http://127.0.0.1:8000/docs`

## 开发方式

安装完后端和前端依赖后，可以运行：

```bash
python scripts/start_dev.py
```

它会同时启动：

- 前端页面：`http://127.0.0.1:5173/admin`
- 后端接口：`http://127.0.0.1:8000/docs`

macOS 也可以双击根目录的 `启动前后端.command`。

Windows 可以双击根目录的 `启动前后端.bat`。

## 正式启动

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

首次启动会自动创建本地 SQLite 数据库文件：`data/tournament.sqlite3`。比赛数据、二维码、导出报表等运行时文件不会上传到 GitHub，需要在部署机器上现场生成。

可选现场资源：

- 若需要自定义实时成绩表样式，可放入 `templates/成绩统计表模板.xlsx`；没有模板时系统会自动生成基础格式。
- 若需要显示场馆座位底图，可放入 `static/assets/seat_map.jpg`；没有底图时仍可使用座位点位和桌号分配功能。

## 访问入口

- 管理端：`http://本机局域网IP:8000/admin`
- 裁判端：扫描选手个人二维码自动进入 `http://本机局域网IP:8000/player?token=...`，再进入本桌成绩录入。

本机局域网 IP 可在 macOS 终端运行：

```bash
ipconfig getifaddr en0
```

## Excel 导入列

必须包含以下列：

- `姓名`
- `队伍名称`
- `年级组别`
- `所属游戏`
- `赛前种子排名`
- `是否升学过渡`
- `升学出路选择`

可选值：

- 年级组别：`小学低年级组`、`小学高年级组`、`初中组`
- 所属游戏：`大熊猫国家公园`、`雪山之巅·三江源`、`雨林奇境`
- 是否升学过渡：`是` / `否`
- 升学出路选择：`自由人补位` / `跟随原学校`

赛前种子排名必须从 1 开始连续且全局唯一。

## 现场工作人员一页纸操作指南

1. 赛前关闭系统防火墙，或放行 8000 端口。
2. 确认所有设备连接同一个 Wi-Fi。
3. 启动系统后，在电脑浏览器打开管理端。
4. 在“选手导入”上传 Excel。若出现人数警告，确认名单无误后可强制导入。
5. 在“升学过渡管理”确认自由人名单和原校特批名单。自由人会单独比赛，不补入普通桌位。
6. 每轮开始前进入“赛程控制台”，选择轮次并点击“生成本轮桌位”。
7. 打印或截图每位选手的个人二维码，发给选手或贴在选手证件上。
8. 裁判扫描任意选手个人二维码，查看当前桌位，并点击“录入本桌成绩”提交本桌分数；缺席选手勾选“缺席”。
9. 全部桌位提交后，系统自动结束本轮；继续生成下一轮。
10. 第 6 轮结束后，进入“最终报表”导出 Excel。

## iOS 扫码提示

局域网部署默认是 HTTP。若 iOS 扫码工具强制要求 HTTPS，可让裁判用 Safari 直接打开链接，或使用安卓手机/第三方扫码工具。
