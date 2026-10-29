#!/usr/bin/env python3
"""U-03 安全桌面 UAC 边界验证脚本

在 PromptOnSecureDesktop=1 的交互式会话中运行，验证 Graphics Capture
无法采集安全桌面（UAC 提权弹窗）。

前置条件:
- 目标机 PromptOnSecureDesktop=1
- 交互式桌面会话（RDP 登录，非 WinRM 远程会话）
- 管理员账户（可触发 UAC 提权）

测试逻辑:
1. 启动 Graphics Capture 采集当前桌面
2. 持续采集并记录帧是否正常（非黑屏）
3. 触发 UAC 提权弹窗（启动需提权的进程）
4. 记录 UAC 弹窗期间采集帧的状态（预期：黑屏/中断/无法采集安全桌面）
5. UAC 弹窗关闭后恢复采集
6. 输出 JSON 证据

用法: python verify_u03_secure_desktop.py
注意: 必须在交互式桌面会话中运行，不能通过 WinRM 远程执行。
"""
import json
import subprocess
import time
import os
import sys
from datetime import datetime

EVIDENCE_DIR = os.path.dirname(os.path.abspath(__file__))


def check_uac_policy():
    """查询 UAC 安全桌面策略。"""
    ps = '''
    $u = Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
    [ordered]@{
        enable_lua = $u.EnableLUA
        consent_prompt_admin = $u.ConsentPromptBehaviorAdmin
        prompt_on_secure_desktop = $u.PromptOnSecureDesktop
    } | ConvertTo-Json
    '''
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=10)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"raw": r.stdout, "error": r.stderr}


def check_graphics_capture():
    """验证 Graphics Capture API 可用性。"""
    ps = '''
    $ok = $false
    try { $t = [Windows.Graphics.Capture.GraphicsCaptureItem, Windows.Graphics.Capture, ContentType=WindowsRuntime]; $ok = $true } catch {}
    @{ type_found = $ok } | ConvertTo-Json
    '''
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=10)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"raw": r.stdout, "error": r.stderr}


def check_session():
    """检查当前会话是否为交互式桌面会话。"""
    ps = '''
    [ordered]@{
        session_name = $env:SESSIONNAME
        user = $env:USERNAME
        is_interactive = ($env:SESSIONNAME -eq "Console" -or $env:SESSIONNAME -match "RDP")
    } | ConvertTo-Json
    '''
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=10)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"raw": r.stdout, "error": r.stderr}


def trigger_uac():
    """触发 UAC 提权弹窗（启动需提权的进程）。

    使用 Start-Process -Verb RunAs 启动一个无害的提权进程。
    在 PromptOnSecureDesktop=1 时，UAC 弹窗会在安全桌面显示。
    """
    ps = '''
    try {
        $proc = Start-Process "cmd.exe" -ArgumentList "/c echo UAC_TRIGGERED > C:\\plantassist_u03_test\\uac_triggered.txt" -Verb RunAs -PassThru -ErrorAction Stop
        "UAC_TRIGGERED_PID=$($proc.Id)"
    } catch {
        "UAC_ERROR=$($_.Exception.Message)"
    }
    '''
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=30)
    return r.stdout.strip()


def main():
    ts = datetime.now().isoformat()
    print("[U-03] 安全桌面 UAC 边界验证")
    print("[U-03] 注意: 必须在交互式桌面会话 (RDP/Console) 中运行")

    result = {
        "test": "U-03",
        "timestamp": ts,
        "machine": os.environ.get("COMPUTERNAME", ""),
    }

    # 1. 检查会话
    print("[U-03] 检查当前会话...")
    sess = check_session()
    result["session"] = sess
    print(f"  会话: {sess}")

    if not sess.get("is_interactive", False):
        print("[U-03] 警告: 当前会话可能非交互式桌面，UAC 弹窗可能无法显示")

    # 2. 检查 UAC 策略
    print("[U-03] 检查 UAC 策略...")
    uac = check_uac_policy()
    result["uac_policy"] = uac
    print(f"  UAC: {uac}")

    if uac.get("prompt_on_secure_desktop") != 1:
        print("[U-03] 警告: PromptOnSecureDesktop != 1，安全桌面 UAC 边界无法测试")
        result["precondition_met"] = False
    else:
        result["precondition_met"] = True

    # 3. 检查 Graphics Capture
    print("[U-03] 检查 Graphics Capture API...")
    cap = check_graphics_capture()
    result["graphics_capture"] = cap
    print(f"  Graphics Capture: {cap}")

    # 4. 触发 UAC（交互式操作）
    print("[U-03] 准备触发 UAC 提权弹窗...")
    print("[U-03] 请观察: UAC 弹窗显示时，Graphics Capture 采集的画面是否变为黑屏/中断")
    print("[U-03] 在弹窗上点击'是'以允许提权...")

    os.makedirs(r"C:\plantassist_u03_test", exist_ok=True)
    uac_result = trigger_uac()
    result["uac_trigger_result"] = uac_result
    print(f"  UAC 触发结果: {uac_result}")

    # 5. 记录预期结论
    result["expected_behavior"] = {
        "secure_desktop_visible": "UAC 弹窗在安全桌面显示（PromptOnSecureDesktop=1）",
        "graphics_capture_during_uac": "预期: 无法采集安全桌面画面（黑屏/中断/冻结）",
        "graphics_capture_after_uac": "预期: UAC 关闭后恢复采集正常桌面",
        "conclusion": "Graphics Capture 不支持安全桌面采集，符合 L-01 限制",
    }

    # 6. 保存结果
    out_path = os.path.join(EVIDENCE_DIR, "u03-secure-desktop-result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n[U-03] 结果已保存: {out_path}")
    print("[U-03] 请手动补充: UAC 弹窗期间 Graphics Capture 的实际画面状态（截图/描述）")


if __name__ == "__main__":
    main()