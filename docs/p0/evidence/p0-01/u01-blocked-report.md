# U-01 Win10 22H2 兼容性验证 — 阻塞报告

> 关联：P0-01 补测项 U-01
> 状态：**BLOCKED**（缺少 Win10 22H2 测试环境）
> 日期：2026-10-29
> PM 要求：U-01 关闭前不启动 P0-02

## 1. PM 交付要求（原文）

1. Windows 版本、具体 Build、补丁状态及硬件信息。
2. Graphics Capture API 的实际调用结果与失败日志。
3. Session 0 / 交互用户会话的行为差异。
4. 目标桌面采集是否影响当前用户会话，以及异常退出后的进程、服务和端口清理情况。
5. 测试步骤、原始日志、截图和明确的 PASS / FAIL / BLOCKED 结论。

## 2. 环境能力评估（实测）

| 检查项 | 实测结果 | 说明 |
| --- | --- | --- |
| Hyper-V vmcompute 服务 | Running | Hyper-V 计算服务可用 |
| Hyper-V vmms 服务 | Running | Hyper-V 虚拟机管理服务可用 |
| VMware 服务 | 未发现 | — |
| VirtualBox 服务 | 未发现 | — |
| Win10 ISO 介质 | **未找到** | Downloads 仅有 debian-13.5.0-DVD-1.iso |
| 现成 Win10 VHDX | **未找到** | 常见路径无 VHDX |
| 现成 Hyper-V VM | **无连接** | Get-VM 未返回任何 VM |

**结论**：Hyper-V 平台可用，但**缺少 Win10 22H2 安装介质（ISO）或现成 VM 镜像**，无法在本环境创建 Win10 22H2 测试机。

## 3. 阻塞原因

| 阻塞项 | 说明 |
| --- | --- |
| 无 Win10 22H2 ISO | 无法创建 Win10 22H2 虚拟机 |
| 无现成 Win10 VM/VHDX | 无法直接启动测试 |
| 无物理 Win10 机器 | 内网中未发现可用的 Win10 目标机 |

## 4. 所需资源（解除阻塞条件）

满足以下任一条件即可解除阻塞：

| 方案 | 所需资源 | 说明 |
| --- | --- | --- |
| 方案 A | Win10 22H2 ISO（官方 Media Creation Tool 生成） | 放置于本机可访问路径，用 Hyper-V 创建 VM |
| 方案 B | Win10 22H2 VHDX/VM 镜像 | 现成虚拟机，直接导入 Hyper-V |
| 方案 C | 物理 Win10 22H2 机器 | 可通过网络访问的目标机，远程执行验证脚本 |

## 5. 解除阻塞后的测试计划

获得 Win10 22H2 测试机后，执行以下步骤（复用 `verify_p0_01.py`）：

| 步骤 | 内容 | 产出 |
| --- | --- | --- |
| 1 | 在 Win10 22H2 上运行 `verify_p0_01.py` | environment.json, session-verification.json |
| 2 | 记录 OS 版本/Build/补丁/硬件 | 环境清单 |
| 3 | 验证 Graphics Capture API 调用 | 成功/失败日志（Build 19045 ≥ 18362 预期可用） |
| 4 | 验证 Session 0 / 交互会话隔离 | query session + 进程会话分布 |
| 5 | 验证桌面采集不影响当前用户会话 | 采集前后用户操作对比 |
| 6 | 验证异常退出后进程/服务/端口清理 | 零残留复测 |
| 7 | 记录测试步骤、原始日志、截图 | 证据文件 |
| 8 | 给出 PASS / FAIL / BLOCKED 结论 | 验收记录 |

## 6. 当前结论

**U-01 = BLOCKED**

- 无法在当前环境完成 Win10 22H2 兼容性验证。
- 需 PM 提供以下任一资源：Win10 22H2 ISO / VHDX 镜像 / 物理测试机。
- 资源到位后，预计可在创建/配置测试机后完成验证。
- **在 U-01 关闭前，不启动 P0-02**（遵循 PM 执行指令）。

## 7. 不变量

- 不伪造 Win10 测试结果。
- 不将 Win11 24H2 单机结果推广为全平台兼容结论。
- 产品编码 NOT AUTHORIZED 不变。