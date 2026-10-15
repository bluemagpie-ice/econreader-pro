"""Build portable text and a modular skill archive using Python standard library."""
from pathlib import Path
import re
import zipfile

root = Path(__file__).resolve().parents[1]
output = root / 'submission'
output.mkdir(exist_ok=True)
files = [root / 'SKILL.md', *sorted((root / 'references').glob('*.md')), root / 'agents/openai.yaml']
for file in files:
    text = file.read_text(encoding='utf-8-sig')
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not (file.parent / target).exists():
            raise SystemExit(f'Broken reference: {file.name}: {target}')
with zipfile.ZipFile(output / 'econreader-pro-modular.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file, 'econreader-pro/' + file.relative_to(root).as_posix())
modules = ['classification', 'evidence-rules', 'output-formats', 'empirical-workflow',
           'method-checks', 'theoretical-workflow', 'institutional-workflow',
           'review-workflow', 'methodology-workflow', 'multi-paper', 'research-ideas']
entry = (root / 'SKILL.md').read_text(encoding='utf-8-sig')
entry = entry.split('## 校准材料与平台')[0]
entry = re.sub(r'\[([^\]]+)\]\(references/[^)]+\)', r'「\1」（见下文对应模块）', entry)
parts = [entry, '\n本单文件版将规则内联；不依赖本地参考文件或特定工具。平台无法读取PDF时，请用户提供可读文本。\n']
for name in modules:
    parts.append((root / 'references' / f'{name}.md').read_text(encoding='utf-8-sig'))
(output / 'econreader-pro-single-file.md').write_text('\n\n---\n\n'.join(parts), encoding='utf-8')
with zipfile.ZipFile(output / 'econreader-pro-modular.zip') as archive:
    assert archive.testzip() is None
    assert 'econreader-pro/SKILL.md' in archive.namelist()
print('Built modular archive and standalone Markdown; local links and ZIP integrity checked.')
