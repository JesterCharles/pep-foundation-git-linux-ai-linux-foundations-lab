# Linux Foundations — Code lab

A service won't start. Work through the on-call evidence with the Linux shell: find the real errors, fix a file permission, set an environment variable and fix a port mismatch.

- **Edit:** one bash script per task in `src/` (`task1_checklist.sh` ... `task5_port.sh`). Each script has `TODO` comments for its task.
- **Run the tests:** **Run Tests** in Exa Studio, or `pip install -r requirements.txt` then `python -m pytest -q`. All 5 visible tests fail at first; every message starts with `Task N:`.
- **Needs Linux (or WSL) with bash and git.** The tests run your scripts on a fresh temp copy of the scenario. `python -m test.sandbox` makes a practice copy to try commands in first.
- **Done** when every visible test passes. **Submit** also runs held-out tests you can't see.

Full task steps and hints: [`.evolv/instructions.md`](.evolv/instructions.md)
