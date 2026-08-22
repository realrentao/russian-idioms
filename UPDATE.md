# 俄语习语网站 · 更新流水线说明

> 项目路径：`D:/俄语材料/俄语习语/`
> 线上地址：https://realrentao.github.io/russian-idioms/
> 仓库：`realrentao/russian-idioms`（GitHub Pages，默认分支 `main`）

---

## 一、文件角色

| 文件 | 作用 |
|---|---|
| `russian_idioms_data.py` | **数据源**。每条习语一个 dict，`id` 必须从 1 连续递增（生成器与页面顺序都依赖它）。 |
| `russian_generate_html.py` | **生成器**。读数据 → 调 `edge_tts` 生成音频 → 写出 `index.html` + `idiom-XX.html` + `data/*.json`。 |
| `audio/*.mp3` | 主音频（100 个，文件名是习语西里尔转写）。详情页 `audioUrl` 引用，**必须入库**。 |
| `audio/inline_*.mp3` | 内联音频实体备份（300 个）。页面**不引用**（用 `data/` 的 base64），已被 `.gitignore` 排除。 |
| `data/*.json` | 内联音频的 base64（300 个）。页面按需加载，**必须入库**。 |
| `index.html` / `idiom-XX.html` | 页面（共 101 个）。**必须入库**。 |

**入库清单**：`index.html` + `idiom-01..100.html` + `data/*.json` + `audio/` 下**非 inline 的主音频**。
**不入库**：`audio/inline_*.mp3`、`deploy.py`（见 `.gitignore`）。

---

## 二、日常更新流程（改数据 / 加习语）

### 1. 改数据
编辑 `russian_idioms_data.py`：
- 新增习语 → 在列表末尾追加，**`id` 取当前最大值 +1**，保持连续。
- 改已有习语 → 直接改对应 dict，不要动 `id`。
- 字段必须齐全：`id / idiom / category / meaning_cn / meaning_it / meaning_it_cn / usage_cn / examples / cultural_cn / exercise_q / english_eq`。
- 填空题：`fill` 列表长度 = 输入框数量；题面里的 `___` 只是视觉占位，可写一段或拆成多段（不影响判分）。

### 2. 重新生成（出沙箱联网）
```bash
cd "D:/俄语材料/俄语习语"
"C:/Users/迪丽希斯/.workbuddy/binaries/python/envs/default/Scripts/python.exe" russian_generate_html.py
```
生成器会**自动跳过已存在的音频文件**，只联网生成新增/改动习语的主音频 + 内联音频，并**重建全部 HTML**（index + 详情页）。

> ⚠️ 必须在**出沙箱**环境运行（edge-tts 需访问微软 TTS 网络）。Bash 工具加 `dangerouslyDisableSandbox=true`；WorkBuddy 内直接跑会被拦截。

### 3. 本地预览
打开 `D:/俄语材料/俄语习语/index.html`，确认新习语出现、音频可播放、练习题判分正常（西里尔填空已做 `\w` 扩展，俄文判分准确）。

### 4. 提交并推送
```bash
cd "D:/俄语材料/俄语习语"
git add -A
git commit -m "更新：新增/修订 N 条俄语习语"
git push -u origin main
```
GitHub Pages 会在推送后 **1–2 分钟**自动重新构建，无需手动操作。
浏览器若仍显示旧版 → **硬刷新**（Ctrl+F5 / 无痕窗口）清缓存。

---

## 三、完整首次部署（仅首次需要，已做过）

部署脚本：`D:\workbuddy工作区\2026-08-22-14-19-36\deploy_russian.py`
它负责：读 `~/.workbuddy/mcp.json` 的 PAT → 建仓库 → `git init` → 提交 → `git push` → `POST /repos/.../pages` 启用 Pages。

已上线后**日常更新只需走第二节的"提交并推送"**，不要重跑 `deploy.py`（会重复建仓/force push）。

---

## 四、避坑清单

1. **PAT 来源**：始终从 `~/.workbuddy/mcp.json` 读取，切勿写死进脚本或提交到仓库。
2. **`id` 必须连续**：断号会导致 index 翻页错位、生成器循环越界。
3. **分类映射**：新增 `category` 俄文值后，必须在 `russian_generate_html.py` 的 `CATEGORY_CN` 字典里补中文映射，否则 index 筛选器显示"缺失映射"。
4. **inline 备份不入库**：`.gitignore` 已排除 `audio/inline_*.mp3`；若误删 `.gitignore`，推送前确认没把这些 300 个文件加进去（页面不依赖它们）。
5. **Bash 输出截断误判**：用 Bash 跑 python 部署/push 时，`tail` 可能截断 push 后的输出让脚本看起来"失败"。判断真失败看 `git status`/`git log` 与 `git push` 的真实返回码——本项目的 push 实际已成功，重跑 `git push` 单独命令即可确认。
6. **Pages CDN TLS 偶发超时**：首页偶尔 `urlopen handshake timed out`，属 GitHub CDN 正常抖动，详情页能 200 即说明站点在线，刷新即可。
7. **体积**：当前仓库约 11MB（data 7.5M + 主音频约 2M + html 1.6M）。继续加习语时主音频与 data json 会线性增长，属预期。

---

## 五、一键重推（带缓存校验，可选）

若担心漏推或想强制全量同步，可重新执行提交+推送（生成器已增量跳过音频，重复 commit 也不会重复生成音频）：
```bash
cd "D:/俄语材料/俄语习语"
git add -A && git commit -m "sync: 全量重推俄语习语站" && git push -u origin main
```
