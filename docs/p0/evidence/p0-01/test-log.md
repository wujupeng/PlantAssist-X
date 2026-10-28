# P0-01 测试日志 — Windows 桌面会话验证

> 任务：P0-01 平台兼容性
> 执行日期：2026-10-28
> 测试机：HUNT (Dell Inspiron 14 Plus 7440, Win11 24H2 Build 26100)
> 验证脚本：`verify_p0_01.py`
> 证据文件：`environment.json`, `session-verification.json`

## 1. 测试环境清单（实测）

| 项 | 实测值 |
| --- | --- |
| OS | Microsoft Windows 11 专业版 |
| 版本/Build | 10.0.26100 (24H2) |
| 架构 | 64-bit |
| 硬件 | Dell Inspiron 14 Plus 7440 |
| CPU | 12th Gen Intel Core i5-12450H |
| 内存 | 16069 MB |
| 主显卡 | Intel UHD Graphics, 驱动 32.0.101.7085, 1920x1080@60Hz |
| 虚拟显示 | OrayIddDriver Device, 驱动 17.50.19.949（向日葵第三方远控，环境现状） |
| 补丁 | KB5127647, KB5127648 (Security Update), KB5127690, 安装于 2026-10-14 |
| 显示器 | 1 屏 1920x1080, DPI 96 (100%) |
| 网络 | 192.168.2.17/24, 网关 192.168.2.254 (vEthernet wan) |
| 防火墙 | Domain/Private/Public 全部启用 |
| 当前用户 | hunt (HUNT), Session 1 (console), 管理员权限 |

## 2. Windows 会话模型验证（实测）

### 2.1 会话列表（query session 实测）

| 会话名 | 用户 | Session ID | 状态 | 类型 |
| --- | --- | --- | --- | --- |
| services | — | 0 | 断开 | 无交互桌面 |
| console | hunt | 1 | 运行中 | 交互桌面 |
| rdp-tcp | — | 65536 | 侦听 | RDP（未连接） |

### 2.2 进程会话分布（实测）

| Session ID | 进程数 | 说明 |
| --- | --- | --- |
| 0 | 155 | 后台服务（LocalSystem/LocalService） |
| 1 | 150 | 交互用户进程（DWM PID=1584, Explorer PID=11576） |

### 2.3 隔离结论

**Session 0 与 Session 1 隔离已确认。**

- DWM（桌面窗口管理器）和 Explorer 运行于 **Session 1**，不在 Session 0。
- 155 个服务进程运行于 **Session 0**，无交互桌面。
- 后台服务（Session 0）**无法直接访问** Session 1 的交互桌面 GDI/Direct3D 资源。
- **验证了权限分离架构的前提**：后台服务负责身份/策略，交互客户端在用户会话负责画面/输入，两者通过认证 IPC 通信。

## 3. 桌面采集 API 可用性（实测）

| 验证项 | 结果 |
| --- | --- |
| `Windows.Graphics.Capture.GraphicsCaptureItem` 类型加载 | **成功** |
| OS Build (26100) >= 18362 (Graphics Capture 最低要求) | **是** |
| OS Build (26100) >= 22621 (Win11 22H2) | **是** |

**结论**：Windows Graphics Capture API 在本测试机可用，桌面采集技术路径可行。P0-02 将进一步验证采集性能。

## 4. UAC 与锁屏策略（实测查询，未实际触发）

| 策略项 | 实测值 | 说明 |
| --- | --- | --- |
| EnableLUA | 1 | UAC 已启用 |
| ConsentPromptBehaviorAdmin | 0 | 管理员提权不提示（当前账户已是管理员） |
| ConsentPromptBehaviorUser | 3 | 标准用户提权提示凭据 |
| PromptOnSecureDesktop | 0 | **UAC 弹窗不在安全桌面显示** |
| ScreenSaveActive | 1 | 屏保已启用，可能触发锁屏 |

### 关键发现

- **PromptOnSecureDesktop=0**：本机 UAC 弹窗不在安全桌面（Secure Desktop）显示，因此**无法在本机实测安全桌面采集边界**。需在 `PromptOnSecureDesktop=1` 的专用测试机补测。
- **屏保启用**：系统屏保可能触发锁屏。PlantAssist-X 设计为"不主动锁屏"，但**不能阻止系统屏保/电源策略触发的锁屏**，此为 Windows 系统行为，非本系统可控。需在限制清单中明确。

## 5. 会话场景边界验证

| 场景 | 验证方式 | 结果 | 说明 |
| --- | --- | --- | --- |
| 用户已登录 | 实测 | **支持** | Session 1 活跃，DWM/Explorer 运行，可采集 |
| 锁屏 | 策略查询 | **需补测** | 屏保启用可能触发；未实际锁屏（避免干扰用户工作） |
| 解锁 | — | **需补测** | 需在专用测试机实测会话恢复 |
| 切换用户 | — | **需补测** | 快速用户切换策略未禁用；需实测多会话并存 |
| UAC 弹窗 | 策略查询 | **需补测** | 本机 PromptOnSecureDesktop=0，无法实测安全桌面边界 |
| 用户注销 | — | **需补测** | 需实测会话终止与权限清理 |
| 服务重启 | 零残留基线 | **基线确认** | 当前无 PlantAssist 进程/服务/端口 |
| 网络中断 | — | **需补测** | 需在 P0-04 网络验证中实测 |

> **未实际触发锁屏/注销/切换用户的原因**：当前测试机为用户工作环境，实际触发会中断用户工作，违反"不干扰现有工作"原则。这些场景需在专用隔离测试机补测。

## 6. 权限清理基线（实测）

| 检查项 | 结果 |
| --- | --- |
| PlantAssist 进程 | 未发现（0 个） |
| PlantAssist 服务 | 未发现（0 个） |
| PlantAssist 监听端口 | 未发现 |

**零残留基线已确认**。此为权限清理验证的起点状态。后续实现后，需验证服务重启/网络中断后恢复到此基线（无残留控制权限）。

## 7. 验证脚本可复现性

`verify_p0_01.py` 可在任意 Windows 机器上运行，自动收集环境/会话/采集API/UAC/零残留信息并输出 JSON 证据。

```bash
python docs/p0/evidence/p0-01/verify_p0_01.py
```

输出：`environment.json`, `session-verification.json`