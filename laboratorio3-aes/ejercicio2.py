import json
import sys
from datetime import datetime, timezone
from benchmarks.benchmark_aes import run_tests
from benchmarks.support import ROOT, source_hash, machine_info


def main():
    result, log = run_tests()
    folder = ROOT/'results'/'validacion'
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'pruebas.txt').write_text(log,encoding='utf-8')
    evidence = {'created_utc':datetime.now(timezone.utc).isoformat(),
                'source_sha256':source_hash(),'machine':machine_info(),**result}
    (folder/'pruebas.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
    print(log)
    print('Evidencia:',folder)
    if not result['passed']:
        sys.exit(1)


if __name__ == '__main__':
    main()
