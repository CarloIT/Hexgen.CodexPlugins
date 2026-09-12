# .NET 全局编程规范（后端）

> 适用范围：所有 .NET 后端项目（C#）。**不含前端**。
> 本规范由「默认 .NET 最佳实践」与作者在 Hexgen 系列项目中已有的编码习惯融合而成，将随协作持续优化。
> 示例仅展示所在章节的约定，不是完整应用；具体类型、扩展方法及契约以项目源码为准。

## 目录

1. [总则](#1-总则)
2. [命名规范](#2-命名规范)
3. [项目与文件组织](#3-项目与文件组织)
4. [注释规范](#4-注释规范)
5. [异步最佳实践](#5-异步最佳实践)
6. [异常与错误处理](#6-异常与错误处理)
7. [`#region` 最佳实践](#7-region-最佳实践)
8. [`partial class` 最佳实践](#8-partial-class-最佳实践)
9. [Controller 最佳实践](#9-controller-最佳实践)
10. [依赖注入与生命周期](#10-依赖注入与生命周期)
11. [性能与资源管理](#11-性能与资源管理)
12. [安全](#12-安全)
13. [程序入口最佳实践（Program.cs / AppSettings / AppHelper）](#13-程序入口最佳实践)
14. [测试](#14-测试)
15. [多目标与兼容性](#15-多目标与兼容性)
16. [代码格式与控制流](#16-代码格式与控制流)

---

## 1. 总则

- **优先级与范围**：用户明确指令及项目显式约定优先于本 Skill；格式遵守 `.editorconfig` / `.gitattributes`。已有授权不重复询问，仅对影响范围、公共契约或实际执行风险的未决事项确认。
- **Hexgen 统一默认**：未另作约定的新 .NET 后端采用 `AppSettings` / `AppHelper`、`ApiResponse` 和相应 Helper/Service 分工，有数据库需求时默认使用 SqlSugar 底座；已有项目遵循其显式架构。使用前核实已有引用与 API，默认体系不授权新增第三方依赖或改造全库；确需新增依赖时按用户约定确认。
- **可读性与一致性**：新增代码遵守已确定的命名、注释和格式规则；在未规定处沿用周围代码。通用能力与业务解耦；只调整本次任务相关内容，范围外的风格、重构或性能问题只报告。
- **中文优先**：注释与文档以中文为主，关键字与专业名词保留英文。
- **配置变更有范围**：新项目推荐 `Nullable`、`ImplicitUsings`，类库建议 `GenerateDocumentationFile`，CI 按项目要求采用 `TreatWarningsAsErrors` 或关键告警门槛。现有项目先查 TFM、`LangVersion`、构建属性，不在小改动中顺手修改配置或追加目标框架。
- **个人约定持续有效**：以下风格规则不因模型升级而放宽；先方案后落地、测试桌面影响和 Git/依赖等协作边界遵循当前会话及 `AGENTS.md`。

## 2. 命名规范

| 元素 | 规则 | 示例 |
| --- | --- | --- |
| 类型 / 方法 / 属性 / 事件 / 公共成员 | `PascalCase` | `AppHelper`、`GenerateId` |
| 私有/受保护字段 | `_camelCase`（下划线前缀） | `_configuredServices`、`_instanceLock` |
| 局部变量 / 方法参数 | `camelCase` | `plainText`、`maxDepth` |
| 常量 `const` / `static readonly` | `PascalCase` | `MaxDepth`、`DataCenterIdBit` |
| 接口 | `I` 前缀 | `IClone` |
| 泛型参数 | `T` 或 `T` 前缀 | `T`、`TKey`、`TResult` |
| 异步方法 | `Async` 后缀 | `SaveAsync`、`GetBeiJingTimeAsync` |
| 布尔成员 | `Is/Has/Can/Should` 前缀 | `IsMixed`、`CanWrite` |

补充约定：

- **扩展方法类统一命名 `XxxExtension`**（单数、拼写正确）。
- **静态门面/帮助类用 `XxxHelper`**（`AESHelper`、`CacheHelper`）；**服务用 `XxxService`**。
- **锁字段统一 `_xxxLock` 命名**（`_connectionLock`、`_instanceLock`、`_stateLock`）；不用 `_locker` / `_lock_Xxx`。
- 不使用匈牙利命名；不使用拼音；缩写仅限广为人知者（`Id`、`Url`、`Http`、`Json`、`IP`），且作为单词时只首字母大写（`HttpRequest` 而非 `HTTPRequest`，但已固化的 `IP`/`OSS` 可整体大写——库内统一即可）。
- **词级缩写白名单**：`Error`→`Err`、`Message`→`Msg`（如 `ErrCode`、`ErrMsg`）；一旦采用须全库统一，不与全称混用。扩充白名单前先确认。
- 命名要可读、自解释；宁可长一点也不要含糊（`firstDifferentItem` 优于 `fdi`）。
- **Lambda 参数命名**：通用参数优先 `t`，第二层嵌套用 `x`（如 `list.Any(t => t.Any(x => x.Children.Count > 0))`）；更深嵌套优先拆分，确需保留时使用业务语义名称。
- **文件名与主类型一致**；**一个 `.cs` 文件只放一个顶层类型**（`partial` 拆分见 §8）。`private nested` 是特例——当某类型仅服务一个外层类型、不值得单独成文件时，可内联在所属类型的同一文件中；否则独立成文件（`internal`）。

## 3. 项目与文件组织

- **命名空间与目录结构一致**。
- **块级 vs 文件级 namespace**：项目内**统一**即可。Hexgen 系列现用块级 `namespace X { ... }`；新项目可选文件级（`namespace X;`）减少缩进，但不要在同一项目内混用。
- `using` 顺序：`System.*` → 第三方 → 本项目；可用 `global using`（或 `.csproj` 的 `<Using>`）收敛高频命名空间。
- **`global using` 去重与上提**：已在 `.csproj` 的 `<Using>` 或 `GlobalUsings.cs` 声明的命名空间，不在单文件重复 `using`。多文件重复引用可建议上提，但会扩大全项目符号可见面，须由人类主导者决定；未授权时只报告建议，不修改全局配置、不阻塞其他工作，已有明确授权不再重复询问。
- 成员排列建议：常量/字段 → 构造函数 → 属性 → 方法；公有在前、私有在后；静态与实例分组。

## 4. 注释规范

1. **公共 API 必须有 XML 文档注释**，私有成员按需；中文优先，保留英文术语。
   - `<summary>` / `<remarks>` 的开始标签、内容、结束标签各占一行，即使只有一句也不压成单行。
   - `<param>` / `<typeparam>` / `<returns>` / `<exception>` / `<value>` 每条标签完整写在同一 `///` 行内。
   - **唯一排版例外**：`<param>` 内含 `<list>` 时允许多行。`<param>` 开始标签与引导文字同行，`<list>`、每条 `<item>`、`</list>`、`</param>` 各占一行；每个 `<item>` 的标签与内容仍保持单行。
   - `<see cref="..."/>`、`<paramref name="..."/>`、`<see langword="..."/>`、`<c>`、`<b>` 等行内标签内嵌于文字。

   普通 XML 注释示例：
   ```csharp
   /// <summary>
   /// 按协议约定读取点位数据。
   /// </summary>
   /// <param name="address">点位地址。</param>
   /// <param name="length">读取长度，其含义由协议决定。</param>
   /// <returns>读取结果。</returns>
   ```

   `<param>` 含列表的排版示例，具体协议语义以项目契约为准：
   ```csharp
   /// <param name="length">读取长度，对变长场景有意义：
   /// <list type="bullet">
   /// <item><b>Modbus</b>：按 <paramref name="length"/> 决定读取字节数。</item>
   /// <item><b>OpcUa</b>：<paramref name="length"/> 不生效，返回服务器当前值。</item>
   /// </list>
   /// </param>
   ```
2. **XML 文档中的代码标识符用引用标签**：类型/成员用 `<see cref="ApiResponse"/>` / `<see cref="ApiResponse.Total"/>`；参数用 `<paramref name="length"/>`；关键字用 `<see langword="null"/>`。不要将这些标识符写成普通字符串。
3. **文档说明契约，实现注释解释原因**：公共 API 的 XML 注释应说明功能、参数、返回值及必要的失败边界；方法体内注释解释意图、权衡或外部约束，不复述代码。行为改变时同步更新注释。
4. **运行时字符串中的成员名优先 `nameof(...)`**；当前方法名和项目扩展方法的边界见 §6。
5. **TODO / 已有作者署名**沿用以下格式；署名须有真实依据，不自动套用示例中的作者和日期：
   ```csharp
   //TODO --考虑实现默认的 Token 判断？
   //此处切勿更改堆栈信息 --by ZhuShaoxiang @2024.07.11
   ```
6. **废弃公共成员**按 §15 的兼容性判断使用 `[Obsolete("理由")]`，并在 `<remarks>` 中指向替代 API；不只按是否到达 1.0 决定是否保留过渡。
7. **实现注释的多行格式**：一句话用 `//`；多行说明或分条论证使用 `/* … */`，不堆叠多行 `//`。第一行先给结论，续行用对齐的 `*`，再解释前提、依据和失效条件。
   ```csharp
   /* 两次读取之间锁会短暂释放，但当前调用路径仍保持串行。
    * 上层持有同一把业务锁，且不存在后台读循环。
    * 若引入其他读取方，必须重新核实帧接收的原子性。
    */
   ```
   此规则只针对实现注释；XML 文档仍遵循本节第 1 条。异常吸收点若一句 `// reason: ...` 能说明原因，无需改为块注释。

## 5. 异步最佳实践

- **类库 `await` 使用 `.ConfigureAwait(false)`**，应用层不强制；若 API 明确依赖调用方上下文则保留契约、说明例外。它不能替代同步阻塞和锁依赖分析。
- 新增异步方法默认返回 `Task` / `Task<T>`，命名以 `Async` 结尾；已有 API 的命名和返回类型受 §15 约束。
- **限定异步化范围**：本次新增或修改的 I/O 优先使用真正的异步 API；范围外同步 I/O 只报告，不自动重构调用链，也不用 `Task.Run` 制造形式上的异步。
- **禁止 `async void`**，事件处理器除外；事件处理器自身负责必要的异常处理。
- **禁止用 `.Result` / `.Wait()` / `.GetAwaiter().GetResult()` 同步阻塞未完成的异步操作**，避免死锁和线程阻塞。
- **透传 `CancellationToken`**：新增对外异步 API 在支持取消时提供并下传令牌；已有 API 按 §15 先查兼容性，增加可选参数也可能破坏二进制兼容。调用方取消不包装为普通业务故障。
  ```csharp
  /// <summary>
  /// 获取远程时间。
  /// </summary>
  /// <param name="url">时间服务地址。</param>
  /// <param name="timeout">超时时长，单位为毫秒（ms）。</param>
  /// <param name="cancellationToken">取消令牌。</param>
  /// <returns>远程时间。</returns>
  Task<DateTime?> GetBeiJingTimeAsync(string url, int timeout = 3000, CancellationToken cancellationToken = default);
  ```
- **谨慎 fire-and-forget**：不直接用 `_ = SaveAsync();` 丢弃任务；确需后台执行时使用项目已有的后台队列或受管理任务，明确停止方式并观测异常。
- `Task.WhenAll` 只用于能安全并发的独立操作；业务独立不代表可以并发使用同一个非线程安全的 `DbContext`、连接或客户端。
- **`ValueTask` / `ValueTask<T>` 按收益选择**：仅在分配开销重要，且高比例同步完成或可有效复用异步资源时考虑，并确认调用方可遵守直接消费、不重复等待等限制；不因为“热路径”或“只读”就替换 `Task`。流式返回可用 `IAsyncEnumerable<T>`。参见 [ValueTask 选择依据](https://devblogs.microsoft.com/dotnet/understanding-the-whys-whats-and-whens-of-valuetask/)。

## 6. 异常与错误处理

- 抛出**具体异常类型**和清晰中文消息；参数异常使用 `nameof` 指定参数或成员名，状态错误使用 `InvalidOperationException` 等适当类型：
  ```csharp
  throw new ArgumentOutOfRangeException(nameof(DataCenterId), $"数据中心 ID 应介于 0–{MaxDataCenterId} 之间。");
  ```
- **不要吞异常**；可预期失败沿用项目的 `TryXxx(out ...)` 或结果契约。仅对有明确理由的吸收点采用 §16 的空 `catch` 例外。
- 重抛保留堆栈用 `throw;`，不要 `throw ex;`。
- **成员名优先 `nameof(...)`**。项目确实提供 `GetFullName()` 且需完整诊断名称时，才沿用 `MethodBase.GetCurrentMethod()?.GetFullName()`；异步状态机、混淆等场景核实实际输出，不假定得到源代码方法名，也不为此新增扩展方法或依赖。
  ```csharp
  throw new InvalidOperationException($"已进行服务配置，禁止重复调用 {nameof(ConfigureServices)}。");
  ```
- **面向用户的报错话术统一**（如“……请联系软件厂商/系统管理员”）。生产环境对外返回通用消息与 correlation id；异常详情和堆栈写日志，仅开发环境按需返回细节。
- **判空优先 `is null` / `is not null`**，避免自定义 `==` / `!=` 运算符影响判空；普通值比较仍用 `==`。
- **禁用 property pattern（属性模式）**：不写 `obj is { IsValid: true }` / `obj is not { IsValid: true }`，改为判空加属性访问：
  ```csharp
  if (obj is null || !obj.IsValid)
  {
      return;
  }
  ```
  `is null` / `is not null` 是保留的判空语法，不在属性模式禁用范围内。

## 7. `#region` 最佳实践

- 用于**对成员做主题分组**（如「构造函数」「Properties」「Swagger 配置」「IP 黑名单」），提升长文件可读性。
- 命名要清晰表达分组意图；与代码块边界对齐。
- **不要用 `#region` 掩盖坏味道**（超长方法、过大类）——那是拆分的信号，不是折叠的理由。
- 避免过深嵌套；一个 `#region` 内聚一个主题。

## 8. `partial class` 最佳实践

合理用途：

1. **隔离生成代码**（设计器、source generator）与手写代码。
2. **拆分超大类型到多文件**（如按功能分 `Foo.Core.cs` / `Foo.Validation.cs`）。
3. **同文件内"逻辑分节"**（Hexgen 系列特色）：把一个类型拆成同文件多个 `partial class X { }` 段，每段聚焦一个职责，配合 `#region` 组织。例：`AESHelper`（加密/解密/密钥生成分三段）、`ApiResponse`（数据体/异常处理分两段）。
   ```csharp
   public static partial class AESHelper
   {
       // 加密成员。
   }
   partial class AESHelper
   {
       // 解密成员。
   }
   partial class AESHelper
   {
       // 密钥与 IV 生成成员。
   }
   ```

边界：

- `partial` 是**组织手段**，不是给 God class 续命的工具。当多个分段彼此低内聚、依赖各异时，应**拆成独立类型**而非继续 `partial`。
- 同文件分节时，**只在第一段写访问修饰符与基类/接口**，后续段用 `partial class X` 即可。

## 9. Controller 最佳实践

- **薄 Controller**：只做“接收请求 → 调用 Helper/Service → 返回”，不承载业务逻辑与数据访问。以下是项目已有无状态静态 Helper 门面的示例；有状态依赖通过构造函数 DI 注入：
  ```csharp
  [HttpPost]
  [ApiExtension(AutoLog = true)]
  public async Task<ApiResponse> Upload(IFormFile file)
      => await OSSHelper.UploadAsync(file).ConfigureAwait(false);
  ```
- **API 用 `ControllerBase`**（无需视图），MVC 页面才用 `Controller`。
- **继承项目统一基类**以共享路由前缀、鉴权策略等约定；具体基类与路由模板由各项目在自身 `AGENTS.md` 或其明确指向的设计文档中规定。
- 显式标注 HTTP 动词（`[HttpGet]`/`[HttpPost]`）。
- **统一返回类型**（如 `ApiResponse`）；文件下载返回 `IActionResult`/`File(...)`。
- I/O 调用链按 §5 使用异步；纯同步计算不为形式一致强加 `async`。通过 **DI 构造函数注入**有生命周期的依赖，避免将请求状态放进静态可变成员，不使用 service locator。
- 入参校验前置；用特性/中间件统一处理鉴权、日志、限频、跨域（如 `[ApiExtension(...)]`）。

## 10. 依赖注入与生命周期

- **构造函数注入**为主；避免 service locator（`IServiceProvider.GetService` 满天飞）。
- 生命周期选择：无状态共享单例用 `Singleton`；每请求一个用 `Scoped`（如 `DbContext`/工作单元）；轻量无状态可 `Transient`。
- **不要把 `Scoped` 注入 `Singleton`**（捕获陷阱）。
- 第三方/框架装配集中在统一入口（见 §13），避免散落各处。

## 11. 性能与资源管理

- **按所有权释放资源**：自己拥有的 `IDisposable` 用 `using`，异步释放用 `await using`。DI 容器创建并管理的服务由容器或作用域释放；外部创建后注册、工厂返回及借用对象按所有权契约处理。参见 [DI 资源释放规则](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection/guidelines)。
- 字符串构建、切片、装箱及 LINQ 分配优化按实际热路径和测量结果选择 `StringBuilder`、`Span<T>` / `ReadOnlySpan<T>` 等；不为小改动扩大性能重构。
- 集合已知容量时预设容量；计数优先用 `ICollection.Count` 等 O(1) 路径，避免无谓枚举。
- **时刻与耗时分开**：记录时刻用 UTC（`DateTime.UtcNow` 或契约要求的 `DateTimeOffset.UtcNow`），展示时转时区；耗时和超时预算用 `Stopwatch`，UTC 墙上时钟仍可能被校时。需可测试时钟且 TFM 支持时用 `TimeProvider`：耗时取 `GetTimestamp` / `GetElapsedTime`，不对 `GetUtcNow` 做差，不顺手升级 TFM 或加依赖。参见 [TimeProvider](https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview)。
- **时长单位与命名**：数值时长统一毫秒（ms），用 `ConnectTimeout`、`SamplingInterval`、`Debounce`、`Duration` 等业务名，不加 `Ms` 后缀。XML 注释、OpenAPI、前端标签标明 ms，`[Range]` 等校验与单位一致；`TimeSpan`、日期时刻保留自身语义，Prometheus 指标可保留 `_ms` 等单位后缀。
- **`Dispose` 立即终止职责**：销毁时停止接受新工作，不在销毁后继续分发残留通知/事件（尤其是 `AsyncEventDispatcher` 等组件）。正在执行的任务按组件契约取消或等待；不要把释放资源理解为可强制中断任意正在运行的回调。

## 12. 安全

- **口令哈希**：使用加盐慢哈希（如 PBKDF2 / 项目已验证的 `PasswordHashHelper`），参数按当前适用的安全建议核实；禁止用 MD5/SHA 直接哈希口令。示例和默认初始化不得内置通用口令。
- **对称加密优先认证加密（AES-GCM）**；同一密钥下 nonce 不得重复，必须验证认证标签；避免 ECB，CBC 必须配合可靠的完整性校验。参见 [AesGcm.Encrypt](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.aesgcm.encrypt)。
- **密钥来源分开处理**：随机加密密钥使用密码学安全随机源或受管理密钥；只有从口令派生密钥时才使用 PBKDF2 等适当 KDF，并生成随机盐。盐与 IV/nonce 用途不同，IV/nonce 的生成和长度遵循所选算法。
- **SQL 值参数化**：ORM 查询也要检查所用 API；原生 SQL、插值和动态条件不能仅凭“用了 ORM”视为安全。表名、列名等不可作为值参数的位置使用可信映射或白名单，不拼接未验证输入。
- 最小权限；敏感配置（连接串、密钥）不以明文入库、不入仓库，使用配置/密钥管理。日志和错误响应不泄露敏感值或内部堆栈，见 §6。

## 13. 程序入口最佳实践

> Hexgen 默认分工：框架装配放在通用底座 `AppHelper`，业务初始化放在应用内 `AppSettings`，`Program.cs` 负责编排。已有项目显式架构优先；具体 API 与依赖按 §1 核实。

**`Program.cs` 保持极简**。以下是已采用相应 Hexgen 扩展方法的混合 Web 应用编排示例；核实扩展方法内部是否已注册中间件，避免重复装配。纯 API 不添加 SPA fallback；已有 `Init` 等 API 不借此示例强制改名：

```csharp
var builder = WebApplication.CreateBuilder(args);

// 业务配置及已明确要求的初始化；失败直接终止启动。
await AppSettings.InitAsync(builder);

// 框架服务装配。
builder.ConfigureServices(registerEmbeddedControllers: true);

var app = builder.Build();

app.UseHttpsRedirection();
// 框架管道装配；鉴权等顺序以已核实的底座实现为准。
app.ConfigureMiddlewares(isMixed: true);
app.UseAuthorization();
app.MapControllers();
app.MapFallbackToFile("/index.html");
app.Run();
```

**`AppSettings` 配置中心**：

- 使用 `public partial class AppSettings`，按主题用 `#region` + `partial` 分节。
- 配置沿用静态属性与私有 backing field，或使用 `{ get; private set; }` 向外提供只读值。确需懒加载的派生项保证并发安全，不在 getter 中执行建库、写种子等副作用。
- 配置统一走 `builder.Configuration`，不限定为 `appsettings.json`；必要配置缺失应报错，不用空连接串掩盖。普通配置可在初始化时赋值 `ApplicationName = builder.Configuration["Application:Name"] ?? "Hexgen";`，属性声明如下：
  ```csharp
  internal static string ApplicationName
  {
      get;
      private set;
  } = string.Empty;
  ```

**一次性初始化契约**：

- “重复调用抛异常”是一次性守卫，不是幂等。区分“已开始”和“已成功”：可能并发时原子抢占开始状态，全部步骤完成后才标记成功；重复进入抛 `InvalidOperationException`。
- 首次调用失败传播原始异常、终止启动，不复位为可重试状态，也不自动重跑可能已有副作用的建库、建表或种子步骤。
- 初始化只执行项目明确需要的步骤；静态状态的作用域须符合宿主模型。同进程多个宿主或测试实例需要隔离时，不用进程级静态标记冒充每个宿主的状态。
- 新增异步初始化 API 使用 `InitAsync`；已有 API 按 §15 维护兼容，不因范例更名，也不制造无 `await` 的异步方法。
- 底座装配沿用项目已定的重复调用契约；新的一次性装配默认拒绝重复。已明确幂等的方法保持等价状态，不套用抛异常规则。

## 14. 测试

- 测试命名：`方法_场景_预期`（如 `Encrypt_EmptyKey_Throws`）；结构使用 Arrange / Act / Assert。
- **核心通用能力必须有测试**（加解密、序列化、比较、ID 生成等），相关改动后回归；覆盖本次行为涉及的边界和异常路径，不写只复述实现或机械匹配文字的测试。
- 执行项目规定的基线和质量门槛；若要求“基线不绿立即停止”则遵循，不改命令、跳过或放宽门槛掩盖失败。
- 按变更影响选择验证范围。完成项目必需检查与相关回归后，只有新修改、失败或未解决疑点才扩大或重复测试；低影响文本/格式改动通常检查差异和格式即可。
- 测试可能启动外部进程或影响桌面时，按 `AGENTS.md` 提前说明影响。报告实际命令、结果及未覆盖内容；自动化通过不代替尚未完成的人工验收。

## 15. 多目标与兼容性

- 类库按消费者需求选择受支持的 LTS；核实 TFM、`LangVersion` 和部署约定。新 LTS 或目标 EOL 只触发升级评估，不授权自动增删 `TargetFrameworks`，历史项目迁移另定范围。
- 跨目标 API 差异按实际需求用 `#if NETx_0` 等条件处理；语言特性由 `LangVersion` 决定，运行时 API 由 TFM 决定，不为假设的兼容目标增加分支。
- **公共 API 按发布和实际消费者判断兼容性**：检查源码、二进制及相关序列化/协议契约，包括可选参数、返回类型和命名。迁移时按需使用 `[Obsolete]` 及替代 API 说明，破坏性变更按项目版本策略安排。
- 未发布、无真实消费者且项目允许直接调整时，不添加无需求的兼容别名或迁移层；不能仅以“1.0 前”推定可破坏已有消费者。
- **公共命名尽量在首次发布前定稿**；混淆后的名称保留取决于实际配置，不能假定公共 API 一定保留。涉及反射、序列化或 `dynamic` 的变更按发布产物验证。

## 16. 代码格式与控制流

- **大括号统一 Allman 风格**：左大括号独占一行（类型、方法、属性、控制流语句皆然）。
  ```csharp
  public static void ValidateApplicationName(string applicationName)
  {
      if (string.IsNullOrWhiteSpace(applicationName))
      {
          throw new ArgumentException("应用名称不能为空。", nameof(applicationName));
      }
  }
  ```
- **方法声明签名保持单行**：方法、构造函数和局部函数的返回类型、名称及完整参数列表必须写在同一行，不因参数数量或行宽主动拆行；接口方法同样适用。方法调用的实参列表不受此规则限制，复杂或嵌套调用可按可读性换行。
  ```csharp
  // 接口声明：完整签名保持单行。
  Task<ActionResult<object>> ReadAsync(string address, DataType dataType, int length = 1, CancellationToken cancellationToken = default);
  ```
- **控制流一律带大括号**：`if`/`else`/`for`/`foreach`/`while`/`do`/`using (...)`/`lock`/`try`/`catch`/`finally` 即使只有一条语句也必须带大括号，左大括号独占一行；`using var` / `await using var` 是声明，不在此列。
  ```csharp
  // 正确
  if (condition)
  {
      DoSomething();
  }

  // 错误
  if (condition) DoSomething();
  if (condition) { DoSomething(); }
  ```
- **空 `catch` 例外**：确需主动吸收异常的兜底场景可用同行 `catch { }`，必须逐处注释说明原因；不能只因处于 `Dispose` 就忽略关键释放失败。有处理代码的 `catch` 仍遵循 Allman。
  ```csharp
  try
  {
      Cleanup();
  }
  catch { /* 此可选清理不影响关键资源释放；继续后续释放，避免覆盖原始异常。 */ }
  ```

---

*本规范的默认约定服从用户明确指令及项目显式约定，适用范围见 §1。*
