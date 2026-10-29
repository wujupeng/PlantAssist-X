"""U-01 Win10 22H2 兼容性验证 — 在 192.168.2.12 上完整收集证据。"""
import winrm
import json
import sys
import subprocess
import os

TARGET = "192.168.2.12"
USER = "dell"
PWD = "1111"
LOCAL_PS = r"C:\Users\DELL\IDEProjects\PlantAssist-X\.codeartsdoer\tmp_collect_info.ps1"
REMOTE_PS = r"C:\plantassist_u01_test\collect_info.ps1"

def main():
    # 1. SMB 连接 + 复制脚本
    smb_unc = rf"\\{TARGET}\C$"
    print(f"[U-01-Win10] 建立 SMB 连接 {smb_unc} ...")
    subprocess.run(["net", "use", smb_unc, "/del", "/y"], capture_output=True)
    subprocess.run(["net", "use", smb_unc, f"/user:{USER}", PWD], capture_output=True)

    smb_path = os.path.join(smb_unc, "plantassist_u01_test")
    print(f"[U-01-Win10] 复制收集脚本 ...")
    ps_copy = f'New-Item -ItemType Directory -Path "{smb_path}" -Force | Out-Null; Copy-Item "{LOCAL_PS}" "{smb_path}\\collect_info.ps1" -Force'
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps_copy], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[U-01-Win10] SMB 复制失败: {r.stderr}")
        sys.exit(1)
    print("[U-01-Win10] 脚本已复制")

    # 2. pywinrm 执行
    print("[U-01-Win10] 通过 WinRM 执行收集脚本...")
    sess = winrm.Session(TARGET, auth=(USER, PWD), transport="ntlm")
    r = sess.run_ps(f"Set-ExecutionPolicy Bypass -Scope Process -Force; & '{REMOTE_PS}'")
    if r.status_code != 0:
        err = r.std_err.decode('utf-8', errors='replace')
        print(f"[U-01-Win10] 执行失败 (status={r.status_code}):")
        print(err[:3000])
        sys.exit(1)

    out = r.std_out.decode('utf-8', errors='replace').strip()
    print(f"[U-01-Win10] 收集完成, 输出长度={len(out)}")

    # 解析 JSON
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        idx = out.find('{')
        if idx >= 0:
            data = json.loads(out[idx:])
        else:
            print(f"[U-01-Win10] JSON 解析失败, 前500字符:\n{out[:500]}")
            sys.exit(1)

    # 保存结果
    outPath = os.path.join(os.path.dirname(__file__), "u01-win10-22h2-result.json")
    with open(outPath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[U-01-Win10] 结果已保存: {outPath}")

    # 打印关键信息
    os_info = data.get("os", {})
    iso = data.get("session_isolation", {})
    cap = data.get("graphics_capture", {})
    zr = data.get("zero_residual", {})
    uac = data.get("uac", {})
    comp = data.get("computer", {})
    print(f"\n=== U-01 Win10 22H2 关键结果 ===")
    print(f"机器名: {data.get('machine')}")
    print(f"OS: {os_info.get('caption')} | Build {os_info.get('build')} | {os_info.get('arch')}")
    print(f"硬件: {comp.get('manufacturer')} {comp.get('model')} | {comp.get('memory_mb')}MB")
    print(f"GPU: {data.get('gpus')}")
    print(f"Graphics Capture: type_found={cap.get('type_found')} | build_ge_18362={cap.get('build_ge_18362')}")
    print(f"Session 隔离: S0={iso.get('session0_process_count')}进程 S1={iso.get('session1_process_count')}进程 | 确认={iso.get('isolation_confirmed')}")
    print(f"UAC: {uac}")
    print(f"零残留: {zr.get('confirmed')}")

    build = int(os_info.get('build', 0))
    is_win10_22h2 = (build == 19045)
    print(f"\n=== U-01 判定 ===")
    print(f"Build {build} == 19045 (Win10 22H2): {is_win10_22h2}")


if __name__ == "__main__":
    main()