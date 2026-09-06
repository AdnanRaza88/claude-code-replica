# AgentForge Phase 4 — remaining host steps

Linux can pack and test reports. Exit is only true on a Windows host after `/ui` opens and Accept + Signoff + Closeout run.

## Copy-paste

```
gh workflow run windows-setup.yml --repo AdnanRaza88/claude-code-replica
```

Wait for the Action. Download `AgentForge-Setup-*.exe` or the portable zip.

On Windows:

```
Start-AgentForge.bat
```

Confirm `http://127.0.0.1:8787/ui/` opens, then:

```
Accept-AgentForge.bat
Signoff-AgentForge.bat
Closeout-AgentForge.bat
```

`Closeout` prints `exit_met true` only on that Windows machine.

## Packet

`python desktop/launch_engine.py --remain` writes `.agentforge/logs/remain.json` and `remain.txt`.

GET `/desktop/remain` returns the same card.

`python desktop/launch_engine.py --host-block` writes `.agentforge/logs/host_block.json` and `host_block.txt` with structured blockers (`host`, `stamp`, `closeout`).

GET `/desktop/host-block` returns the same card.

`python desktop/launch_engine.py --host-next` writes `.agentforge/logs/host_next.json` and `host_next.txt` with the single next command and the first blocker as `why`.

GET `/desktop/host-next` returns the same card.

`python desktop/launch_engine.py --host-copy` writes `.agentforge/logs/host_copy.json`, `host_copy.txt`, and a one-line `host_copy.cmd` with only the next host command.

GET `/desktop/host-copy` returns the same card.

`python desktop/launch_engine.py --host-brief` writes the three remaining Windows steps.

GET `/desktop/host-brief` returns the same card.

`python desktop/launch_engine.py --host-line` prints only the next host command on stdout (pipe-ready) and writes `.agentforge/logs/host_line.txt`.

GET `/desktop/host-line` returns the same card.
