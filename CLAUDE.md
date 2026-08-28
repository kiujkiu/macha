# macha (pov3d 结构件)

## 🔴 提交 = 推两个远端

用户 2026-07-30 定的规矩：说"提交"就是 **两个远端都推**，别只推 origin。

| remote | URL |
|---|---|
| `origin` | `https://github.com/kiujkiu/macha.git` （个人账号，原仓属主） |
| `yjhh` | `https://github.com/pov-yjhh/macha.git` （组织） |

同一套约定也用在 `zynq_pov`、`mlkpai_fs03`，详见
`D:\claude_workspace\pov3d\zynq_pov\docs\claude_memory\reference_git_dual_remote.md`。

### 推送命令

WSL 里 **必须走 `cmd.exe`** 才能用上 Windows 凭据管理器，别绕 SSH/PAT：

```bash
cmd.exe /c "cd /d D:\claude_workspace\macha\pov3d && git push origin master && git push yjhh master"
```

注意 git 仓库根目录是 `macha\pov3d`，不是 `macha` —— 外层 `macha\`（含 `.claude\`、`memory\`）不在版本控制里。

### 三个坑

1. **别用 `git push -u yjhh`**。`-u` 会把 `master` 的上游从 `origin/master` 改成 `yjhh/master`，
   之后裸 `git push` / `git pull` 就默默走组织仓了。上游固定留在 `origin`，和另外两个仓库一致。
   万一改错了：`git branch --set-upstream-to=origin/master master`。

2. **`dubious ownership`**。目录属主是 `PC-W003SS3G0143/kiujkiu`，但 cmd.exe 里当前用户解析成
   `UNDEF/wanqi.liu`，Windows git 会拒绝操作。已配过例外，换机后需重配：
   ```
   git config --global --add safe.directory D:/claude_workspace/macha/pov3d
   ```

3. **组织下的新仓库要手工建**（本机没有 `gh` CLI）。建时 Owner 记得从 `kiujkiu` 切成 `pov-yjhh`，
   且 README / .gitignore / license **三项都不要勾** —— 勾了远端会有一个无关的初始 commit，
   首次推送报 `non-fast-forward`，还得 `--allow-unrelated-histories` 收拾。
