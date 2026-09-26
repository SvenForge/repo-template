"""Use generated starters as templates and extend their module manifests."""

import subprocess
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]

from ..support import TemplateCase, copier_starter_files


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(TemplateCase(answers={'features': '[copier]'}, expected=copier_starter_files()), id='default-module'),
        pytest.param(
            TemplateCase(answers={'features': '[copier]', 'copier_module_name': 'example'}, expected=copier_starter_files('example')),
            id='named-module',
        ),
        pytest.param(TemplateCase(answers={'features': '[copier]', 'copier_module_name': ''}, expected=copier_starter_files('')), id='no-module'),
    ],
)
def test_starter(tmp_path: Path, template_source: Path, case: TemplateCase) -> None:
    starter = tmp_path / 'starter'
    command = ['copier', 'copy', '--defaults', '--quiet', str(template_source), str(starter)]
    for name, value in case.answers.items():
        command.extend(('--data', f'{name}={value}'))
    subprocess.run(command, check=True)

    files = {path.relative_to(starter).as_posix() for path in starter.rglob('*') if path.is_file()}
    assert files == set(case.expected)
    for path, anchors in case.expected.items():
        for anchor in anchors:
            assert anchor in (starter / path).read_text()

    module_name = case.answers.get('copier_module_name', 'custom')
    outer_answers = yaml.safe_load((starter / '.copier-answers.yml').read_text())
    assert outer_answers['copier_module_name'] == module_name

    for selection in ('default', 'empty'):
        destination = tmp_path / selection
        command = ['copier', 'copy', '--defaults', '--quiet', str(starter), str(destination)]
        if selection == 'empty':
            command.extend(('--data', 'features=[]'))
        subprocess.run(command, check=True)
        assert {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()} == {'.copier-answers.yml'}
        answers = yaml.safe_load((destination / '.copier-answers.yml').read_text())
        assert answers.get('features', []) == ([module_name] if module_name and selection == 'default' else [])
        assert 'module_paths' not in answers

    if not module_name:
        return

    # A valid feature choice must also have a registered module path.
    invalid = subprocess.run(
        ['copier', 'copy', '--defaults', '--quiet', '--data', 'module_paths={}', str(starter), str(tmp_path / 'invalid')],
        check=False,
        capture_output=True,
        text=True,
    )
    assert invalid.returncode != 0
    assert f'Path to template module "{module_name}" not found.' in invalid.stderr

    # Extend the generated module in the temporary source, exercising both manifests.
    module = starter / 'modules' / module_name
    config = module / 'copier.yml'
    source = config.read_text().replace('    enabled: true', '    enabled: true\n    message: Hello')
    source = source.replace('    files: []', """    files:
      {% if vars.enabled %}
      - path: greeting.txt
        template: files/greeting.txt.jinja
      {% endif %}""")
    source = source.replace('    contributions: []', """    contributions:
      {% if vars.enabled %}
      - target: greeting
        template: fragments/greeting.jinja
      {% endif %}""")
    config.write_text(source)
    (module / 'files').mkdir()
    (module / 'fragments').mkdir()
    (module / 'files/greeting.txt.jinja').write_text(
        '{{ ' + module_name + '.vars.message }}'
        '{% for contribution in contributions if contribution.target == "greeting" %}'
        '{% include contribution.template %}{% endfor %}',
    )
    (module / 'fragments/greeting.jinja').write_text(' from the module')

    destination = tmp_path / 'extended'
    subprocess.run(['copier', 'copy', '--defaults', '--quiet', str(starter), str(destination)], check=True)
    assert (destination / 'greeting.txt').read_text().strip() == 'Hello from the module'
