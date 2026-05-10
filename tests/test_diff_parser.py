from src.determa_replay.diff_parser import parse_unified_diff, parsed_changes_to_dicts


def test_parse_modified_file():
    diff = """diff --git a/app/service.py b/app/service.py
index 1111111..2222222 100644
--- a/app/service.py
+++ b/app/service.py
@@ -1,3 +1,3 @@
-old_value = 10
+old_value = 100
 keep = True
"""

    changes = parse_unified_diff(diff)

    assert len(changes) == 1
    assert changes[0].path == "app/service.py"
    assert changes[0].old_path == "app/service.py"
    assert changes[0].status == "modified"
    assert changes[0].additions == 1
    assert changes[0].deletions == 1


def test_parse_added_file():
    diff = """diff --git a/docs/new.md b/docs/new.md
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/docs/new.md
@@ -0,0 +1,2 @@
+# Title
+Body
"""

    changes = parse_unified_diff(diff)

    assert len(changes) == 1
    assert changes[0].path == "docs/new.md"
    assert changes[0].status == "added"
    assert changes[0].additions == 2
    assert changes[0].deletions == 0


def test_parse_deleted_file():
    diff = """diff --git a/old.txt b/old.txt
deleted file mode 100644
index 1111111..0000000
--- a/old.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-old
-content
"""

    changes = parse_unified_diff(diff)

    assert len(changes) == 1
    assert changes[0].path == "old.txt"
    assert changes[0].status == "deleted"
    assert changes[0].additions == 0
    assert changes[0].deletions == 2


def test_parse_renamed_file():
    diff = """diff --git a/old_name.py b/new_name.py
similarity index 88%
rename from old_name.py
rename to new_name.py
index 1111111..2222222 100644
--- a/old_name.py
+++ b/new_name.py
@@ -1 +1 @@
-print('old')
+print('new')
"""

    changes = parse_unified_diff(diff)

    assert len(changes) == 1
    assert changes[0].old_path == "old_name.py"
    assert changes[0].path == "new_name.py"
    assert changes[0].status == "renamed"
    assert changes[0].additions == 1
    assert changes[0].deletions == 1


def test_parse_multiple_files_preserves_order():
    diff = """diff --git a/a.txt b/a.txt
index 1111111..2222222 100644
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-a
+A
diff --git a/b.txt b/b.txt
index 3333333..4444444 100644
--- a/b.txt
+++ b/b.txt
@@ -1 +1 @@
-b
+B
"""

    changes = parse_unified_diff(diff)

    assert [change.path for change in changes] == ["a.txt", "b.txt"]


def test_output_is_deterministic():
    diff = """diff --git a/app.py b/app.py
index 1111111..2222222 100644
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-x = 1
+x = 2
"""

    first = parsed_changes_to_dicts(parse_unified_diff(diff))
    second = parsed_changes_to_dicts(parse_unified_diff(diff))

    assert first == second
