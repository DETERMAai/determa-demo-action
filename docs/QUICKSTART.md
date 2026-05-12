# DETERMA Quickstart

## Create Virtual Environment

```bash
python -m venv .venv
```

---

## Activate

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Execute Governed Runtime Demo

```bash
python demo/governed_execution_demo.py
```

---

## Execute Runtime Replay

```bash
python -m runtime.replay
```

---

## Execute Runtime Recovery

```bash
python -m runtime.recovery_runtime
```

---

## Execute Runtime CLI

```bash
python -m runtime.cli replay
python -m runtime.cli recover
python -m runtime.cli verify
python -m runtime.cli lineage
```

---

## Execute Full Runtime Proof Suite

```bash
python -m pytest runtime/tests -v
```
