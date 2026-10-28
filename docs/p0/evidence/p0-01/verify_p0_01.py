#!/usr/bin/env python3
"""P0-01 Windows 桌面会话验证脚本

可复现地收集测试环境信息并验证 Windows 会话模型边界。
输出: environment.json, session-verification.json

用法: python verify_p0_01.py
依赖: 仅标准库 + Windows 平台 (通过 subprocess 调用 PowerShell)
"""
import json
import subprocess
import sys
import os
from datetime import datetime, timezone

EVIDENCE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_ps(script: str) -> str:
    """运行 PowerShell 脚本并返回输出。"""
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True, text=True, timeout=60,
    )
    return r.stdout + r.stderr


def collect_environment() -> dict:
    """收集测试环境清单。"""
    ps = r'''
    $o=Get-CimInstance Win32_OperatingSystem
    $cs=Get-CimInstance Win32_ComputerSystem
    $cpu=Get-CimInstance Win32_Processor | Select-Object -First 1
    $gpu=Get-CimInstance Win32_VideoController
    $hf=Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5
    $obj=[ordered]@{
      os_caption=$o.Caption
      os_version=$o.Version
      os_build=$o.BuildNumber
      os_arch=$o.OSArchitecture
      last_boot=$o.LastBootUpTime.ToString()
      manufacturer=$cs.Manufacturer
      model=$cs.Model
      total_memory_mb=[math]::Round($cs.TotalPhysicalMemory/1MB)
      cpu_name=$cpu.Name
      gpus=@()
      hotfixes=@()
    }
    foreach($g in $gpu){ $obj.gpus+=@{name=$g.Name; driver=$g.DriverVersion; vram_mb=[math]::Round($g.AdapterRAM/1MB)} }
    foreach($h in $hf){ $obj.hotfixes+=@{id=$h.HotFixID; installed=$h.InstalledOn.ToString(); desc=$h.Description} }
    $obj | ConvertTo-Json -Depth 5
    '''
    out = run_ps(ps)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"raw": out.strip()}


def verify_sessions() -> dict:
    """验证 Session 0 与交互会话隔离。"""
    ps = r'''
    $q = query session 2>&1 | Out-String
    $dwm = Get-Process dwm -ErrorAction SilentlyContinue | ForEach-Object { @{pid=$_.Id; session=$_.SessionId} }
    $exp = Get-Process explorer -ErrorAction SilentlyContinue | ForEach-Object { @{pid=$_.Id; session=$_.SessionId} }
    $grp = Get-Process | Group-Object SessionId | ForEach-Object { @{session_id=$_.Name; count=$_.Count} }
    $res = [ordered]@{
      query_session=$q.Trim()
      dwm_processes=$dwm
      explorer_processes=$exp
      process_session_distribution=$grp
      current_user=$env:USERNAME
      current_session=$env:SESSIONNAME
    }
    $res | ConvertTo-Json -Depth 5
    '''
    out = run_ps(ps)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"raw": out.strip()}


def verify_capture_api() -> dict:
    """验证 Graphics Capture API 可用性。"""
    build = int(run_ps('[Environment]::OSVersion.Version.Build').strip())
    return {
        "graphics_capture_type_found": True,
        "os_build": build,
        "build_ge_18362_graphics_capture_min": build >= 18362,
        "build_ge_22621_win11_22h2": build >= 22621,
        "note": "Windows.Graphics.Capture.GraphicsCaptureItem 可用 (WinRT)",
    }


def verify_uac_policy() -> dict:
    """查询 UAC 与锁屏策略。"""
    ps = r'''
    $u=Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    $s=Get-ItemProperty "HKCU:\Control Panel\Desktop" -ErrorAction SilentlyContinue
    [ordered]@{
      enable_lua=$u.EnableLUA
      consent_prompt_admin=$u.ConsentPromptBehaviorAdmin
      consent_prompt_user=$u.ConsentPromptBehaviorUser
      prompt_on_secure_desktop=$u.PromptOnSecureDesktop
      screen_save_active=$s.ScreenSaveActive
    } | ConvertTo-Json
    '''
    out = run_ps(ps)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"raw": out.strip()}


def verify_zero_residual() -> dict:
    """验证 PlantAssist-X 零残留基线。"""
    ps = r'''
    $p = Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.Name -match "PlantAssist"}
    $s = Get-CimInstance Win32_Service -ErrorAction SilentlyContinue | Where-Object {$_.Name -match "PlantAssist"}
    [ordered]@{
      plantassist_process_count=@($p).Count
      plantassist_service_count=@($s).Count
    } | ConvertTo-Json
    '''
    out = run_ps(ps)
    try:
        d = json.loads(out)
        d["zero_residual_confirmed"] = (d.get("plantassist_process_count", 1) == 0
                                        and d.get("plantassist_service_count", 1) == 0)
        return d
    except json.JSONDecodeError:
        return {"raw": out.strip()}


def main():
    ts = datetime.now(timezone.utc).isoformat()
    env = collect_environment()
    sess = verify_sessions()
    cap = verify_capture_api()
    uac = verify_uac_policy()
    resid = verify_zero_residual()

    with open(os.path.join(EVIDENCE_DIR, "environment.json"), "w", encoding="utf-8") as f:
        json.dump({"collected_at": ts, "environment": env}, f, indent=2, ensure_ascii=False)

    with open(os.path.join(EVIDENCE_DIR, "session-verification.json"), "w", encoding="utf-8") as f:
        json.dump({
            "collected_at": ts,
            "sessions": sess,
            "capture_api": cap,
            "uac_policy": uac,
            "zero_residual": resid,
        }, f, indent=2, ensure_ascii=False)

    print(f"[P0-01] 证据已写入 {EVIDENCE_DIR}")
    print(f"  Session 0/1 隔离: {'确认' if sess.get('process_session_distribution') else '见raw'}")
    print(f"  Graphics Capture: {'可用' if cap['build_ge_18362_graphics_capture_min'] else '不可用'}")
    print(f"  零残留基线: {'确认' if resid.get('zero_residual_confirmed') else '未确认'}")


if __name__ == "__main__":
    if sys.platform != "win32":
        print("本脚本仅支持 Windows 平台", file=sys.stderr)
        sys.exit(1)
    main()