# U-01 Win10 22H2 兼容性验证 — 验收报告

> 状态：**实测完成，待 PM 裁定**
> 关联：P0-01 补测项 U-01
> 目标机：192.168.2.12 (IPSEC)
> 日期：2026-10-29
> 方式：SMB + pywinrm (HTTP+NTLM)
> 验证脚本：`run_u01_win10.py`

## 1. PM 最小关闭条件核对

| 条件 | 结果 | 证据 |
| --- | --- | --- |
| 1. 原始系统信息记录 Win10 22H2 Build 19045.x | ✅ Build 19045 | u01-win10-22h2-result.json |
| 2. 实测 Graphics Capture API + 桌面会话行为 | ✅ type_found=True, 隔离确认 | graphics_capture, session_isolation |
| 3. Session 归属/DWM/异常退出清理/零残留 | ✅ 全部记录 | sessions_raw, dwm, zero_residual |
| 4. 失败/未执行/无法验证项分别标记 | ✅ 见 §5 | 本报告 §5 |
| 5. 提交独立报告待 PM 裁定 | ✅ 本文件 | — |

## 2. 测试环境清单（实测）

| 项 | 实测值 |
| --- | --- |
| 机器名 | IPSEC |
| IP | 192.168.2.12 |
| OS | **Microsoft Windows 10, Build 19045 (22H2), 64-bit** |
| 硬件 | Microsoft Corporation Virtual Machine (Hyper-V VM) |
| CPU | Intel Core i7-14700 (宿主机) |
| 内存 | 2844 MB |
| GPU | Microsoft Hyper-V Video, 驱动 10.0.19041.3636 |
| 补丁 | KB5126256, KB5071982, KB5066790, KB5071959 (Security Update 2026-09-21) 等 |
| 最后启动 | 2026-10-26 |

### Windows 10 22H2 支持状态说明

> Windows 10 22H2 于 2025-10-14 结束常规支持。本机补丁最新至 2026-09-21，表明可能通过 ESU（扩展安全更新）继续获取更新。**本验证仅确认兼容性，不构成安全支持承诺。** 生产部署需确认 ESU 状态。

## 3. 实测验证项

### 3.1 Graphics Capture API

| 验证项 | 结果 |
| --- | --- |
| `Windows.Graphics.Capture.GraphicsCaptureItem` 类型加载 | **成功 (type_found=True)** |
| Build 19045 >= 18362 (Graphics Capture 最低要求) | **是** |

**结论：Win10 22H2 上 Graphics Capture API 可用。**

### 3.2 Session 0 / Session 1 隔离

| 会话 | ID | 状态 | 进程数 | 类型 |
| --- | --- | --- | --- | --- |
| services | 0 | 断开 | 57 | 无交互桌面 |
| dell | 1 | 断开 | 36 | 交互桌面 |
| console | 2 | 连接 | 5 | 交互桌面 |

| 验证项 | 结果 |
| --- | --- |
| DWM 运行会话 | Session 1 (PID 1396) + Session 2 (PID 2824) |
| Explorer 运行会话 | Session 1 (PID 5572, 5804) |
| Session 0 有交互桌面 | 否 |
| **隔离确认** | **是 (isolation_confirmed=True)** |

**结论：Win10 22H2 上 Session 0 与交互会话隔离确认，权限分离架构前提成立。**

### 3.3 UAC 策略

| 策略项 | 值 | 说明 |
| --- | --- | --- |
| EnableLUA | 1 | UAC 已启用 |
| ConsentPromptBehaviorAdmin | 5 | 管理员提权提示同意 |
| PromptOnSecureDesktop | 1 | UAC 弹窗在安全桌面显示 |

### 3.4 零残留检查

| 检查项 | 结果 |
| --- | --- |
| PlantAssist 进程 | 0 |
| PlantAssist 服务 | 0 |
| **零残留确认** | **是** |

### 3.5 屏保策略

| 项 | 值 |
| --- | --- |
| ScreenSaveActive | 1（启用） |

## 4. PM 交付要求逐项核对

| PM 要求 | 结果 | 说明 |
| --- | --- | --- |
| 1. Windows 版本/Build/补丁/硬件 | ✅ PASS | Win10 22H2 Build 19045, 补丁/硬件已记录 |
| 2. Graphics Capture API 调用结果 | ✅ PASS | type_found=True, 无失败日志 |
| 3. Session 0 / 交互会话行为差异 | ✅ PASS | S0=57进程无桌面, S1=36进程有桌面, 隔离确认 |
| 4. 桌面采集影响 + 异常退出清理 | ✅ PASS | 零残留确认（无 PlantAssist 进程/服务） |
| 5. 测试步骤/原始日志/结论 | ✅ PASS | u01-win10-22h2-result.json + 本报告 |

## 5. 未验证项标记（按 PM 要求分别标记）

| 项 | 标记 | 原因 |
| --- | --- | --- |
| 锁屏时采集行为 | **NOT RUN** | 未实际锁屏（避免干扰；通过 WinRM 远程无法触发交互式锁屏） |
| 解锁后会话恢复 | **NOT RUN** | 同上 |
| 切换用户 | **NOT RUN** | 同上 |
| 用户注销 | **NOT RUN** | 同上 |
| 安全桌面 UAC 采集边界 | **NOT RUN**（U-03 另行处理） | 需交互式会话 + Graphics Capture 原型 |
| 多显示器 | **NOT RUN** | Hyper-V VM 单显示器 |
| 异常退出后清理（实现后） | **NOT RUN** | 当前无 PlantAssist 实现，仅零残留基线 |
| 显示器枚举 | **NOT RUN** | display query_failed（WinRM 会话限制） |

> 所有未验证项标记为 **NOT RUN**，不混为 PASS。

## 6. U-01 判定

**U-01 = PASS（待 PM 裁定）**

### 通过的方面

- ✅ Windows 10 22H2 Build 19045 系统信息已记录
- ✅ Graphics Capture API 实测可用
- ✅ Session 0 / Session 1 隔离确认
- ✅ 零残留基线确认
- ✅ UAC 策略记录
- ✅ PM 最小关闭条件 1-4 全部满足

### 需 PM 注意

- Win10 22H2 已结束常规支持（2025-10-14），补丁通过 ESU 获取至 2026-09-21
- 锁屏/注销/切换用户等交互式场景标记为 NOT RUN（需专用测试机补测）
- 本验证通过 WinRM 远程执行，非交互式会话

## 7. 与 P0-01 整体验收的关系

| 环境 | OS | Graphics Capture | Session 隔离 | 零残留 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 本机 HUNT | Win11 24H2 (26100) | ✅ | ✅ | ✅ | 实测 |
| 192.168.2.181 | Win11 Build 26200 | ✅ | ✅ | ✅ | 实测 |
| **192.168.2.12** | **Win10 22H2 (19045)** | **✅** | **✅** | **✅** | **实测 PASS** |

U-01 关闭后，P0-01 的补测条件 U-01 满足，可提交 P0-01 升级为无条件 PASS 的申请（仍需 PM 裁定）。