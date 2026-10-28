# P0-01 验收结论

> 任务：P0-01 平台兼容性 — Windows 桌面会话验证
> 验收日期：2026-10-28
> 验收基线提交：见 evidence-index.md

## 1. 交付物清单

| 交付物 | 文件 | 状态 |
| --- | --- | --- |
| 验证脚本（可复现） | `verify_p0_01.py` | ✅ |
| 环境清单 JSON | `environment.json` | ✅ |
| 会话验证 JSON | `session-verification.json` | ✅ |
| 测试日志 | `test-log.md` | ✅ |
| OS 兼容性矩阵 | `os-compatibility-matrix.md` | ✅ |
| 限制清单 | `limitations.md` | ✅ |
| 验收结论 | `acceptance.md`（本文件） | ✅ |

## 2. 通过条件核对

| 通过条件（来自 tasks.md） | 结果 | 证据 |
| --- | --- | --- |
| 所有声明支持的场景有实际证据 | **部分满足** | 用户已登录场景实测；锁屏/注销/切换用户需补测 |
| 不支持场景有明确边界 | **满足** | limitations.md 列出 L-01~L-06 明确不支持项 |

## 3. 实测验证项

| 验证项 | 结论 | 证据位置 |
| --- | --- | --- |
| Win11 24H2 发起端 OS/补丁/硬件 | ✅ 实测 | environment.json, test-log.md §1 |
| Session 0 与 Session 1 隔离 | ✅ 实测确认 | session-verification.json, test-log.md §2 |
| Graphics Capture API 可用 | ✅ 实测可用 | session-verification.json, test-log.md §3 |
| UAC 策略 | 🔶 查询确认 | test-log.md §4 |
| 屏保策略 | 🔶 查询确认（启用） | test-log.md §4 |
| 零残留基线 | ✅ 实测确认 | session-verification.json, test-log.md §6 |
| 权限分离架构前提成立 | ✅ 推定 | Session 0/1 隔离 → 后台服务+交互客户端+IPC 架构可行 |

## 4. 需补测项（不阻塞 P0-02，但需在 P0-03 前关闭）

| 补测项 | 关联 | 优先级 |
| --- | --- | --- |
| Win10 22H2 目标机兼容性 | U-01 | 高（P0-02 前需至少 1 台 Win10） |
| 安全桌面 UAC 采集边界 | U-03 | 高（P0-03 输入验证前必须关闭） |
| 锁屏/注销/切换用户实际触发 | U-04~U-07 | 中（需专用隔离测试机） |
| 多显示器采集 | U-08 | 中（P0-02） |

## 5. 验收裁定

**P0-01 = 有条件通过（CONDITIONAL PASS）**

### 通过的方面

- 测试环境清单完整且可复现。
- Windows 会话模型隔离已实测确认，权限分离架构前提成立。
- Graphics Capture API 可用性已实测。
- 不支持场景边界明确（L-01~L-06）。
- 零残留基线已确认。

### 条件（需后续关闭）

1. 需在专用隔离测试机补测锁屏/解锁/切换用户/注销场景（U-04~U-07）。
2. 需在 `PromptOnSecureDesktop=1` 的机器补测安全桌面 UAC 边界（U-03），**P0-03 前必须关闭**。
3. 需至少 1 台 Win10 22H2 目标机验证兼容性（U-01）。

### 不阻塞 P0-02 的理由

P0-02（双向屏幕技术验证）可在当前 Win11 24H2 测试机上进行单机采集/编码/解码验证，补测项可在获得目标机后追加。但 P0-03（输入与安全协议）前必须关闭 U-03 安全桌面边界。

## 6. 与 Gate B 整改条件的关系

PM Gate B 裁定要求 P0-03 协议实现前关闭密钥层级（DG-03-A）、标准 TLS 实现（DG-04-A）、撤权最坏情况（DG-04-B）。本验收不涉及这些项，它们仍为 P0-03 前置条件，状态不变。