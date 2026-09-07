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

`python desktop/launch_engine.py --host-go` prints `GO <version>: <command>` for the next host action.
