# U-03 安全桌面 UAC 边界测试 — 测试步骤与准备材料

> 状态：**准备材料完成，待实测**（PM 指令：不得将准备记为验收通过）
> 关联：P0-01 补测项 U-03
> 目标机：192.168.2.181 (SHAREFILESERVER, Win11 Build 26200, **PromptOnSecureDesktop=1**)
> 日期：2026-10-29

## 1. 测试目标

验证 **Graphics Capture API 无法采集安全桌面（UAC 提权弹窗）**，确认 L-01 限制成立。

| 验证项 | 预期 |
| --- | --- |
| UAC 弹窗显示位置 | 安全桌面（PromptOnSecureDesktop=1） |
| UAC 弹窗期间 Graphics Capture | 黑屏 / 中断 / 冻结 / 无法采集 |
| UAC 关闭后 Graphics Capture | 恢复采集正常桌面 |
| 结论 | Graphics Capture 不支持安全桌面，L-01 成立 |

## 2. 前置条件

| 条件 | 状态 | 说明 |
| --- | --- | --- |
| PromptOnSecureDesktop=1 | ✅ 192.168.2.181 已确认 | u01-win10-result.json |
| 交互式桌面会话 | ⚠️ 需 RDP 登录 | WinRM 远程会话非交互式，无法触发 UAC 弹窗 |
| 管理员账户 | ✅ dell/1111 | ConsentPromptBehaviorAdmin=5 会提示 |
| Graphics Capture API | ✅ 可用 | type_found=True |

## 3. 测试步骤

### 步骤 1：RDP 登录目标机

```
mstsc /v:192.168.2.181
用户名: dell
密码: 1111
```

确认登录到交互式桌面会话（Console 或 RDP-Tcp）。

### 步骤 2：复制并运行验证脚本

在 RDP 会话中打开 PowerShell（管理员），执行：

```powershell
# 复制脚本（从本机 SMB 共享，或手动复制）
python verify_u03_secure_desktop.py
```

或手动执行测试逻辑：

```powershell
# 1. 确认 UAC 策略
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" | Select-Object EnableLUA, ConsentPromptBehaviorAdmin, PromptOnSecureDesktop

# 2. 启动 Graphics Capture 采集（需实现最小采集原型或使用现成工具）
#    - 持续采集当前桌面帧
#    - 记录帧是否正常（非全黑）

# 3. 触发 UAC 提权弹窗
Start-Process "cmd.exe" -Verb RunAs

# 4. 观察 UAC 弹窗期间采集画面
#    - 预期：画面冻结/黑屏/无法更新
#    - 截图记录

# 5. 在 UAC 弹窗上点击"是"或"否"
#    - 观察采集是否恢复

# 6. 记录结论
```

### 步骤 3：记录证据

| 证据项 | �*录方式 |
| --- | --- |
| UAC 策略 | 脚本自动记录 JSON |
| UAC 弹窗截图 | 手动截图（RDP 会话中 PrintScreen） |
| 弹窗前采集画面 | 截图 |
| 弹窗期间采集画面 | 截图（预期黑屏/冻结） |
| 弹窗后采集画面 | 截图 |
| 结论 | PASS（L-01 成立）/ FAIL / BLOCKED |

### 步骤 4：保存证据

将以下文件保存到 `docs/p0/evidence/p0-03/`：

- `u03-secure-desktop-result.json`（脚本自动生成）
- `u03-screenshot-before-uac.png`（弹窗前采集）
- `u03-screenshot-during-uac.png`（弹窗期间采集）
- `u03-screenshot-after-uac.png`（弹窗后采集）
- `u03-test-log.md`（手动记录观察结果）

## 4. 远程预测试（可执行部分）

以下可通过 WinRM 远程执行（无需交互式登录），但**不构成 U-03 完整验证**：

| 预测试项 | 方式 | 预期 |
| --- | --- | --- |
| UAC 策略确认 | pywinrm 查询注册表 | PromptOnSecureDesktop=1 ✅ 已确认 |
| Graphics Capture 可用性 | pywinrm 查询 WinRT 类型 | type_found=True ✅ 已确认 |
| 安全桌面存在性 | pywinrm 查询 Win32_Desktop | 确认 Default/Desktop 区分 |
| 交互式会话检查 | pywinrm 查询 SESSIONNAME | WinRM 会话非交互式（无法触发 UAC） |

## 5. 限制说明

- **WinRM 远程会话无法触发交互式 UAC 弹窗**：WinRM 运行在非交互式会话中，Start-Process -Verb RunAs 在 WinRM 中行为不同（可能直接失败或无弹窗）。
- **完整 U-03 测试必须通过 RDP 交互式登录**。
- **Graphics Capture 采集需要最小原型**：P0-02 将建立采集原型，U-03 完整测试可能需在 P0-02 后进行。
- 本准备材料**不等于 U-03 已通过**。

## 6. 与 P0 任务顺序的关系

| 项 | 状态 |
| --- | --- |
| U-03 完整测试 | 需 RDP 交互式登录 + Graphics Capture 原型 |
| Graphics Capture 原型 | P0-02 产出 |
| P0-02 启动 | 需 U-01 关闭 |
| U-01 关闭 | 需 Win10 22H2 环境 |

> U-03 完整测试可能在 P0-02 采集原型就绪后才能执行。当前仅准备测试脚本和步骤。