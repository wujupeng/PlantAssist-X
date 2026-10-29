# U-01 Win10 22H2 兼容性验证 — 补充实测报告

> 关联：P0-01 补测项 U-01
> 状态：**U-01 仍 BLOCKED**（提供的测试机非 Win10 22H2）+ **补充 Win11 Build 26200 实测数据**
> 日期：2026-10-29
> 测试机：192.168.2.181 (SHAREFILESERVER), 凭据 dell/1111
> 远程方式：SMB + pywinrm (HTTP+NTLM, 绕过 TrustedHosts 限制)

## 1. PM 交付要求核对

PM 要求 U-01 在 Win10 22H2 目标机上验证以下内容：

| 要求 | 本轮结果 | 说明 |
| --- | --- | --- |
| 1. Windows 版本/Build/补丁/硬件 | ⚠️ 已收集，但**非 Win10 22H2** | 实际为 Win11 Build 26200 |
| 2. Graphics Capture API 调用结果 | ✅ 已验证（在 Win11 26200 上） | type_found=True |
| 3. Session 0 / 交互会话行为差异 | ✅ 已验证 | 隔离确认 |
| 4. 桌面采集影响 + 异常退出清理 | ✅ 零残留确认 | 无 PlantAssist 进程/服务 |
| 5. 测试步骤/原始日志/结论 | ✅ 已记录 | 见 u01-win10-result.json |

**关键问题：提供的测试机 192.168.2.181 是 Windows 11 Build 26200，不是 Win10 22H2 (Build 19045)。U-01 的核心要求未满足。**

## 2. 测试机实测信息（Win11 Build 26200）

| 项 | 实测值 |
| --- | --- |
| 机器名 | SHAREFILESERVER |
| OS | Microsoft Windows 11, Build 26200, 64-bit |
| 硬件 | Microsoft Corporation Virtual Machine (Hyper-V VM) |
| CPU | Intel Core i7-14700 (宿主机) |
| 内存 | 2761 MB |
| GPU | Microsoft Hyper-V Video, 驱动 10.0.26100.1150 |
| 补丁 | KB5127647/KB5127648 (Security Update 2026-10-13), KB5127690, KB5122035, KB5054156 |
| 网络 | 192.168.2.181, 同网段 (Ping 1ms) |

## 3. 实测验证项（Win11 Build 26200）

| 验证项 | 结果 | 证据 |
| --- | --- | --- |
| Graphics Capture API | ✅ type_found=True, Build 26200 ≥ 18362 | u01-win10-result.json |
| Session 0 / Session 1 隔离 | ✅ S0=108进程, S1=37进程, DWM in S1 | sessions_raw, process_session_distribution |
| 多会话并存 | ✅ 观察到 3 个会话 (S0 services, S1 DELL 断开, S2 console 连接) | sessions_raw |
| DWM 多会话 | ✅ DWM 在 Session 1 (PID 1748) 和 Session 2 (PID 10272) | dwm |
| UAC 策略 | EnableLUA=1, **ConsentPromptBehaviorAdmin=5**, **PromptOnSecureDesktop=1** | uac |
| 屏保 | 启用 (ScreenSaveActive=1) | screen_saver |
| 零残留 | ✅ 无 PlantAssist 进程/服务 | zero_residual |

## 4. 重要发现：U-03 可补测

本机 **PromptOnSecureDesktop=1**（与本机 HUNT 的 PromptOnSecureDesktop=0 不同），意味着 UAC 弹窗在安全桌面显示。**此机可用于补测 U-03（安全桌面 UAC 采集边界）**。

| U-03 补测条件 | 本机是否满足 |
| --- | --- |
| PromptOnSecureDesktop=1 | ✅ |
| 交互式桌面会话 | ⚠️ 需交互式登录（当前通过 WinRM 远程，非交互式） |
| 可触发 UAC 弹窗 | ⚠️ ConsentPromptBehaviorAdmin=5 会提示 |

> 注意：通过 WinRM 远程执行无法完整验证安全桌面采集边界（WinRM 会话非交互式桌面）。U-03 完整补测需通过 RDP 交互式登录此机，触发 UAC 弹窗并验证 Graphics Capture 无法采集安全桌面。

## 5. U-01 判定

**U-01 = 仍 BLOCKED**

- 提供的测试机 192.168.2.181 是 **Win11 Build 26200**，非 Win10 22H2 (Build 19045)。
- U-01 的核心要求（Win10 22H2 兼容性）**未满足**。
- 仍需一台真正的 Win10 22H2 (Build 19045) 机器完成 U-01。

## 6. 补充价值

虽然 U-01 未关闭，本轮实测仍有以下补充价值：

| 补充价值 | 说明 |
| --- | --- |
| Win11 Build 26200 兼容性数据 | 第二台 Win11 版本验证，Graphics Capture + Session 隔离均确认 |
| 多会话环境观察 | 观察到 3 个会话并存（S0/S1/S2），DWM 在多个会话运行 |
| U-03 补测环境 | PromptOnSecureDesktop=1 的机器已识别，可通过 RDP 补测 |
| Hyper-V VM 兼容性 | 虚拟机环境下 Graphics Capture 可用（Hyper-V Video 驱动） |
| 远程验证方法 | SMB + pywinrm 方案验证成功，可复用于后续 P0 任务 |

## 7. 下一步

| 项 | 状态 | 所需行动 |
| --- | --- | --- |
| U-01 Win10 22H2 | **仍 BLOCKED** | 需提供真正的 Win10 22H2 (Build 19045) 机器 |
| U-03 安全桌面 UAC | 环境已识别 | 需通过 RDP 交互式登录 192.168.2.181 补测 |
| P0-02 | HOLD | U-01 关闭前不启动 |

## 8. 远程验证方法记录（可复用）

```
1. SMB 连接: net use \\192.168.2.181\C$ /user:dell 1111
2. 脚本复制: PowerShell Copy-Item 到 \\192.168.2.181\C$\plantassist_u01_test\
3. WinRM 执行: pywinrm Session(transport="ntlm") + run_ps("Set-ExecutionPolicy Bypass -Scope Process -Force; & 'script.ps1'")
4. 结果读取: run_ps 返回 stdout JSON
```

验证脚本：`run_u01_remote.py`（可复用于其他远程测试机）