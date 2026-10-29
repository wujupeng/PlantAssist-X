# U-03 安全桌面 UAC 边界 — 预测试报告

> 状态：**预测试完成，U-03 未通过**（PM 指令：不得将准备记为验收通过）
> 关联：P0-01 补测项 U-03
> 目标机：192.168.2.181 (SHAREFILESERVER)
> 日期：2026-10-29
> 方式：pywinrm 远程预测试（可执行部分）

## 1. 预测试结果

| 验证项 | 结果 | 说明 |
| --- | --- | --- |
| UAC EnableLUA | 1 | UAC 已启用 |
| ConsentPromptBehaviorAdmin | 5 | 管理员提权提示同意 |
| **PromptOnSecureDesktop** | **1** | **UAC 弹窗在安全桌面显示** ✅ |
| Graphics Capture API | type_found=True | 可用 |
| WinRM 会话交互式 | **false** | WinRM 非交互式，无法触发 UAC 弹窗 |
| .DEFAULT 桌面存在 | ✅ | 安全桌面（Winlogon）已识别 |

## 2. 桌面枚举（实测）

| 桌面名 | 类型 |
| --- | --- |
| NT AUTHORITY\SYSTEM | 系统桌面 |
| NT AUTHORITY\LOCAL SERVICE | 服务桌面 |
| NT AUTHORITY\NETWORK SERVICE | 服务桌面 |
| SHAREFILESERVER\DELL | 用户桌面 |
| **.DEFAULT** | **安全桌面（Winlogon/UAC）** |

`.DEFAULT` 桌面的存在确认了安全桌面与用户桌面的分离，UAC 弹窗（PromptOnSecureDesktop=1）将在此桌面显示。

## 3. 预测试结论

| 项 | 结论 |
| --- | --- |
| U-03 测试环境条件满足 | ✅ PromptOnSecureDesktop=1 |
| Graphics Capture 可用 | ✅ |
| 安全桌面存在 | ✅ .DEFAULT |
| 完整测试需 RDP 交互式登录 | ✅ WinRM 无法触发 UAC 弹窗 |
| **U-03 是否通过** | **否 — 仅预测试，未完成完整验证** |

## 4. 完整测试待执行项

| 待执行项 | 条件 | 状态 |
| --- | --- | --- |
| RDP 登录 192.168.2.181 | 交互式桌面会话 | 待执行 |
| 启动 Graphics Capture 采集 | 需采集原型（P0-02 产出） | 待 P0-02 |
| 触发 UAC 提权弹窗 | 交互式会话中 Start-Process -Verb RunAs | 待执行 |
| 记录弹窗期间采集画面 | 截图（预期黑屏/冻结） | 待执行 |
| 记录弹窗后采集恢复 | 截图 | 待执行 |
| 给出 PASS/FAIL/BLOCKED 结论 | 完整证据 | 待执行 |

## 5. 依赖关系

```
U-03 完整测试
  ├── 需 RDP 交互式登录 192.168.2.181 ✅ 环境已识别
  ├── 需 Graphics Capture 采集原型 ← P0-02 产出
  └── P0-02 需 U-01 关闭 ← 需 Win10 22H2 环境（仍 BLOCKED）
```

> U-03 完整测试依赖 P0-02 采集原型，而 P0-02 依赖 U-01 关闭。当前 U-01 仍 BLOCKED。

## 6. 已准备材料

| 材料 | 文件 | 状态 |
| --- | --- | --- |
| U-03 验证脚本 | `verify_u03_secure_desktop.py` | ✅ 已准备 |
| U-03 测试步骤文档 | `u03-test-procedure.md` | ✅ 已准备 |
| U-03 预测试结果 | `u03-pretest-result.json` | ✅ 远程预测试 |
| U-03 预测试报告 | `u03-pretest-report.md`（本文件） | ✅ |

## 7. 不变量

- 本预测试**不等于 U-03 已通过**。
- 完整 U-03 测试需 RDP 交互式登录 + Graphics Capture 原型。
- U-03 完整测试可能在 P0-02 后执行。
- 产品编码 NOT AUTHORIZED 不变。