import hashlib
import json
from datetime import datetime
from pathlib import Path


def generate_manifest_file(manifest_file_path: Path, print_file_path: Path, pack_code, supplier, row_count):
    manifest = create_manifest(print_file_path, pack_code, supplier, row_count)
    manifest_file_path.write_text(json.dumps(manifest))


def create_manifest(print_file_path: Path, pack_code, supplier, row_count) -> dict:
    return {
        'packCode': pack_code,
        'supplier': supplier,
        'manifestCreated': datetime.utcnow().isoformat(timespec='milliseconds') + 'Z',
        'sourceName': 'ONS_RM',
        'files': [
            {
                'name': print_file_path.name,
                'relativePath': './',
                'sizeBytes': str(print_file_path.stat().st_size),
                'md5sum': hashlib.md5(print_file_path.read_text().encode()).hexdigest(),
                'rows': row_count
            }
        ]
    }
