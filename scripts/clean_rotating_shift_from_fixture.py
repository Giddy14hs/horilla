import json
import sys
from pathlib import Path


def clean_fixture(path: Path) -> int:
	with path.open("r", encoding="utf-8") as f:
		data = json.load(f)
	before = len(data)
	dropped = {"base.rotatingshift", "base.rotatingshiftassign"}
	cleaned = [obj for obj in data if obj.get("model") not in dropped]
	with path.open("w", encoding="utf-8") as f:
		json.dump(cleaned, f, indent=2, ensure_ascii=False)
	return before - len(cleaned)


def main():
	infile = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("load_data/base_data.json")
	removed = clean_fixture(infile)
	print(f"Removed {removed} RotatingShift-related entries from {infile}")


if __name__ == "__main__":
	main()







