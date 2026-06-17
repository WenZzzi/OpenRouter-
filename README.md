# OpenRouter 生图中转服务

claude.ai artifact 无法直接请求 OpenRouter（CORS 拦截）。
这个服务部署到 Railway 作为中转，artifact 调你的 Railway URL，由服务端转发到 OpenRouter。

## 部署步骤（Railway）

### 方式一：GitHub 部署（推荐）

1. 把这个文件夹 push 到一个 GitHub 仓库
2. Railway → New Project → Deploy from GitHub repo → 选这个仓库
3. 部署后，到 **Variables** 标签，添加环境变量：
   ```
   OPENROUTER_API_KEY = sk-or-v1-你的key
   ```
4. Railway 会自动重新部署
5. 到 **Settings → Networking → Generate Domain**，拿到公开 URL
   （形如 `https://xxx.up.railway.app`）

### 方式二：Railway CLI

```bash
npm i -g @railway/cli
railway login
railway init
railway up
railway variables set OPENROUTER_API_KEY=sk-or-v1-你的key
railway domain   # 生成公开域名
```

## 测试

部署好后测试健康检查：
```bash
curl https://你的域名.up.railway.app/
# 应返回 {"status":"ok",...}
```

测试生图：
```bash
curl -X POST https://你的域名.up.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"a cute black cat, flat illustration"}'
```

## API

### POST /generate
请求体：
```json
{
  "prompt": "要画的内容",
  "size": "1024x1024",   // 可选
  "n": 1                  // 可选
}
```

## 安全提示

- API Key 只存在 Railway 环境变量里，不写进代码、不进 git
- CORS 当前设为允许所有来源（`*`），方便 artifact 调用
- 如需收紧，可把 app.py 里的 origins 改成只允许 claude.ai
