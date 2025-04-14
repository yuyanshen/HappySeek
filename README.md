# HappySeek


web-crawler/
├── frontend/               # 前端代码
│   ├── public/
│   └── src/
│       ├── views/Crawler.vue  # 主界面
│       └── ...
├── backend/                # 后端代码
│   ├── app.py              # Flask主程序
│   ├── crawler.py          # 爬虫核心
│   └── celery_worker.py    # 异步任务
├── requirements.txt        # Python依赖
└── README.md