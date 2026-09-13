# Hexgen.CodexPlugins

Hexgen 团队的 Codex 插件维护仓库。面向使用个人账号的工程师，通过同一个 Git 插件源安装和更新，在不同项目中使用共同的工作流程。

| 项目 | 标识 |
|---|---|
| Git 仓库 | [CarloIT/Hexgen.CodexPlugins](https://github.com/CarloIT/Hexgen.CodexPlugins) |
| 团队插件源 | `hexgen-team` |
| 软件工程插件 | `hexgen-software-engineering` |
| 软件工程插件显示名称 | Hexgen 软件工程规范 |
| 通用工作方式插件 | `hexgen-productivity`（Hexgen 通用工作方式） |

本仓库发布两个可独立安装的插件：`hexgen-software-engineering` 提供软件工程规范；`hexgen-productivity` 提供跨领域的计划、设计与决策追问。五个技能分别保留自己的名称与触发范围。

## 包含的技能

| 技能 | 适用工作 | 主要边界 |
|---|---|---|
| [dev-plan](plugins/hexgen-software-engineering/skills/dev-plan/SKILL.md) | 开发、优化、重构、迭代的分阶段计划 | 不用于 PRD 或单次小改动的临时待办 |
| [dotnet-backend-standards](plugins/hexgen-software-engineering/skills/dotnet-backend-standards/SKILL.md) | .NET 后端设计、实现、审查、测试与排障 | 不用于纯前端或非 .NET 任务；混合任务仅约束后端部分 |
| [manual-acceptance-guide](plugins/hexgen-software-engineering/skills/manual-acceptance-guide/SKILL.md) | 中文人工验收手册及作者回报的结果登记 | 不代替作者执行、签收，也不把自动验证当成人工通过 |
| [Grill Me Single](plugins/hexgen-productivity/skills/grill-me-single/SKILL.md) | 逐题澄清计划、设计、决策或想法 | 显式调用，每次只问一个问题；固定用户认可的本地规则 |
| [Grill Me](plugins/hexgen-productivity/skills/grill-me/SKILL.md) | 按Github 源 SKILL方式分轮集中追问 | 显式调用；跟踪Github 源 SKILL、验证后发布，不保证永远保持当前提问方式 |

前三个技能属于软件工程插件，会按请求匹配，也可显式选择；两个 Grill Me 属于通用工作方式插件，保留显式调用策略。跨项目安装不表示每条请求都要执行所有技能。项目 `AGENTS.md` 保存项目长期规则；仅将规则放在本插件仓库中，不会自动把它们分发为其他项目的全局指令。

## 目录结构

```text
Hexgen.CodexPlugins/
├── .agents/plugins/marketplace.json
├── plugins/hexgen-software-engineering/
│   ├── .codex-plugin/plugin.json
│   └── skills/
│       ├── dev-plan/
│       ├── dotnet-backend-standards/
│       └── manual-acceptance-guide/
├── plugins/hexgen-productivity/
│   ├── .codex-plugin/plugin.json
│   ├── skills/grill-me-single/
│   ├── skills/grill-me/
│   ├── 上游快照/入口.md
│   ├── 上游来源.json
│   ├── 上游维护.md
│   └── LICENSE
├── scripts/校验插件.ps1
├── scripts/检查上游技能.py
├── scripts/验证上游检查.py
├── AGENTS.md
├── README.md
└── CHANGELOG.md
```

市场条目中的 `./plugins/<插件标识>` 相对于仓库根目录。每个技能目录包含完整的 `SKILL.md`、引用文件、模板及 `agents/openai.yaml`。

## 工程师首次安装

前提：安装支持 `codex plugin` 的 Codex CLI，并使用 Codex 桌面端或 CLI。若仓库为私有，工程师的 Git 凭据必须具有读取权限；不需要共享维护者的账号或凭据。

本地提交发布到 GitHub 后，在 PowerShell 中执行：

```powershell
codex plugin marketplace add https://github.com/CarloIT/Hexgen.CodexPlugins.git --ref main
codex plugin add hexgen-software-engineering@hexgen-team
codex plugin add hexgen-productivity@hexgen-team
```

先注册插件源，再安装所需插件；可以只安装其中一个，前一条失败时先解决原因。两个都安装后，在 CLI 或桌面端开启新任务，应分别看到“Hexgen 软件工程规范”的三个技能和“Hexgen 通用工作方式”的两个技能。桌面端与 CLI 应使用同一套本地 Codex 配置；不同设备、Windows 用户或自定义 `CODEX_HOME` 需要分别配置。

可以用以下命令检查插件列表；该命令不会安装插件：

```powershell
codex plugin list --marketplace hexgen-team --json
```

在新任务的技能选择器中选择对应技能，或使用包含插件前缀的名称，明确调用本插件提供的版本：

```text
使用 $hexgen-software-engineering:dev-plan，为当前已确认的需求编写分阶段开发计划。
使用 $hexgen-software-engineering:dotnet-backend-standards，审查当前任务涉及的 .NET 后端改动。
使用 $hexgen-software-engineering:manual-acceptance-guide，为当前变更编写中文人工验收手册。
使用 $hexgen-productivity:grill-me-single，逐题帮我想清楚这份计划，每次只问一个问题。
使用 $hexgen-productivity:grill-me，按上游规则分轮讨论这份计划。
```

Codex IDE 扩展当前不支持插件；本仓库的插件安装流程面向桌面端与 CLI。需要其他客户端时，应先核实其支持方式。[官方客户端说明](https://learn.chatgpt.com/docs/plugins)

## 维护与团队更新

源码目录、GitHub 发布源、Codex 安装副本各自独立：

```text
维护者编辑本仓库 → 验证并发布到 GitHub → 维护者与工程师更新插件 → 新任务使用
```

1. 在 `plugins/<插件标识>/skills/<技能名>/` 修改源码及受影响的引用或模板。Grill Me 的原文快照与来源记录按[上游维护说明](plugins/hexgen-productivity/上游维护.md)处理；Single 独立维护。不要直接编辑 Codex 缓存作为团队变更。
2. 调整受影响插件的独立版本，并在 `CHANGELOG.md` 标明插件及版本，记录行为、适用范围或包装变化。仅文案修正通常递增补丁版本；新增能力递增次版本；破坏既有工作约定的变更需明确说明升级影响。公开版本不复用。
3. 从仓库根目录执行结构校验和差异检查：

   ```powershell
   & '.\scripts\校验插件.ps1'
   git diff --check
   ```

4. 根据改动验证实际安装、技能发现及代表性请求。结构通过只能证明包装与本地引用完整，不能证明模型行为或人工验收通过。
5. 审查后提交，并由获得推送授权的人将通过验证的变更推送到 GitHub。`main` 作为团队发布通道，未验证内容在独立分支整理。
6. 发布后维护者先更新自己的安装副本并验证，再通知工程师更新。维护者刚推送的源码无需再次 `git pull`。

维护者和工程师使用相同的更新命令：

```powershell
codex plugin marketplace upgrade hexgen-team
codex plugin add hexgen-software-engineering@hexgen-team
codex plugin add hexgen-productivity@hexgen-team
```

第一条刷新 Git 插件源快照，后面的命令安装对应插件版本，按需选择安装并随后开启新任务。普通 `git pull` 只更新源码工作目录，不等于更新插件。发布或更新失败时保留错误信息，先确认分支、权限和源地址，不原样反复重装。

## 本地试装与旧技能切换

远程尚未发布时，可在独立的临时 Codex 配置中注册本地仓库并试装：

```powershell
$previousCodexHome = $env:CODEX_HOME
$pluginTestConfig = Join-Path ([System.IO.Path]::GetTempPath()) ('Hexgen.PluginTest-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $pluginTestConfig | Out-Null
try {
    $env:CODEX_HOME = $pluginTestConfig
    codex plugin marketplace add 'E:\Hexgen.Products\Hexgen.CodexPlugins'
    if ($LASTEXITCODE -ne 0) { throw '注册本地插件源失败' }
    codex plugin add hexgen-software-engineering@hexgen-team
    if ($LASTEXITCODE -ne 0) { throw '安装插件失败' }
    codex plugin add hexgen-productivity@hexgen-team
    if ($LASTEXITCODE -ne 0) { throw '安装通用工作方式插件失败' }
    codex plugin list --marketplace hexgen-team --json
    if ($LASTEXITCODE -ne 0) { throw '读取插件列表失败' }
} finally {
    $env:CODEX_HOME = $previousCodexHome
}
```

仓库路径是维护者当前示例，其他机器换成实际仓库根目录。该脚本只在临时配置中试装，最后恢复当前 PowerShell 的原环境变量；测试文件保留在 `$pluginTestConfig` 便于排查，日常 Codex 不会因此安装插件。需要验证实际技能发现时，让隔离的 Codex App Server 执行 `skills/list`，分别查询仓库目录和无关项目目录；应发现三个来自 `hexgen-software-engineering`、两个来自 `hexgen-productivity` 的启用技能，错误列表为空；两个 Grill Me 的显示名称分别为 Grill Me Single / Grill Me，且隐式调用均关闭。原始快照不应形成第三个追问技能。

日常使用按“工程师首次安装”配置 Git 来源。已在日常配置注册同名本地源时，先用 `codex plugin marketplace list --json` 核对来源，再明确切换；`marketplace upgrade` 用于刷新 Git 来源，不会把本地来源转换成 Git 来源。

原先安装在个人 `~/.codex/skills` 下的三个技能可先保留，待插件安装和新任务验证通过后，再禁用旧版本或将它们备份到技能扫描目录之外。只处理已确认迁入并完成验证的旧版本，保留其他个人技能。个人目录中的 `grill-me` / `grilling` 同样先保留，验证插件版后再明确切换，避免按裸名称调用时混淆。迁入仓库不自动安装插件、不停用原技能，也不使当前已运行任务切换版本。

技能启用设置应使用客户端支持的方式；如编辑配置，须以旧技能实际路径为准。不要删除源码仓库，也不要将备份放在另一处仍会被扫描的技能目录。[官方技能发现与配置说明](https://learn.chatgpt.com/docs/build-skills)

## Grill Me 上游跟踪

在 PowerShell 中运行以下只读检查，需要 Python 3.9+，不安装第三方依赖：

```powershell
python '.\scripts\检查上游技能.py'
python '.\scripts\检查上游技能.py' --offline
python -B '.\scripts\验证上游检查.py'
```

在线检查同时跟踪上游入口、实际规则目录及 LICENSE，报告新增、修改和删除；先验证本地快照与 Single 完整性，再比较固定的远程 commit。退出码 `0` 为无相关更新，`2` 为发现更新，`1` 为检查失败；离线模式的 `0` 只说明本地完整性通过。网络或 GitHub 限流错误不代表“已是最新”。

检查不会覆盖文件、安装插件或发布版本，当前未配置定时任务。采用新版本时先审查差异和依赖、保留许可、验证行为，再更新来源记录并发布。详见[来源、Codex 适配和更新流程](plugins/hexgen-productivity/上游维护.md)。

## 校验与文件格式

`scripts/校验插件.ps1` 使用 PowerShell 和 .NET 内置功能，无第三方依赖，需要在允许执行本地脚本的 PowerShell 环境中运行。它检查市场与插件标识、版本基本格式、必要字段、两个插件的五个技能入口与 UI 元数据、本地 Markdown 引用、UTF-8 无 BOM 和文件内行尾一致性。它不实现完整 YAML/schema 校验，也不调用模型、不安装插件、不连接外部服务。

插件打包首次交付及结构变更，应另用 Codex 在隔离配置中实际安装并读取技能列表。若安装环境提供 plugin-creator / skill-creator 的校验脚本，也应运行；其 Python YAML 依赖不可用时要如实记录，并用 Codex 实际解析结果验证发现行为。

新文档与清单采用 UTF-8 无 BOM + CRLF。迁入技能保留各自原有 LF 或 CRLF，`.gitattributes` 固定其检出行尾，避免不同 Git 配置改变技能文件。后续修改继续保持所属文件格式。

## 参考

- [官方插件构建说明](https://learn.chatgpt.com/docs/build-plugins)
- [官方插件安装说明](https://learn.chatgpt.com/docs/plugins)
- [官方技能文档](https://learn.chatgpt.com/docs/build-skills)

安装与更新命令已按 Codex CLI 0.147.0 核对；客户端升级后，以本机 `codex plugin --help` 和各子命令帮助为准。
