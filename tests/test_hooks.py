"""Unit tests for the plugin hook scripts.

Pipes realistic Claude Code hook payloads (JSON on stdin) into each hook script
and checks the exit code and output. Runs every case under each available awk
(awk, gawk, mawk, busybox awk) and each available /bin/sh-like shell (sh, dash,
bash), because users' machines differ.

Run from anywhere:  python3 tests/test_hooks.py   (stdlib only)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---- config ----
REPO = Path(__file__).resolve().parent.parent
SAFETY = REPO / "plugins" / "field-guide-safety" / "scripts"
RULES = REPO / "plugins" / "field-guide-house-rules"
AWKS = ["awk", "gawk", "mawk", "busybox"]   # whichever exist get tested
SHELLS = ["sh", "dash", "bash"]
VERBOSE = False
# ----------------

FAILS = []
COUNT = 0


def payload(event, tool=None, tool_input=None, **extra):
    d = {
        "session_id": extra.pop("session_id", "11111111-2222-3333-4444-555555555555"),
        "transcript_path": "/tmp/x/transcript.jsonl",
        "cwd": extra.pop("cwd", "/tmp"),
        "permission_mode": "default",
        "hook_event_name": event,
    }
    if tool:
        d["tool_name"] = tool
        d["tool_input"] = tool_input or {}
        d["tool_use_id"] = "toolu_01ABC"
    d.update(extra)
    # Claude Code serializes compactly and leaves non-ASCII unescaped.
    return json.dumps(d, separators=(",", ":"), ensure_ascii=False)


def bash_payload(cmd):
    return payload("PreToolUse", "Bash", {"command": cmd, "description": "Remove stuff with rm -rf (description must be ignored)"})


def run(shell, script, stdin, env_extra=None, awk_dir=None, cwd=None):
    env = dict(os.environ)
    for k in list(env):
        if k.startswith("FIELD_GUIDE_") or k.startswith("CLAUDE_"):
            del env[k]
    if awk_dir:
        env["PATH"] = f"{awk_dir}:{env['PATH']}"
    if env_extra:
        env.update(env_extra)
    p = subprocess.run([shell, str(script)], input=stdin.encode("utf-8") if isinstance(stdin, str) else stdin,
                       capture_output=True, env=env, cwd=cwd, timeout=30)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def read_gi(repo):
    gi = repo / ".gitignore"
    return gi.read_text() if gi.exists() else ""


def check(name, cond, detail=""):
    global COUNT
    COUNT += 1
    if not cond:
        FAILS.append(f"{name} {detail}")
        print(f"  FAIL {name} {detail}")
    elif VERBOSE:
        print(f"  ok   {name}")


BLOCK_RM = [
    "rm foo",
    "rm -rf build/",
    "/bin/rm x",
    "\\rm x",
    '"rm" x',
    "'r'm x",
    "sudo rm -rf /tmp/x",
    "sudo -u bob rm x",
    "sudo -- rm x",
    "env FOO=1 rm x",
    "env -i PATH=/bin rm x",
    "FOO=1 BAR=2 rm x",
    "cd /tmp && rm x",
    "ls || rm x",
    "echo hi; rm x",
    "(rm x)",
    "echo $(rm x)",
    'echo "$(rm x)"',
    "echo `rm x`",
    'echo "`rm x`"',
    "xargs rm < list.txt",
    "ls | xargs -0 rm",
    "ls | xargs -I {} rm {}",
    "ls | xargs -n 1 rm -f",
    "find . -name '*.pyc' -exec rm {} +",
    "find . -exec rm -f {} \\;",
    "find . -exec /bin/rm {} +",
    "find . -exec sh -c 'rm \"$0\"' {} \\;",
    "bash -c 'rm -rf x'",
    'sh -c "cd /tmp && rm y"',
    "bash -lc 'rm x'",
    "sudo bash -c 'rm x'",
    "ls | xargs sh -c 'rm \"$@\"' _",
    'eval "rm x"',
    "eval rm x",
    "if [ -f x ]; then rm x; fi",
    'for f in *.tmp; do rm "$f"; done',
    "while true; do rm x; break; done",
    "unlink file",
    "shred -u secret.txt",
    "timeout 10 rm x",
    "timeout -s KILL 5s rm x",
    "nohup rm x &",
    "command rm x",
    "time rm x",
    "nice -n 10 rm x",
    "echo a\nrm b",
    "echo a\r\nrm b",
    "bash <<'EOF'\nrm -rf x\nEOF",
    "sudo sh <<EOF\nrm -rf x\nEOF",
    "rm x # trailing comment",
    "rm \\\n  -rf x",
    "{ rm x; }",
    "! rm x",
    "true && rm -rf ~/scratch",
    "x=$(ls); rm $x",
    "cat <<'EOF' > notes.txt\nhello\nEOF\nrm notes.txt",
]

BLOCK_FIND = [
    "find . -name '*.log' -delete",
    "find /tmp -type f -mtime +7 -delete",
    "cd build && find . -delete",
]

BLOCK_GIT = [
    "git clean -fd",
    "git clean -fdx",
    "git -C repo clean -f",
    "git clean -f -x",
    "git --no-pager clean -ffd",
    "cd repo && git clean -fdX",
]

ALLOW = [
    "ls -la",
    "echo rm",
    'echo "rm -rf /"',
    "echo 'rm -rf /'",
    'grep -rn "rm -rf" .',
    "git rm file.txt",
    "git rm -r --cached big/",
    'git commit -m "fix: remove x; rm y"',
    "git commit -m \"$(cat <<'EOF'\nrm old stuff\n1) more (stuff\nEOF\n)\"",
    "cat > script.sh <<'EOF'\nrm -rf build\nEOF",
    "cat > script.sh <<-EOF\n\trm -rf build\n\tEOF",
    "trash foo",
    "trash -r some_dir/",
    "rmdir emptydir",
    "docker rm container",
    "npm run rm",
    "command -v rm",
    "which rm",
    "type rm",
    "git clean -n",
    "git clean -nd",
    "git clean --dry-run -d",
    "git clean -fn",
    "find . -name '*.log'",
    "find . -exec ls {} \\;",
    "echo 'a; rm b'",
    "printf '%s\\n' \"rm is a command\"",
    "x=$((1<<2)); echo $x",
    "# rm x",
    "echo hi >rm",
    "ls rm-old-files/",
    "./rm-cache.sh",
    "python3 -c \"import os; print('rm')\"",
    "ssh host 'ls'",
    "bash script.sh",
    "sh ./rm-helper.sh",
    "echo $((3 << 1)) && ls",
    "gh pr create --body \"$(cat <<'EOF'\n## Summary\n- rm the old flag; rename\nEOF\n)\"",
    "",
]


def test_rm_guard(shell, awk_dir, label):
    script = SAFETY / "rm-guard.sh"
    for cmd in BLOCK_RM + BLOCK_FIND + BLOCK_GIT:
        code, out, err = run(shell, script, bash_payload(cmd), awk_dir=awk_dir)
        check(f"[{label}] block {cmd!r}", code == 2 and "Blocked by the field-guide-safety plugin" in err, f"-> exit {code} {err[:120]!r}")
    for cmd in BLOCK_FIND:
        code, out, err = run(shell, script, bash_payload(cmd), awk_dir=awk_dir)
        check(f"[{label}] find message {cmd!r}", "find ... -delete" in err)
    for cmd in BLOCK_GIT:
        code, out, err = run(shell, script, bash_payload(cmd), awk_dir=awk_dir)
        check(f"[{label}] git message {cmd!r}", "git clean" in err)
    for cmd in ALLOW:
        code, out, err = run(shell, script, bash_payload(cmd), awk_dir=awk_dir)
        check(f"[{label}] allow {cmd!r}", code == 0 and err == "", f"-> exit {code} {err[:120]!r}")
    # fail open
    for name, stdin in [("empty", ""), ("garbage", "{not json"), ("binary", b"\xff\xfe\x00\x01"),
                        ("non-bash tool", payload("PreToolUse", "Write", {"file_path": "/tmp/a", "content": "rm -rf /"})),
                        ("no command", payload("PreToolUse", "Bash", {"description": "x"}))]:
        code, out, err = run(shell, script, stdin, awk_dir=awk_dir)
        check(f"[{label}] fail-open {name}", code == 0, f"-> exit {code}")
    # opt-out
    for val in ["off", "OFF", "0", "false", "no"]:
        code, out, err = run(shell, script, bash_payload("rm x"), env_extra={"FIELD_GUIDE_RM_GUARD": val}, awk_dir=awk_dir)
        check(f"[{label}] opt-out {val}", code == 0)
    # unicode in command does not break parsing
    code, out, err = run(shell, script, bash_payload("echo “café” \u2014 ok; rm x"), awk_dir=awk_dir)
    check(f"[{label}] unicode then rm", code == 2)
    code, out, err = run(shell, script, bash_payload("echo “café” \u2014 ok"), awk_dir=awk_dir)
    check(f"[{label}] unicode allow", code == 0)


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def make_big(path, mb):
    with open(path, "wb") as f:
        f.truncate(mb * 1024 * 1024 + 1)


def test_gitignore(shell, awk_dir, label):
    script = SAFETY / "gitignore-big-files.sh"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td).resolve()
        data = td / "plugin-data"
        env = {"CLAUDE_PLUGIN_DATA": str(data)}
        repo = td / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "t@example.com")
        git(repo, "config", "user.name", "t")
        (repo / "small.txt").write_text("hi")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "init")
        sid = "abc-123"

        # A big file that existed before the session must not be swept.
        make_big(repo / "old_big.bin", 51)

        # SessionStart: creates the marker, prints nothing.
        code, out, err = run(shell, script, payload("SessionStart", session_id=sid, source="startup", cwd=str(repo)), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] SessionStart silent", code == 0 and out == "", f"{code} {out!r} {err!r}")
        check(f"[{label}] marker created", (data / "sessions" / sid).exists())
        os.utime(repo / "old_big.bin", (1_000_000_000, 1_000_000_000))

        # PostToolUse on a small file: nothing.
        code, out, err = run(shell, script, payload("PostToolUse", "Write", {"file_path": str(repo / "small.txt"), "content": "hi"}, session_id=sid), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] small file ignored", code == 0 and out == "")

        # PostToolUse on a big untracked file in a subdir with a space: gitignored.
        (repo / "data dir").mkdir()
        big = repo / "data dir" / "big file.csv"
        make_big(big, 51)
        code, out, err = run(shell, script, payload("PostToolUse", "Write", {"file_path": str(big), "content": "x"}, session_id=sid), env_extra=env, awk_dir=awk_dir)
        gi = read_gi(repo)
        check(f"[{label}] big file gitignored", "/data dir/big file.csv" in gi, f"gi={gi!r} out={out!r} err={err!r}")
        try:
            j = json.loads(out)
            ok = "big file.csv" in j.get("systemMessage", "") and "additionalContext" in j.get("hookSpecificOutput", {})
        except Exception:
            ok = False
        check(f"[{label}] PostToolUse JSON valid", ok, repr(out))
        st = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True).stdout
        check(f"[{label}] git no longer sees big file", "big file.csv" not in st, st)

        # Same file again: no duplicate entry.
        run(shell, script, payload("PostToolUse", "Write", {"file_path": str(big), "content": "x"}, session_id=sid), env_extra=env, awk_dir=awk_dir)
        gi2 = read_gi(repo)
        check(f"[{label}] no duplicate", gi2.count("/data dir/big file.csv") == 1, gi2)

        # Tracked big file: left alone.
        tracked = repo / "tracked_big.bin"
        make_big(tracked, 51)
        git(repo, "add", "tracked_big.bin")
        git(repo, "commit", "-qm", "big")
        run(shell, script, payload("PostToolUse", "Write", {"file_path": str(tracked), "content": "x"}, session_id=sid), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] tracked left alone", "tracked_big.bin" not in read_gi(repo))

        # LFS-managed path: left alone.
        (repo / ".gitattributes").write_text("*.psd filter=lfs diff=lfs merge=lfs -text\n")
        lfs = repo / "art.psd"
        make_big(lfs, 51)
        run(shell, script, payload("PostToolUse", "Write", {"file_path": str(lfs), "content": "x"}, session_id=sid), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] LFS left alone", "art.psd" not in read_gi(repo))

        # Special characters in a name are escaped in the pattern.
        weird = repo / ("a[1].bin" if os.name == "nt" else "a[1]*.bin")   # Windows forbids * in names
        make_big(weird, 51)
        run(shell, script, payload("PostToolUse", "Write", {"file_path": str(weird), "content": "x"}, session_id=sid), env_extra=env, awk_dir=awk_dir)
        st = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True).stdout
        check(f"[{label}] glob chars escaped and effective", "a[1]" not in st, st + read_gi(repo))

        # Stop sweep: a big file made through Bash during the session is caught; the pre-session one is not.
        (repo / "downloads").mkdir()
        made = repo / "downloads" / "dump.parquet"
        make_big(made, 60)
        code, out, err = run(shell, script, payload("Stop", session_id=sid, cwd=str(repo / "downloads"), stop_hook_active=False), env_extra=env, awk_dir=awk_dir)
        gi3 = read_gi(repo)
        check(f"[{label}] Stop sweep catches new big file", "/downloads/dump.parquet" in gi3, f"{gi3!r} {out!r} {err!r}")
        check(f"[{label}] Stop sweep skips pre-session file", "old_big.bin" not in gi3, gi3)
        try:
            ok = "dump.parquet" in json.loads(out)["systemMessage"]
        except Exception:
            ok = False
        check(f"[{label}] Stop JSON valid", ok, repr(out))

        # Threshold env var.
        mid = repo / "mid.bin"
        make_big(mid, 30)
        run(shell, script, payload("PostToolUse", "Write", {"file_path": str(mid), "content": "x"}, session_id=sid), env_extra={**env, "FIELD_GUIDE_BIG_FILE_MB": "20"}, awk_dir=awk_dir)
        check(f"[{label}] custom threshold", "/mid.bin" in read_gi(repo))

        # Opt-out.
        off = repo / "off.bin"
        make_big(off, 51)
        run(shell, script, payload("PostToolUse", "Write", {"file_path": str(off), "content": "x"}, session_id=sid), env_extra={**env, "FIELD_GUIDE_GITIGNORE_BIG": "off"}, awk_dir=awk_dir)
        check(f"[{label}] opt-out", "/off.bin" not in read_gi(repo))

        # Outside any git repo: nothing written anywhere.
        outside = td / "loose"
        outside.mkdir()
        make_big(outside / "big.bin", 51)
        code, out, err = run(shell, script, payload("PostToolUse", "Write", {"file_path": str(outside / "big.bin"), "content": "x"}, session_id=sid), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] no repo -> nothing", code == 0 and out == "" and not (outside / ".gitignore").exists())

        # Stop without a marker (session started before install): nothing.
        code, out, err = run(shell, script, payload("Stop", session_id="no-marker", cwd=str(repo)), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] Stop without marker", code == 0 and out == "")

        # Fail open on junk.
        for name, stdin in [("empty", ""), ("garbage", "{oops"), ("binary", b"\xff\x00")]:
            code, out, err = run(shell, script, stdin, env_extra=env, awk_dir=awk_dir)
            check(f"[{label}] fail-open {name}", code == 0 and out == "")


def test_house_rules(shell, awk_dir, label):
    inject = RULES / "scripts" / "inject-rules.sh"
    emdash = RULES / "scripts" / "em-dash-check.sh"
    if not inject.exists():
        return
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cfg = td / "cfg"
        cfg.mkdir()
        env = {"CLAUDE_CONFIG_DIR": str(cfg), "CLAUDE_PLUGIN_ROOT": str(RULES)}
        code, out, err = run(shell, inject, payload("SessionStart", source="startup"), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] rules injected", code == 0 and "field-guide-house-rules" in out and "em dash" in out.lower() and len(out) < 10000, f"{code} len={len(out)} {err!r}")
        custom = cfg / "field-guide-house-rules.md"
        custom.write_text("- Always answer in haiku.\n")
        code, out, err = run(shell, inject, payload("SessionStart", source="startup"), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] custom rules used", "Always answer in haiku." in out and "Lead with the answer" not in out, out[:300])
        custom.write_text("x" * 20000)
        code, out, err = run(shell, inject, payload("SessionStart", source="startup"), env_extra=env, awk_dir=awk_dir)
        check(f"[{label}] oversize rules truncated", code == 0 and len(out) < 10000 and "truncated" in out, f"len={len(out)}")
        custom.write_text("- Always answer in haiku.\n")
        code, out, err = run(shell, inject, payload("SessionStart", source="startup"), env_extra={**env, "FIELD_GUIDE_HOUSE_RULES": "off"}, awk_dir=awk_dir)
        check(f"[{label}] rules opt-out", code == 0 and out == "")
        custom.unlink()

        md = td / "notes.md"
        def em(tool, ti):
            return run(shell, emdash, payload("PostToolUse", tool, ti), env_extra=env, awk_dir=awk_dir)
        code, out, err = em("Write", {"file_path": str(md), "content": "One \u2014 two \u2014 three"})
        try:
            j = json.loads(out)
            ok = "2 em dash" in j["hookSpecificOutput"]["additionalContext"]
        except Exception:
            ok = False
        check(f"[{label}] em dash flagged on Write", code == 0 and ok, f"{out!r} {err!r}")
        code, out, err = em("Write", {"file_path": str(md), "content": "No dashes here - just hyphens."})
        check(f"[{label}] clean Write silent", code == 0 and out == "")
        code, out, err = em("Edit", {"file_path": str(md), "old_string": "a \u2014 b", "new_string": "a, b"})
        check(f"[{label}] Edit removing em dash silent", code == 0 and out == "")
        code, out, err = em("Edit", {"file_path": str(md), "old_string": "a, b", "new_string": "a \u2014 b"})
        check(f"[{label}] Edit adding em dash flagged", code == 0 and "1 em dash" in out)
        code, out, err = em("Write", {"file_path": str(td / "code.py"), "content": "x = 1  # \u2014"})
        check(f"[{label}] code files ignored", code == 0 and out == "")
        code, out, err = em("Write", {"file_path": str(md), "content": "One \\u2014 escaped"})
        check(f"[{label}] literal backslash-u text not counted", code == 0 and out == "", out)
        custom.write_text("- Always answer in haiku.\n")
        code, out, err = em("Write", {"file_path": str(md), "content": "One \u2014 two"})
        check(f"[{label}] no em-dash rule -> silent", code == 0 and out == "")
        custom.unlink()
        code, out, err = run(shell, emdash, payload("PostToolUse", "Write", {"file_path": str(md), "content": "a \u2014 b"}), env_extra={**env, "FIELD_GUIDE_EM_DASH_CHECK": "off"}, awk_dir=awk_dir)
        check(f"[{label}] em-dash opt-out", code == 0 and out == "")
        for name, stdin in [("empty", ""), ("garbage", "{oops")]:
            code, out, err = run(shell, emdash, stdin, env_extra=env, awk_dir=awk_dir)
            check(f"[{label}] em-dash fail-open {name}", code == 0 and out == "")


def main():
    awk_dirs = []
    tmp = Path(tempfile.mkdtemp(prefix="fg-awk-"))
    for a in ([] if os.name == "nt" else AWKS):   # Windows (Git Bash): just the default awk
        exe = shutil.which(a)
        if not exe:
            continue
        d = tmp / a
        d.mkdir()
        if a == "busybox":
            (d / "awk").write_text(f'#!/bin/sh\nexec "{exe}" awk "$@"\n')
            (d / "awk").chmod(0o755)
        else:
            (d / "awk").symlink_to(exe)
        awk_dirs.append((a, str(d)))
    if not awk_dirs:
        awk_dirs.append(("awk", None))
    # Run each shell by the full path that PATH lookup finds. A bare "bash" on
    # Windows makes CreateProcess search System32 first, which finds the WSL
    # launcher instead of Git Bash, so skip anything that resolves there.
    shells = []
    for s in SHELLS:
        exe = shutil.which(s)
        if exe and not (os.name == "nt" and "\\system32\\" in exe.lower()):
            shells.append((s, exe))
    print(f"awks: {[a for a, _ in awk_dirs]}  shells: {[f'{s} ({e})' for s, e in shells]}")
    for a, d in awk_dirs:
        for sh, exe in shells:
            label = f"{sh}+{a}"
            print(f"== {label}")
            test_rm_guard(exe, d, label)
            test_gitignore(exe, d, label)
            test_house_rules(exe, d, label)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{COUNT - len(FAILS)}/{COUNT} checks passed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
